"""DFA-EHOA components, kept separate from the baseline implementation."""

from .dfa_ehoa import DFAEHOA
from .consensus_veto import CalibrationTrust, consensus_veto, entropy_confidence
from .dfa_ehoa_v2 import DFAEHOAV2
from .cost_stable_ehoa import CostStableEHOA, repair_to_budget, resampled_lcb_utility

# SFIG-EHOA is the descriptive name used in the manuscript; DFA-EHOA is kept
# as the stable API/configuration name for backward compatibility.
SFIGEHOA = DFAEHOA

__all__ = ["DFAEHOA", "SFIGEHOA"]
