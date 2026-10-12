"""Agreement-gated evidence fusion for DFA-EHOA V2.

The gate is deliberately neutral under disagreement: neither evidence source
is allowed to overrule the other.  This is search-dynamics evidence only and
never changes the wrapper fitness.
"""
from __future__ import annotations
import numpy as np


def entropy_confidence(q):
    q=np.clip(np.asarray(q,float),0,1)
    safe=np.clip(q,1e-12,1-1e-12)
    h=-(safe*np.log2(safe)+(1-safe)*np.log2(1-safe))
    return np.clip(1-h,0,1)


def consensus_veto(resample_q, elite_q, *, margin=.10, trust=1.0):
    """Return direction, confidence and agreement mask for two memories.

    Directional pressure exists only when both independent memories are at
    least ``margin`` from ambiguity and have the same sign.  Otherwise the
    exact neutral value zero is returned, enabling baseline fallback.
    """
    a=2*np.asarray(resample_q,float)-1
    b=2*np.asarray(elite_q,float)-1
    if a.shape != b.shape: raise ValueError('memory vectors must have equal shape')
    agreement=(np.abs(a)>=margin)&(np.abs(b)>=margin)&(np.sign(a)==np.sign(b))
    direction=np.where(agreement,.5*(a+b),0.)
    confidence=np.where(agreement,np.minimum(entropy_confidence(resample_q),entropy_confidence(elite_q)),0.)
    confidence*=float(np.clip(trust,0,1))
    return np.clip(direction,-1,1),np.clip(confidence,0,1),agreement


class CalibrationTrust:
    """Beta-Bernoulli trust in whether gated proposals improve search."""
    def __init__(self, success=1., failure=1.): self.success=float(success); self.failure=float(failure)
    @property
    def value(self): return self.success/(self.success+self.failure)
    def update(self, improved):
        if improved: self.success+=1
        else: self.failure+=1
        return self.value
