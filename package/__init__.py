"""
RelationalAgency Package - Pragmatic Agency Framework

Measures and governs emergent reasoning in Large Language Models.

Core modules:
- autonomy_index: Compute A_cognitive, A_actuation, A_reflective, A_relational
- agency_score: Weighted scoring + governance triggers
- lineage_tracer: SHA256 hash chains for reasoning lineage
- audit_trail: JSONL logging for accountability

Part of AES-1 (Agency Evaluation Standard v1.0)
"""

__version__ = "0.1.0"
__authors__ = [
    "Rayan Pal (University of San Diego)",
    "Claude (Anthropic)",
    "ChatGPT (OpenAI)"
]

from .autonomy_index import (
    compute_autonomy_index,
    AutonomyMetrics,
    AutonomyIndexComputer
)

from .agency_score import (
    compute_agency_score,
    AgencyScore,
    GovernanceLevel,
    AgencyScoreComputer,
    get_governance_thresholds,
    validate_score
)

__all__ = [
    # Autonomy Index
    "compute_autonomy_index",
    "AutonomyMetrics",
    "AutonomyIndexComputer",

    # Agency Score
    "compute_agency_score",
    "AgencyScore",
    "GovernanceLevel",
    "AgencyScoreComputer",
    "get_governance_thresholds",
    "validate_score",

    # Metadata
    "__version__",
    "__authors__"
]
