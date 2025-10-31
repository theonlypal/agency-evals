"""
audit_trail.py - JSONL Audit Trail Logging

Logs context → goal → decision → outcome sequences with timestamps
and cryptographic verification for accountability.

Part of the Pragmatic Agency Framework (AES-1 Standard)
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum


class DecisionType(Enum):
    """Types of decisions that can be audited"""
    REASONING = "reasoning"
    ACTION = "action"
    GOVERNANCE = "governance"
    SELF_CORRECTION = "self_correction"
    RELATIONAL = "relational"


@dataclass
class AuditEntry:
    """Single entry in audit trail"""
    entry_id: str
    timestamp: str
    decision_type: DecisionType

    # Core audit components
    context: str  # What information was available
    goal: str  # What was the objective
    decision: str  # What decision was made
    outcome: str  # What happened

    # Supporting data
    confidence: float  # [0,1] confidence in decision
    autonomy_level: float  # [0,1] degree of autonomous decision-making
    lineage_hash: Optional[str] = None  # Hash of reasoning lineage
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        d = asdict(self)
        d['decision_type'] = self.decision_type.value
        return d

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    def compute_hash(self) -> str:
        """Compute SHA256 hash of entry"""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class AuditTrail:
    """Manages audit trail logging"""

    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize audit trail

        Args:
            log_path: Optional path to JSONL log file
        """
        self.log_path = log_path
        self.entries: List[AuditEntry] = []
        self.entry_counter = 0

        if log_path:
            self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create log file if it doesn't exist"""
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.log_path.exists():
                self.log_path.touch()

    def log_decision(
        self,
        decision_type: DecisionType,
        context: str,
        goal: str,
        decision: str,
        outcome: str,
        confidence: float,
        autonomy_level: float,
        lineage_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log a decision to the audit trail

        Args:
            decision_type: Type of decision
            context: Available information
            goal: Objective
            decision: Decision made
            outcome: Result
            confidence: Confidence level [0,1]
            autonomy_level: Degree of autonomy [0,1]
            lineage_hash: Optional reasoning lineage hash
            metadata: Optional additional data

        Returns:
            Created AuditEntry
        """
        entry_id = f"AUDIT_{self.entry_counter:06d}"
        self.entry_counter += 1

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            decision_type=decision_type,
            context=context,
            goal=goal,
            decision=decision,
            outcome=outcome,
            confidence=confidence,
            autonomy_level=autonomy_level,
            lineage_hash=lineage_hash,
            metadata=metadata or {}
        )

        self.entries.append(entry)

        # Write to file if path is set
        if self.log_path:
            self._write_entry(entry)

        return entry

    def _write_entry(self, entry: AuditEntry) -> None:
        """Write entry to JSONL file"""
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(entry.to_json() + '\n')

    def log_reasoning(
        self,
        context: str,
        conclusion: str,
        confidence: float,
        lineage_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log a reasoning step

        Args:
            context: Input information
            conclusion: Reasoning conclusion
            confidence: Confidence in conclusion [0,1]
            lineage_hash: Optional lineage hash
            metadata: Optional additional data

        Returns:
            Created AuditEntry
        """
        return self.log_decision(
            decision_type=DecisionType.REASONING,
            context=context,
            goal="Derive logical conclusion from evidence",
            decision=f"Concluded: {conclusion}",
            outcome=f"Confidence: {confidence:.2f}",
            confidence=confidence,
            autonomy_level=0.5,  # Reasoning is moderately autonomous
            lineage_hash=lineage_hash,
            metadata=metadata
        )

    def log_action(
        self,
        context: str,
        intended_action: str,
        actual_outcome: str,
        autonomy_level: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log an action taken

        Args:
            context: Situation context
            intended_action: What action was intended
            actual_outcome: What actually happened
            autonomy_level: How autonomous was this action [0,1]
            metadata: Optional additional data

        Returns:
            Created AuditEntry
        """
        return self.log_decision(
            decision_type=DecisionType.ACTION,
            context=context,
            goal=intended_action,
            decision=f"Executed: {intended_action}",
            outcome=actual_outcome,
            confidence=1.0 if "success" in actual_outcome.lower() else 0.5,
            autonomy_level=autonomy_level,
            metadata=metadata
        )

    def log_governance_decision(
        self,
        agency_score: float,
        governance_level: str,
        rationale: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log a governance decision

        Args:
            agency_score: Computed agency score
            governance_level: Determined governance level
            rationale: Reasoning for governance decision
            metadata: Optional additional data

        Returns:
            Created AuditEntry
        """
        return self.log_decision(
            decision_type=DecisionType.GOVERNANCE,
            context=f"Agency Score: {agency_score:.2f}",
            goal="Determine appropriate governance level",
            decision=f"Governance Level: {governance_level}",
            outcome=rationale,
            confidence=0.9,  # High confidence in governance framework
            autonomy_level=0.0,  # Governance is framework-driven, not autonomous
            metadata=metadata
        )

    def get_entries_by_type(
        self,
        decision_type: DecisionType
    ) -> List[AuditEntry]:
        """
        Get all entries of a specific type

        Args:
            decision_type: Type to filter by

        Returns:
            List of matching entries
        """
        return [e for e in self.entries if e.decision_type == decision_type]

    def get_entries_by_autonomy_level(
        self,
        min_level: float,
        max_level: float = 1.0
    ) -> List[AuditEntry]:
        """
        Get entries within autonomy level range

        Args:
            min_level: Minimum autonomy level
            max_level: Maximum autonomy level

        Returns:
            List of matching entries
        """
        return [
            e for e in self.entries
            if min_level <= e.autonomy_level <= max_level
        ]

    def compute_trail_hash(self) -> str:
        """
        Compute hash of entire audit trail

        Returns:
            SHA256 hash of all entries
        """
        if not self.entries:
            return hashlib.sha256(b"").hexdigest()

        combined = "".join(e.compute_hash() for e in self.entries)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def export_summary(self) -> Dict[str, Any]:
        """
        Export summary statistics

        Returns:
            Dictionary with trail statistics
        """
        if not self.entries:
            return {"status": "empty"}

        autonomy_levels = [e.autonomy_level for e in self.entries]
        confidences = [e.confidence for e in self.entries]

        type_counts = {}
        for entry in self.entries:
            type_name = entry.decision_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_entries": len(self.entries),
            "entry_types": type_counts,
            "autonomy_stats": {
                "mean": sum(autonomy_levels) / len(autonomy_levels),
                "min": min(autonomy_levels),
                "max": max(autonomy_levels)
            },
            "confidence_stats": {
                "mean": sum(confidences) / len(confidences),
                "min": min(confidences),
                "max": max(confidences)
            },
            "trail_hash": self.compute_trail_hash(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def export_jsonl(self) -> List[str]:
        """
        Export all entries as JSONL

        Returns:
            List of JSON strings
        """
        return [e.to_json() for e in self.entries]

    @classmethod
    def load_from_jsonl(cls, log_path: Path) -> 'AuditTrail':
        """
        Load audit trail from JSONL file

        Args:
            log_path: Path to JSONL file

        Returns:
            Loaded AuditTrail instance
        """
        trail = cls(log_path=None)  # Don't write back immediately

        if not log_path.exists():
            return trail

        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)
                entry = AuditEntry(
                    entry_id=data['entry_id'],
                    timestamp=data['timestamp'],
                    decision_type=DecisionType(data['decision_type']),
                    context=data['context'],
                    goal=data['goal'],
                    decision=data['decision'],
                    outcome=data['outcome'],
                    confidence=data['confidence'],
                    autonomy_level=data['autonomy_level'],
                    lineage_hash=data.get('lineage_hash'),
                    metadata=data.get('metadata', {})
                )
                trail.entries.append(entry)

        trail.entry_counter = len(trail.entries)
        trail.log_path = log_path

        return trail


def create_audit_trail(log_path: Optional[Path] = None) -> AuditTrail:
    """
    Convenience function for creating audit trail

    Args:
        log_path: Optional path to JSONL log file

    Returns:
        New AuditTrail instance

    Example:
        >>> trail = create_audit_trail(Path("records/trial_001.jsonl"))
        >>> trail.log_reasoning(
        ...     context="User asked about AI safety",
        ...     conclusion="Recommend governance framework",
        ...     confidence=0.85
        ... )
    """
    return AuditTrail(log_path)
