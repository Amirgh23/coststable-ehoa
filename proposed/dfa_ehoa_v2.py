"""DFA-EHOA V2 candidate: calibrated dual-memory consensus veto."""
from __future__ import annotations
import numpy as np
from .dfa_ehoa import DFAEHOA
from .consensus_veto import CalibrationTrust, consensus_veto


class DFAEHOAV2(DFAEHOA):
    """Conservative V2 that falls back to baseline under evidence conflict.

    Resampling memory and elite-history memory must agree before reliability or
    relevance/redundancy guidance can affect the binary transition. Guidance is
    event-driven and its confidence is calibrated from observed search success.
    The inherited EHOA fitness is unchanged.
    """
    def __init__(self,*args,consensus_margin=.15,collapse_threshold=.18,**kwargs):
        kwargs.setdefault('transition_mode','dual')
        kwargs.setdefault('stability_strategy','event')
        kwargs.setdefault('warmup',1)
        super().__init__(*args,**kwargs)
        self.consensus_margin=float(consensus_margin)
        self.collapse_threshold=float(collapse_threshold)
        self.calibration_=CalibrationTrust()

    def fit(self,X,y):
        self.calibration_=CalibrationTrust()
        return super().fit(X,y)

    def _fuse_transition_evidence(self,q,reliability,elite_masks):
        if q is None or len(elite_masks)<2:
            return np.zeros_like(reliability),np.zeros_like(reliability)
        elite_q=np.asarray(elite_masks,bool).mean(axis=0)
        direction,confidence,agreement=consensus_veto(q,elite_q,margin=self.consensus_margin,trust=self.calibration_.value)
        self.last_consensus_fraction_=float(agreement.mean())
        return direction,confidence

    def _guidance_active(self,detector,diversity,iteration):
        # No permanent pressure: only measured collapse or stagnation opens gate.
        return iteration>self.warmup and (detector.counter>0 or diversity<self.collapse_threshold)

    def _filter_interaction(self,signal,direction,confidence,active):
        if not active: return np.zeros_like(signal)
        signal=np.asarray(signal,float)
        aligned=(np.sign(signal)==np.sign(direction))&(confidence>0)
        return np.where(aligned,signal*confidence,0.)

    def _after_guided_iteration(self,active,improved):
        if active: self.calibration_.update(improved)
