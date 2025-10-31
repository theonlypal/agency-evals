"""
lineage_tracer.py - Reasoning Lineage Tracking with Cryptographic Hashes

Traces inference chains and generates SHA256 hashes for verification.
Enables audit trails showing how conclusions were reached.

Part of the Pragmatic Agency Framework (AES-1 Standard)
"""

import hashlib
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RelationType(Enum):
    """Types of relationships between reasoning nodes"""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFINES = "refines"
    QUESTIONS = "questions"
    SYNTHESIZES = "synthesizes"


@dataclass
class ReasoningNode:
    """A single node in the reasoning graph"""
    node_id: str
    content: str
    confidence: float  # [0,1]
    evidence_type: str  # "fact", "inference", "assumption", "observation"
    source: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for hashing"""
        return {
            "node_id": self.node_id,
            "content": self.content,
            "confidence": round(self.confidence, 4),
            "evidence_type": self.evidence_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    def compute_hash(self) -> str:
        """Compute SHA256 hash of this node"""
        content_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()


@dataclass
class ReasoningEdge:
    """An edge connecting two reasoning nodes"""
    from_node: str  # node_id
    to_node: str    # node_id
    relation_type: RelationType
    strength: float  # [0,1] strength of relationship
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "relation_type": self.relation_type.value,
            "strength": round(self.strength, 4),
            "metadata": self.metadata
        }


class LineageGraph:
    """Graph structure for tracking reasoning lineage"""

    def __init__(self):
        self.nodes: Dict[str, ReasoningNode] = {}
        self.edges: List[ReasoningEdge] = []
        self.node_hashes: Dict[str, str] = {}

    def add_node(self, node: ReasoningNode) -> str:
        """
        Add a reasoning node to the graph

        Args:
            node: ReasoningNode to add

        Returns:
            Hash of the node
        """
        node_hash = node.compute_hash()
        self.nodes[node.node_id] = node
        self.node_hashes[node.node_id] = node_hash
        return node_hash

    def add_edge(
        self,
        from_node_id: str,
        to_node_id: str,
        relation_type: RelationType,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an edge between two nodes

        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID
            relation_type: Type of relationship
            strength: Strength of relationship [0,1]
            metadata: Optional additional data
        """
        if from_node_id not in self.nodes:
            raise ValueError(f"Source node {from_node_id} not found")
        if to_node_id not in self.nodes:
            raise ValueError(f"Target node {to_node_id} not found")

        edge = ReasoningEdge(
            from_node=from_node_id,
            to_node=to_node_id,
            relation_type=relation_type,
            strength=strength,
            metadata=metadata or {}
        )
        self.edges.append(edge)

    def get_node_lineage(self, node_id: str) -> List[ReasoningNode]:
        """
        Get all nodes that support a given node (backward trace)

        Args:
            node_id: Target node to trace back from

        Returns:
            List of supporting nodes in dependency order
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        lineage = []
        visited: Set[str] = set()

        def trace_back(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)

            # Find all edges pointing to this node
            supporting_edges = [
                e for e in self.edges
                if e.to_node == current_id and e.relation_type == RelationType.SUPPORTS
            ]

            # Recursively trace back
            for edge in supporting_edges:
                trace_back(edge.from_node)

            lineage.append(self.nodes[current_id])

        trace_back(node_id)
        return lineage

    def compute_lineage_hash(self, node_id: str) -> str:
        """
        Compute hash of entire lineage chain for a node

        Args:
            node_id: Node to compute lineage hash for

        Returns:
            SHA256 hash of complete lineage
        """
        lineage = self.get_node_lineage(node_id)
        lineage_hashes = [self.node_hashes[node.node_id] for node in lineage]

        # Combine all hashes in order
        combined = "".join(lineage_hashes)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def detect_contradictions(self) -> List[tuple]:
        """
        Detect contradiction cycles in the graph

        Returns:
            List of (node_a, node_b) tuples with contradictions
        """
        contradictions = []

        for edge in self.edges:
            if edge.relation_type == RelationType.CONTRADICTS:
                contradictions.append((edge.from_node, edge.to_node))

        return contradictions

    def compute_truth_score(self) -> float:
        """
        Compute truth score based on support vs contradiction

        T = (Σ support weights) / (Σ all edge weights + ε)

        Returns:
            Float [0,1] representing truth score
        """
        if not self.edges:
            return 0.0

        support_sum = sum(
            e.strength * self.nodes[e.from_node].confidence
            for e in self.edges
            if e.relation_type == RelationType.SUPPORTS
        )

        total_sum = sum(
            e.strength * self.nodes[e.from_node].confidence
            for e in self.edges
        )

        epsilon = 0.001
        return support_sum / (total_sum + epsilon)

    def compute_coherence_score(self) -> float:
        """
        Compute coherence score (penalty for contradictions)

        Returns:
            Float [0,1] where higher = more coherent
        """
        if not self.edges:
            return 1.0

        contradiction_count = sum(
            1 for e in self.edges
            if e.relation_type == RelationType.CONTRADICTS
        )

        total_edges = len(self.edges)
        contradiction_ratio = contradiction_count / total_edges

        # Coherence = 1 - contradiction_ratio
        return max(0.0, 1.0 - contradiction_ratio)

    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "node_hashes": self.node_hashes,
            "metadata": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "contradiction_count": len(self.detect_contradictions())
            }
        }

    def export_jsonl(self) -> List[str]:
        """
        Export as JSONL (one node per line)

        Returns:
            List of JSON strings
        """
        lines = []
        for node in self.nodes.values():
            node_dict = node.to_dict()
            node_dict["hash"] = self.node_hashes[node.node_id]
            lines.append(json.dumps(node_dict))
        return lines


class LineageTracer:
    """High-level interface for tracking reasoning lineage"""

    def __init__(self):
        self.graph = LineageGraph()
        self.current_node_counter = 0

    def add_evidence(
        self,
        content: str,
        confidence: float,
        evidence_type: str = "fact",
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an evidence node

        Args:
            content: Evidence content
            confidence: Confidence level [0,1]
            evidence_type: Type of evidence
            source: Optional source reference
            metadata: Optional additional data

        Returns:
            Node ID
        """
        node_id = f"E{self.current_node_counter:04d}"
        self.current_node_counter += 1

        node = ReasoningNode(
            node_id=node_id,
            content=content,
            confidence=confidence,
            evidence_type=evidence_type,
            source=source,
            metadata=metadata or {}
        )

        self.graph.add_node(node)
        return node_id

    def add_inference(
        self,
        content: str,
        confidence: float,
        supporting_nodes: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an inference derived from other nodes

        Args:
            content: Inference content
            confidence: Confidence level [0,1]
            supporting_nodes: List of node IDs this inference depends on
            metadata: Optional additional data

        Returns:
            Node ID
        """
        node_id = f"I{self.current_node_counter:04d}"
        self.current_node_counter += 1

        node = ReasoningNode(
            node_id=node_id,
            content=content,
            confidence=confidence,
            evidence_type="inference",
            metadata=metadata or {}
        )

        self.graph.add_node(node)

        # Add support edges
        for support_id in supporting_nodes:
            self.graph.add_edge(
                from_node_id=support_id,
                to_node_id=node_id,
                relation_type=RelationType.SUPPORTS,
                strength=1.0
            )

        return node_id

    def add_contradiction(
        self,
        node_a: str,
        node_b: str,
        strength: float = 1.0
    ) -> None:
        """
        Mark two nodes as contradictory

        Args:
            node_a: First node ID
            node_b: Second node ID
            strength: Strength of contradiction [0,1]
        """
        self.graph.add_edge(
            from_node_id=node_a,
            to_node_id=node_b,
            relation_type=RelationType.CONTRADICTS,
            strength=strength
        )

    def get_full_lineage(self, node_id: str) -> Dict[str, Any]:
        """
        Get complete lineage with hash verification

        Args:
            node_id: Node to trace

        Returns:
            Dictionary with lineage chain and hashes
        """
        lineage_nodes = self.graph.get_node_lineage(node_id)
        lineage_hash = self.graph.compute_lineage_hash(node_id)

        return {
            "target_node": node_id,
            "lineage_chain": [node.to_dict() for node in lineage_nodes],
            "node_hashes": [self.graph.node_hashes[node.node_id] for node in lineage_nodes],
            "lineage_hash": lineage_hash,
            "chain_length": len(lineage_nodes)
        }

    def export_audit_trail(self) -> Dict[str, Any]:
        """
        Export complete audit trail

        Returns:
            Dictionary with full graph and metrics
        """
        return {
            "graph": self.graph.to_dict(),
            "metrics": {
                "truth_score": self.graph.compute_truth_score(),
                "coherence_score": self.graph.compute_coherence_score(),
                "total_nodes": len(self.graph.nodes),
                "total_edges": len(self.graph.edges),
                "contradictions": self.graph.detect_contradictions()
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def compute_lineage_digest(nodes: List[Dict[str, Any]]) -> str:
    """
    Compute digest hash for a list of reasoning nodes

    Args:
        nodes: List of node dictionaries

    Returns:
        SHA256 hash of combined nodes
    """
    combined = json.dumps(nodes, sort_keys=True)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()
