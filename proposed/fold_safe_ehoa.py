import time
import numpy as np
from sklearn.feature_selection import mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import ehoa
from ehoa import EHOA
from utils import PreparedFold, _resample_training
from proposed.cost_stable_ehoa import repair_to_budget


class FoldSafeEHOA(EHOA):
    def __init__(self,*args,costs,budget,strategy='stable_lcb',evidence_resamples=4,lcb_z=1.,groups=None,discrete_features=False,**kwargs):
        super().__init__(*args,**kwargs)
        self.costs=np.asarray(costs,float)
        self.budget=float(budget)
        self.strategy=strategy
        self.evidence_resamples=evidence_resamples
        self.lcb_z=lcb_z
        self.groups=groups
        self.discrete_features=discrete_features

    def _utility(self,X,y,seed):
        rng=np.random.default_rng(seed+7919)
        if self.strategy=='EHOA':return np.ones(X.shape[1])
        if self.strategy=='cheapest':return np.ones(X.shape[1])
        if self.strategy=='random':return rng.random(X.shape[1])
        if self.strategy=='mi':return mutual_info_classif(X,y,discrete_features=self.discrete_features,random_state=seed)
        scores=[]
        for _ in range(self.evidence_resamples):
            parts=[]
            for label in np.unique(y):
                pool=np.flatnonzero(y==label)
                parts.append(rng.choice(pool,max(2,int(np.ceil(.8*len(pool)))),replace=True))
            idx=np.concatenate(parts)
            scores.append(mutual_info_classif(X[idx],y[idx],discrete_features=self.discrete_features,random_state=int(rng.integers(0,2**31-1))))
        a=np.asarray(scores)
        return np.maximum(0,a.mean(0)-self.lcb_z*a.std(0,ddof=1))

    def _repair(self,mask,utility):
        return np.asarray(mask,bool) if self.strategy=='EHOA' else repair_to_budget(mask,self.costs,self.budget,utility)

    def _prepare(self,X,y,n_folds,random_state,apply_smote):
        cv=StratifiedKFold(n_folds,shuffle=True,random_state=random_state) if self.groups is None else StratifiedGroupKFold(n_folds,shuffle=True,random_state=random_state)
        splits=cv.split(X,y) if self.groups is None else cv.split(X,y,self.groups)
        folds=[]
        self.inner_utilities=[]
        self.inner_indices=[]
        self.split_audit=[]
        for j,(tr,va) in enumerate(splits):
            imp=SimpleImputer(strategy='mean')
            utility_X=imp.fit_transform(X[tr])
            self.inner_utilities.append(self._utility(utility_X,y[tr],random_state+j+1))
            folds.append(PreparedFold(X[tr],y[tr],X[va],y[va]))
            self.inner_indices.append((tr,va))
            overlap=0 if self.groups is None else len(set(self.groups[tr])&set(self.groups[va]))
            if overlap:raise ValueError('Inner subject overlap')
            self.split_audit.append(dict(inner_fold=j+1,training_rows=len(tr),validation_rows=len(va),utility_validation_row_overlap=len(set(tr)&set(va)),subject_overlap=overlap))
        return folds

    def fit(self,X,y):
        started=time.perf_counter()
        X=np.asarray(X,float)
        y=np.asarray(y,int)
        self.utility_=self._utility(SimpleImputer(strategy='mean').fit_transform(X),y,self.random_state)
        self.candidate_audit=[]
        original=ehoa.prepare_cv_folds
        ehoa.prepare_cv_folds=self._prepare
        try:result=super().fit(X,y)
        finally:ehoa.prepare_cv_folds=original
        self.fit_total_seconds_=time.perf_counter()-started
        self.runtime_seconds_=self.fit_total_seconds_
        return result

    def _evaluate(self,mask):
        key=np.packbits(mask.astype(np.uint8)).tobytes()+len(mask).to_bytes(4,'little')
        if key not in self._fitness_cache:
            scores=[]
            sizes=[]
            for j,(fold,utility) in enumerate(zip(self._folds,self.inner_utilities)):
                selected=np.flatnonzero(self._repair(mask,utility))
                imp=SimpleImputer(strategy='mean')
                sc=StandardScaler()
                xt=sc.fit_transform(imp.fit_transform(fold.X_train[:,selected]))
                xv=sc.transform(imp.transform(fold.X_valid[:,selected]))
                yt=fold.y_train
                if self.apply_smote:xt,yt=_resample_training(xt,yt,self.random_state+j)
                model=KNeighborsClassifier(n_neighbors=min(5,len(yt)),metric='euclidean')
                model.fit(xt,yt)
                scores.append(accuracy_score(fold.y_valid,model.predict(xv)))
                sizes.append(len(selected))
                self.candidate_audit.append(dict(inner_fold=j+1,selected_features=len(selected),smote_input_features=xt.shape[1],selected_cost=float(self.costs[selected].sum())))
            acc=float(np.mean(scores))
            fitness=self.alpha*(1-acc)+(1-self.alpha)*float(np.mean(sizes))/len(mask)
            self._fitness_cache[key]=(fitness,acc,int(round(np.mean(sizes))))
            self.evaluations_+=1
        return self._fitness_cache[key]

    def _consider_global(self,position,mask,fitness,accuracy):
        return super()._consider_global(position,self._repair(mask,self.utility_),fitness,accuracy)
