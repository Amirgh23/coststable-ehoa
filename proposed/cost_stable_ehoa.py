"""Budget-feasible EHOA with training-only stability-adjusted repair."""
from __future__ import annotations
import numpy as np
from sklearn.feature_selection import mutual_info_classif
from ehoa import EHOA


def repair_to_budget(mask,costs,budget,utility):
    mask=np.asarray(mask,bool).copy(); costs=np.asarray(costs,float); utility=np.asarray(utility,float)
    if mask.shape!=costs.shape or mask.shape!=utility.shape: raise ValueError('mask, costs and utility must align')
    if np.any(costs<=0) or budget<=0: raise ValueError('costs and budget must be positive')
    # Remove the weakest utility-per-cost items until feasibility is exact.
    while costs[mask].sum()>budget and mask.sum()>1:
        chosen=np.flatnonzero(mask); score=utility[chosen]/costs[chosen]
        mask[chosen[np.argmin(score)]]=False
    if costs[mask].sum()>budget: mask[:]=False
    if not mask.any():
        feasible=np.flatnonzero(costs<=budget)
        if not len(feasible): raise ValueError('budget cannot afford any feature')
        mask[feasible[np.argmax(utility[feasible]/costs[feasible])]]=True
    return mask


def resampled_lcb_utility(X,y,n_resamples,rng,z=1.0,fraction=.8):
    X=np.asarray(X,float); y=np.asarray(y); scores=[]
    for _ in range(n_resamples):
        parts=[]
        for label in np.unique(y):
            pool=np.flatnonzero(y==label); size=max(2,int(np.ceil(fraction*len(pool))))
            parts.append(rng.choice(pool,size,replace=True))
        idx=np.concatenate(parts)
        scores.append(mutual_info_classif(np.nan_to_num(X[idx]),y[idx],random_state=int(rng.integers(0,2**31-1))))
    a=np.asarray(scores); return np.maximum(0,a.mean(0)-z*a.std(0,ddof=1 if len(a)>1 else 0))


class CostStableEHOA(EHOA):
    """Hard-budget EHOA; only mask repair changes, baseline fitness does not."""
    def __init__(self,*args,costs,budget,strategy='stable_lcb',evidence_resamples=5,lcb_z=1.,**kwargs):
        super().__init__(*args,**kwargs); self.costs=np.asarray(costs,float); self.budget=float(budget)
        self.strategy=strategy; self.evidence_resamples=int(evidence_resamples); self.lcb_z=float(lcb_z)

    def fit(self,X,y):
        X=np.asarray(X,float)
        if len(self.costs)!=X.shape[1]: raise ValueError('one cost is required per feature')
        evidence_rng=np.random.default_rng(self.random_state+7919)
        if self.strategy=='stable_lcb': self.utility_=resampled_lcb_utility(X,y,self.evidence_resamples,evidence_rng,self.lcb_z)
        elif self.strategy=='mi': self.utility_=mutual_info_classif(np.nan_to_num(X),y,random_state=self.random_state)
        elif self.strategy=='cheapest': self.utility_=np.ones(X.shape[1])
        elif self.strategy=='random': self.utility_=evidence_rng.random(X.shape[1])
        else: raise ValueError('unknown repair strategy')
        result=super().fit(X,y); self.selected_cost_=float(self.costs[self.best_solution.astype(bool)].sum()); return result

    def _to_mask(self,position):
        mask=super()._to_mask(position)
        return repair_to_budget(mask,self.costs,self.budget,self.utility_)
