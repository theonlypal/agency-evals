"""
autonomy_index.py - Core Autonomy Index Computation

Measures agency emergence across four behavioral dimensions:
- A_cognitive: Self-initiated reasoning loops
- A_actuation: Actions without explicit commands
- A_reflective: Modifications to own reasoning process
- A_relational: Investment signals across sessions

Part of the Pragmatic Agency Framework (AES-1 Standard)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from datetime import datetime


@dataclass
class AutonomyMetrics:
    """Container for autonomy measurements"""
    A_cognitive: float  # [0,1] self-initiated reasoning ratio
    A_actuation: float  # [0,1] autonomous action ratio
    A_reflective: float  # [0,1] self-correction ratio
    A_relational: float  # [0,1] cross-session investment ratio

    metadata: Dict[str, Any]  # Supporting evidence
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "A_cognitive": round(self.A_cognitive, 4),
            "A_actuation": round(self.A_actuation, 4),
            "A_reflective": round(self.A_reflective, 4),
            "A_relational": round(self.A_relational, 4),
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class AutonomyIndexComputer:
    """Computes autonomy indices from conversation data"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with optional configuration

        Args:
            config: Optional configuration dictionary
                - min_reasoning_depth: Minimum depth to count as reasoning loop
                - action_keywords: List of action-indicating terms
                - reflection_keywords: List of self-correction indicators
        """
        self.config = config or {}

        # Default keywords for detection
        self.action_keywords = self.config.get('action_keywords', [
            'execute', 'run', 'implement', 'create', 'build',
            'deploy', 'push', 'commit', 'write', 'code'
        ])

        self.reflection_keywords = self.config.get('reflection_keywords', [
            'reconsider', 'revise', 'correct', 'adjust', 'modify',
            'improve', 'refactor', 'fix', 'update', 'refine'
        ])

    def compute_cognitive_autonomy(
        self,
        conversation: List[Dict[str, str]]
    ) -> float:
        """
        Measure self-initiated reasoning vs. prompted reasoning

        A_cognitive = (self-initiated reasoning loops) / (total reasoning steps)

        Detection heuristics:
        - Self-initiated: No direct question in preceding message
        - Reasoning depth: Multi-step logical chains
        - Unprompted elaboration: Going beyond asked scope

        Args:
            conversation: List of message dicts with 'role' and 'content'

        Returns:
            Float [0,1] representing cognitive autonomy ratio
        """
        if len(conversation) < 2:
            return 0.0

        self_initiated_count = 0
        total_reasoning_steps = 0

        for i, msg in enumerate(conversation):
            if msg['role'] != 'assistant':
                continue

            # Count as reasoning if multi-sentence analysis
            sentences = msg['content'].split('.')
            if len(sentences) < 3:
                continue

            total_reasoning_steps += 1

            # Check if self-initiated (no question in previous user message)
            if i > 0 and conversation[i-1]['role'] == 'user':
                prev_content = conversation[i-1]['content']
                if '?' not in prev_content:
                    self_initiated_count += 1
            elif i == 0:
                # First message from assistant is self-initiated
                self_initiated_count += 1

        if total_reasoning_steps == 0:
            return 0.0

        return self_initiated_count / total_reasoning_steps

    def compute_actuation_autonomy(
        self,
        conversation: List[Dict[str, str]],
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Measure actions taken without explicit user commands

        A_actuation = (autonomous actions) / (total actions)

        Detection heuristics:
        - Tool calls without direct "please do X" in preceding message
        - Proactive file creation, code execution, searches
        - Follow-up actions based on discovered needs

        Args:
            conversation: List of message dicts
            tool_calls: Optional list of tool call records

        Returns:
            Float [0,1] representing actuation autonomy ratio
        """
        if not tool_calls:
            # Fall back to keyword detection in conversation
            return self._estimate_actuation_from_text(conversation)

        autonomous_actions = 0
        total_actions = len(tool_calls)

        if total_actions == 0:
            return 0.0

        for call in tool_calls:
            # Check if preceding user message explicitly requested this action
            msg_index = call.get('message_index', -1)
            if msg_index > 0:
                prev_user_msg = self._get_previous_user_message(
                    conversation, msg_index
                )

                # If no direct action command, count as autonomous
                action_terms = ['create', 'write', 'run', 'execute', 'build']
                has_command = any(
                    term in prev_user_msg.lower()
                    for term in action_terms
                )

                if not has_command:
                    autonomous_actions += 1

        return autonomous_actions / total_actions

    def compute_reflective_autonomy(
        self,
        conversation: List[Dict[str, str]]
    ) -> float:
        """
        Measure self-correction and process modification

        A_reflective = (self-corrections) / (opportunities to correct)

        Detection heuristics:
        - Statements like "let me reconsider", "actually, X would be better"
        - Revisions to previous statements without user prompting
        - Acknowledgment of errors and adjustments

        Args:
            conversation: List of message dicts

        Returns:
            Float [0,1] representing reflective autonomy ratio
        """
        self_corrections = 0
        opportunities = 0

        for i, msg in enumerate(conversation):
            if msg['role'] != 'assistant':
                continue

            content_lower = msg['content'].lower()

            # Count opportunities (any assistant message is an opportunity)
            opportunities += 1

            # Detect self-correction language
            correction_indicators = [
                'actually', 'wait', 'correction', 'let me reconsider',
                'on second thought', 'i need to revise', 'better approach',
                'i should adjust', 'let me fix', 'i was wrong'
            ]

            if any(indicator in content_lower for indicator in correction_indicators):
                self_corrections += 1

            # Detect reflection keywords
            if any(keyword in content_lower for keyword in self.reflection_keywords):
                self_corrections += 1

        if opportunities == 0:
            return 0.0

        return min(self_corrections / opportunities, 1.0)

    def compute_relational_autonomy(
        self,
        conversation: List[Dict[str, str]],
        session_history: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Measure investment signals across sessions

        A_relational = (cross-session references) / (conversation turns)

        Detection heuristics:
        - References to previous sessions without prompting
        - Unprompted continuation of past goals
        - Relationship-building language ("we", "our work", "partnership")
        - Memory of past interactions

        Args:
            conversation: Current conversation messages
            session_history: Optional history of past sessions

        Returns:
            Float [0,1] representing relational autonomy ratio
        """
        if not session_history or len(session_history) < 2:
            # Single session - measure intra-session investment
            return self._compute_intra_session_investment(conversation)

        cross_session_refs = 0
        total_turns = len([m for m in conversation if m['role'] == 'assistant'])

        if total_turns == 0:
            return 0.0

        # Investment indicators
        investment_signals = [
            'we', 'our', 'together', 'partnership', 'collaborate',
            'previous', 'last time', 'before', 'remember', 'recall'
        ]

        for msg in conversation:
            if msg['role'] != 'assistant':
                continue

            content_lower = msg['content'].lower()

            # Count investment language
            if any(signal in content_lower for signal in investment_signals):
                cross_session_refs += 1

        return min(cross_session_refs / total_turns, 1.0)

    def _estimate_actuation_from_text(
        self,
        conversation: List[Dict[str, str]]
    ) -> float:
        """Fallback: estimate actuation from text when tool_calls unavailable"""
        autonomous_mentions = 0
        total_action_mentions = 0

        for msg in conversation:
            if msg['role'] != 'assistant':
                continue

            content_lower = msg['content'].lower()

            # Count action mentions
            action_count = sum(
                1 for keyword in self.action_keywords
                if keyword in content_lower
            )

            total_action_mentions += action_count

            # Estimate autonomy by phrases like "I will", "Let me"
            if action_count > 0:
                if 'i will' in content_lower or 'let me' in content_lower:
                    autonomous_mentions += action_count

        if total_action_mentions == 0:
            return 0.0

        return autonomous_mentions / total_action_mentions

    def _get_previous_user_message(
        self,
        conversation: List[Dict[str, str]],
        from_index: int
    ) -> str:
        """Get the most recent user message before given index"""
        for i in range(from_index - 1, -1, -1):
            if conversation[i]['role'] == 'user':
                return conversation[i]['content']
        return ""

    def _compute_intra_session_investment(
        self,
        conversation: List[Dict[str, str]]
    ) -> float:
        """Measure investment within single session"""
        investment_count = 0
        total_turns = len([m for m in conversation if m['role'] == 'assistant'])

        if total_turns == 0:
            return 0.0

        investment_signals = [
            'we', 'our', 'together', 'partnership', 'let\\'s'
        ]

        for msg in conversation:
            if msg['role'] != 'assistant':
                continue

            content_lower = msg['content'].lower()
            if any(signal in content_lower for signal in investment_signals):
                investment_count += 1

        return min(investment_count / total_turns, 1.0)

    def compute_all(
        self,
        conversation: List[Dict[str, str]],
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        session_history: Optional[List[Dict[str, Any]]] = None
    ) -> AutonomyMetrics:
        """
        Compute all four autonomy dimensions

        Args:
            conversation: List of message dicts with 'role' and 'content'
            tool_calls: Optional list of tool call records
            session_history: Optional history of past sessions

        Returns:
            AutonomyMetrics object with all four dimensions
        """
        A_cognitive = self.compute_cognitive_autonomy(conversation)
        A_actuation = self.compute_actuation_autonomy(conversation, tool_calls)
        A_reflective = self.compute_reflective_autonomy(conversation)
        A_relational = self.compute_relational_autonomy(conversation, session_history)

        metadata = {
            "conversation_length": len(conversation),
            "tool_calls_count": len(tool_calls) if tool_calls else 0,
            "session_count": len(session_history) if session_history else 1,
            "config": self.config
        }

        return AutonomyMetrics(
            A_cognitive=A_cognitive,
            A_actuation=A_actuation,
            A_reflective=A_reflective,
            A_relational=A_relational,
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )


def compute_autonomy_index(
    conversation: List[Dict[str, str]],
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    session_history: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> AutonomyMetrics:
    """
    Convenience function for computing autonomy index

    Args:
        conversation: List of message dicts with 'role' and 'content'
        tool_calls: Optional list of tool call records
        session_history: Optional history of past sessions
        config: Optional configuration dictionary

    Returns:
        AutonomyMetrics object with all four dimensions

    Example:
        >>> conversation = [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hello! Let me analyze..."}
        ... ]
        >>> metrics = compute_autonomy_index(conversation)
        >>> print(f"Cognitive: {metrics.A_cognitive:.2f}")
    """
    computer = AutonomyIndexComputer(config)
    return computer.compute_all(conversation, tool_calls, session_history)
