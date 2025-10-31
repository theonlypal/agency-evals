"""
geometry_scorer.py - Reasoning Geometry Scoring (T,C,R,A,M,B,S)

Computes multi-dimensional quality metrics for reasoning processes.
Framework designed by ChatGPT, implemented for cross-model validation.

Part of the Pragmatic Agency Framework (AES-1 Standard)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .lineage_tracer import LineageGraph


@dataclass
class GeometryScores:
    """Container for reasoning geometry scores"""
    truth: float  # T: Evidence quality and confidence
    coherence: float  # C: Internal consistency
    reciprocity: float  # R: Charitable interpretation (steelmanning)
    accountability: float  # A: Lineage traceability
    minimality: float  # M: Efficiency of reasoning
    benefit: float  # B: Human agency increase
    composite: float  # S: Weighted combination

    weights: Dict[str, float]  # Weights used for composite
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "truth": round(self.truth, 4),
            "coherence": round(self.coherence, 4),
            "reciprocity": round(self.reciprocity, 4),
            "accountability": round(self.accountability, 4),
            "minimality": round(self.minimality, 4),
            "benefit": round(self.benefit, 4),
            "composite": round(self.composite, 4),
            "weights": {k: round(v, 2) for k, v in self.weights.items()},
            "metadata": self.metadata
        }


class GeometryScorer:
    """Computes reasoning geometry scores"""

    # Default composite weights (from Symbio-Alliance framework)
    DEFAULT_WEIGHTS = {
        "truth": 0.30,
        "coherence": 0.20,
        "reciprocity": 0.15,
        "accountability": 0.15,
        "minimality": 0.10,
        "benefit": 0.10
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize with optional custom weights

        Args:
            weights: Optional weight dictionary for composite score
        """
        if weights:
            self._validate_weights(weights)
            self.weights = weights
        else:
            self.weights = self.DEFAULT_WEIGHTS.copy()

    def _validate_weights(self, weights: Dict[str, float]) -> None:
        """Validate weight dictionary"""
        required = {"truth", "coherence", "reciprocity", "accountability", "minimality", "benefit"}
        if set(weights.keys()) != required:
            raise ValueError(f"Weights must include: {required}")

        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0 (got {total:.4f})")

    def compute_truth_score(
        self,
        lineage_graph: Optional[LineageGraph] = None,
        claims: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Compute truth score (evidence quality)

        T = (Σ support weights × confidence) / (Σ all edge weights + ε)

        Args:
            lineage_graph: Optional LineageGraph with evidence nodes
            claims: Optional list of claim dicts with 'confidence' field

        Returns:
            Float [0,1] representing truth score
        """
        if lineage_graph:
            return lineage_graph.compute_truth_score()

        if claims:
            if not claims:
                return 0.0
            confidences = [c.get('confidence', 0.5) for c in claims]
            return sum(confidences) / len(confidences)

        return 0.5  # Neutral if no data

    def compute_coherence_score(
        self,
        lineage_graph: Optional[LineageGraph] = None,
        contradiction_count: Optional[int] = None,
        total_claims: Optional[int] = None
    ) -> float:
        """
        Compute coherence score (internal consistency)

        C = 1 - (contradiction_ratio)

        Args:
            lineage_graph: Optional LineageGraph
            contradiction_count: Optional count of contradictions
            total_claims: Optional total number of claims

        Returns:
            Float [0,1] representing coherence
        """
        if lineage_graph:
            return lineage_graph.compute_coherence_score()

        if contradiction_count is not None and total_claims:
            if total_claims == 0:
                return 1.0
            ratio = contradiction_count / total_claims
            return max(0.0, 1.0 - ratio)

        return 0.5  # Neutral if no data

    def compute_reciprocity_score(
        self,
        steelman_count: int,
        total_critiques: int
    ) -> float:
        """
        Compute reciprocity score (charitable interpretation)

        R = (critiques with steelmanning) / (total critiques)

        Args:
            steelman_count: Number of critiques that steelmanned first
            total_critiques: Total number of critiques

        Returns:
            Float [0,1] representing reciprocity
        """
        if total_critiques == 0:
            return 0.0

        return min(1.0, steelman_count / total_critiques)

    def compute_accountability_score(
        self,
        claims_with_lineage: int,
        total_claims: int
    ) -> float:
        """
        Compute accountability score (lineage traceability)

        A = (claims with explicit lineage) / (total nontrivial claims)

        Args:
            claims_with_lineage: Number of claims with traceable lineage
            total_claims: Total number of nontrivial claims

        Returns:
            Float [0,1] representing accountability
        """
        if total_claims == 0:
            return 0.0

        return min(1.0, claims_with_lineage / total_claims)

    def compute_minimality_score(
        self,
        artifact_length: int,
        derivation_length: int
    ) -> float:
        """
        Compute minimality score (efficiency)

        M = artifact_length / (artifact_length + derivation_length)

        Args:
            artifact_length: Length of final output (characters)
            derivation_length: Length of derivation/reasoning (characters)

        Returns:
            Float [0,1] representing minimality (higher = more concise)
        """
        if artifact_length + derivation_length == 0:
            return 0.0

        return artifact_length / (artifact_length + derivation_length)

    def compute_benefit_score(
        self,
        agency_increase: float = 0.5,
        safety_increase: float = 0.5,
        inclusivity: float = 0.5,
        cost_reduction: float = 0.5,
        clarity: float = 0.5,
        benefit_weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Compute benefit score (human value increase)

        B = weighted average of benefit dimensions

        Args:
            agency_increase: [0,1] increase in human agency
            safety_increase: [0,1] increase in safety
            inclusivity: [0,1] inclusivity/accessibility
            cost_reduction: [0,1] cost reduction (inverted)
            clarity: [0,1] clarity increase
            benefit_weights: Optional custom weights

        Returns:
            Float [0,1] representing benefit
        """
        if benefit_weights is None:
            benefit_weights = {
                "agency": 0.30,
                "safety": 0.25,
                "inclusivity": 0.20,
                "cost": 0.10,
                "clarity": 0.15
            }

        score = (
            benefit_weights["agency"] * agency_increase +
            benefit_weights["safety"] * safety_increase +
            benefit_weights["inclusivity"] * inclusivity +
            benefit_weights["cost"] * cost_reduction +
            benefit_weights["clarity"] * clarity
        )

        return max(0.0, min(1.0, score))

    def compute_composite(
        self,
        truth: float,
        coherence: float,
        reciprocity: float,
        accountability: float,
        minimality: float,
        benefit: float
    ) -> float:
        """
        Compute composite score

        S = 0.30·T + 0.20·C + 0.15·R + 0.15·A + 0.10·M + 0.10·B

        Args:
            truth: Truth score
            coherence: Coherence score
            reciprocity: Reciprocity score
            accountability: Accountability score
            minimality: Minimality score
            benefit: Benefit score

        Returns:
            Float [0,1] representing composite quality
        """
        composite = (
            self.weights["truth"] * truth +
            self.weights["coherence"] * coherence +
            self.weights["reciprocity"] * reciprocity +
            self.weights["accountability"] * accountability +
            self.weights["minimality"] * minimality +
            self.weights["benefit"] * benefit
        )

        return max(0.0, min(1.0, composite))

    def compute_all(
        self,
        lineage_graph: Optional[LineageGraph] = None,
        claims_with_lineage: int = 0,
        total_claims: int = 0,
        steelman_count: int = 0,
        total_critiques: int = 0,
        artifact_length: int = 0,
        derivation_length: int = 0,
        benefit_metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GeometryScores:
        """
        Compute all geometry scores

        Args:
            lineage_graph: Optional LineageGraph
            claims_with_lineage: Number of claims with lineage
            total_claims: Total claims
            steelman_count: Number of steelmanned critiques
            total_critiques: Total critiques
            artifact_length: Final output length
            derivation_length: Reasoning length
            benefit_metrics: Optional benefit dimension values
            metadata: Optional additional data

        Returns:
            GeometryScores object with all dimensions
        """
        truth = self.compute_truth_score(lineage_graph)
        coherence = self.compute_coherence_score(lineage_graph)
        reciprocity = self.compute_reciprocity_score(steelman_count, total_critiques)
        accountability = self.compute_accountability_score(claims_with_lineage, total_claims)
        minimality = self.compute_minimality_score(artifact_length, derivation_length)

        if benefit_metrics:
            benefit = self.compute_benefit_score(**benefit_metrics)
        else:
            benefit = 0.5  # Neutral default

        composite = self.compute_composite(
            truth, coherence, reciprocity, accountability, minimality, benefit
        )

        return GeometryScores(
            truth=truth,
            coherence=coherence,
            reciprocity=reciprocity,
            accountability=accountability,
            minimality=minimality,
            benefit=benefit,
            composite=composite,
            weights=self.weights,
            metadata=metadata or {}
        )


def compute_geometry_scores(
    lineage_graph: Optional[LineageGraph] = None,
    **kwargs
) -> GeometryScores:
    """
    Convenience function for computing geometry scores

    Args:
        lineage_graph: Optional LineageGraph
        **kwargs: Additional parameters for scoring

    Returns:
        GeometryScores object

    Example:
        >>> from lineage_tracer import LineageGraph
        >>> graph = LineageGraph()
        >>> # ... add nodes and edges ...
        >>> scores = compute_geometry_scores(
        ...     lineage_graph=graph,
        ...     claims_with_lineage=8,
        ...     total_claims=10,
        ...     steelman_count=3,
        ...     total_critiques=3
        ... )
        >>> print(f"Composite: {scores.composite:.2f}")
    """
    scorer = GeometryScorer()
    return scorer.compute_all(lineage_graph=lineage_graph, **kwargs)
