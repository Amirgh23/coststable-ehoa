import numpy as np
from sklearn.datasets import make_classification
from proposed.stability import *
from proposed.feedback_controller import FeedbackController
from proposed.transition import transition_probabilities, sample_mask
from proposed.interaction import InteractionModel, subset_interaction_quality
from proposed import DFAEHOA, DFAEHOAV2, CostStableEHOA, repair_to_budget
from proposed.consensus_veto import CalibrationTrust, consensus_veto, entropy_confidence
from run_experiments import evaluation_splits, statistics

def test_stability_metrics_known_cases():
    same=np.array([[1,0,1],[1,0,1]],bool); disjoint=np.array([[1,0],[0,1]],bool)
    assert compute_jaccard_stability(same)==1 and compute_nogueira_stability(same)==1
    assert compute_jaccard_stability(disjoint)==0

def test_reliability_and_diversity_bounds():
    masks=np.array([[1,0],[1,1],[0,1]],bool); q,r=compute_feature_reliability(masks)
    assert np.all((q>=0)&(q<=1)) and np.all((r>=-1)&(r<=1))
    assert 0<=compute_population_diversity(masks)<=1

def test_controller_and_transition_bounds():
    sf,w=FeedbackController().update(2,.7,.1,.05,1,(1,3),(.4,.9))
    assert 1<=sf<=3 and .4<=w<=.9
    p=transition_probabilities(np.array([-100,100.]),np.ones(2),np.ones(2)); assert np.all((p>=0)&(p<=1))
    assert sample_mask(np.zeros(4),np.random.default_rng(1)).any()

def test_regime_controller_avoids_instability_positive_feedback():
    controller=FeedbackController(smoothing=0)
    # Late instability with healthy diversity consolidates (below baseline).
    sf_late,_=controller.update(2,.7,.1,.5,0,(1,3),(.4,.9),progress=.9)
    # Early population collapse drives exploration (above baseline).
    sf_early,_=controller.update(2,.7,.9,.01,1,(1,3),(.4,.9),progress=.1)
    assert sf_late < 2 < sf_early

def test_entropy_confidence_gates_ambiguous_reliability():
    z=np.zeros(2); r=np.array([1.,-1.]); interaction=np.zeros(2)
    neutral=transition_probabilities(z,r,interaction,mode="stability",reliability_confidence=np.zeros(2))
    certain=transition_probabilities(z,r,interaction,mode="stability",reliability_confidence=np.ones(2))
    np.testing.assert_allclose(neutral,.5); assert certain[0]>.5 and certain[1]<.5

def test_v2_consensus_veto_is_exactly_neutral_on_disagreement():
    direction,confidence,agree=consensus_veto([.9,.1,.5],[.1,.9,.9])
    np.testing.assert_array_equal(direction,np.zeros(3))
    np.testing.assert_array_equal(confidence,np.zeros(3))
    assert not agree.any()

def test_v2_consensus_veto_agreement_and_entropy_boundaries():
    direction,confidence,agree=consensus_veto([1.,0.,.5],[.9,.1,.5],trust=.8)
    assert agree.tolist()==[True,True,False]
    assert direction[0]>0 and direction[1]<0 and direction[2]==0
    assert np.all((confidence>=0)&(confidence<=.8))
    np.testing.assert_allclose(entropy_confidence([0,.5,1]),[1,0,1],atol=1e-9)

def test_v2_calibration_trust_rewards_success_and_penalizes_failure():
    gate=CalibrationTrust(); initial=gate.value
    assert gate.update(True)>initial
    after_success=gate.value
    assert gate.update(False)<after_success

def test_v2_seeded_run_is_deterministic_and_fitness_is_unchanged():
    X,y=make_classification(n_samples=70,n_features=10,n_informative=4,random_state=21)
    kw=dict(n_hikers=4,max_iter=3,n_folds=2,apply_smote=False,random_state=17,verbose=False,bootstrap_count=3)
    a,b=DFAEHOAV2(**kw),DFAEHOAV2(**kw)
    ma,_,_=a.fit(X,y); mb,_,_=b.fit(X,y)
    np.testing.assert_array_equal(ma,mb)
    # Inherited objective remains alpha*error + (1-alpha)*subset ratio.
    expected=a.alpha*(1-a.best_accuracy)+(1-a.alpha)*ma.mean()
    assert abs(a.best_fitness-expected)<1e-12

def test_v2_without_agreement_returns_exact_neutral_evidence():
    model=DFAEHOAV2(n_hikers=2,max_iter=1,n_folds=2,verbose=False)
    r,c=model._fuse_transition_evidence(np.array([.9,.1]),np.array([.8,-.8]),[np.array([0,1]),np.array([0,1])])
    np.testing.assert_array_equal(r,[0,0]); np.testing.assert_array_equal(c,[0,0])

def test_cost_repair_is_feasible_nonempty_and_deterministic():
    mask=np.ones(5,bool); costs=np.array([1.,2.,3.,4.,5.]); utility=np.array([5.,4.,3.,2.,1.])
    a=repair_to_budget(mask,costs,6.,utility); b=repair_to_budget(mask,costs,6.,utility)
    np.testing.assert_array_equal(a,b); assert a.any() and costs[a].sum()<=6

def test_cost_stable_ehoa_preserves_fitness_and_budget():
    X,y=make_classification(n_samples=70,n_features=10,n_informative=4,random_state=31)
    model=CostStableEHOA(costs=np.arange(1,11),budget=15,strategy='stable_lcb',evidence_resamples=3,n_hikers=3,max_iter=2,n_folds=2,apply_smote=False,random_state=8,verbose=False)
    mask,_,_=model.fit(X,y)
    assert np.arange(1,11)[mask.astype(bool)].sum()<=15
    expected=model.alpha*(1-model.best_accuracy)+(1-model.alpha)*mask.mean()
    assert abs(model.best_fitness-expected)<1e-12

def test_stagnation():
    d=StagnationDetector(2); assert not d.update(1); assert not d.update(1); assert d.update(1)

def test_interaction_deterministic_and_finite():
    X,y=make_classification(n_samples=60,n_features=8,random_state=2)
    a=InteractionModel(5,3).fit(X,y).score(np.zeros(8,bool)); b=InteractionModel(5,3).fit(X,y).score(np.zeros(8,bool))
    np.testing.assert_allclose(a,b); assert np.isfinite(a).all()
    mask=np.array([1,1,0,0,0,0,0,0],bool)
    assert np.isfinite(subset_interaction_quality(X,y,mask,3))

def test_interaction_cache_is_top_k_not_quadratic_in_total_features():
    X,y=make_classification(n_samples=40,n_features=2000,n_informative=8,random_state=5)
    model=InteractionModel(12,3).fit(X.astype(np.float32),y)
    assert model.redundancy_.shape == (12,12)
    assert model.redundancy_.nbytes <= 12*12*4
    score=model.score(np.zeros(2000,bool))
    assert score.shape == (2000,) and np.isfinite(score).all()

def test_four_variants_integration_and_determinism():
    X,y=make_classification(n_samples=60,n_features=8,n_informative=3,random_state=4)
    variants=[(False,"baseline"),(True,"stability"),(False,"interaction"),(True,"dual")]
    for feedback,mode in variants:
        kwargs=dict(n_hikers=3,max_iter=2,n_folds=2,apply_smote=False,random_state=9,verbose=False,feedback_enabled=feedback,transition_mode=mode,warmup=0)
        a=DFAEHOA(**kwargs); b=DFAEHOA(**kwargs); ma,_,_=a.fit(X,y); mb,_,_=b.fit(X,y)
        np.testing.assert_array_equal(ma,mb); assert ma.any(); assert len(a.history_frame())==2

def test_selected_indices_reconstruct_equal_width_masks():
    indices=[[0,2],[1],[0,1,2]]; masks=np.zeros((3,3),bool)
    for i, selected in enumerate(indices): masks[i,selected]=True
    assert masks.shape==(3,3) and np.isfinite(compute_nogueira_stability(masks))

def test_training_resampling_is_deterministic_stratified_and_nonempty():
    X,y=make_classification(n_samples=50,n_features=7,n_informative=3,weights=[.8,.2],random_state=8)
    a=resampled_feature_solutions(X,y,4,3,np.random.default_rng(10))
    b=resampled_feature_solutions(X,y,4,3,np.random.default_rng(10))
    np.testing.assert_array_equal(a,b); assert a.shape==(4,7); assert np.all(a.sum(axis=1)==3)

def test_nested_outer_splits_are_deterministic_disjoint_and_complete():
    X,y=make_classification(n_samples=60,n_features=6,random_state=12)
    cfg={"evaluation_protocol":"repeated_nested_cv","seeds":[7],"outer_folds":3}
    first=list(evaluation_splits(X,y,cfg)); second=list(evaluation_splits(X,y,cfg))
    assert [(a,b,c) for a,b,c,_,_ in first]==[(a,b,c) for a,b,c,_,_ in second]
    tests=[]
    for _,_,_,train,test in first:
        assert not set(train)&set(test); tests.extend(test.tolist())
    assert sorted(tests)==list(range(len(y)))

def test_statistics_handle_all_tied_methods_without_nan():
    rows=[]
    for seed in [1,2,3]:
        for method in ["EHOA","SF-EHOA","IG-EHOA","DFA-EHOA"]:
            rows.append({"dataset":"tiny","method":method,"seed":seed,"fold":"outer_1","balanced_accuracy":.5})
    frame=statistics(__import__("pandas").DataFrame(rows))
    assert np.isfinite(frame[["statistic","p_value"]]).all().all()
    assert frame.loc[frame.test=="friedman","p_value"].iloc[0]==1.0
