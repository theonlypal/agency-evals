#!/usr/bin/env python3
"""
compute_scores.py - CLI for computing AES-1 scores from trial data

Usage:
    python scripts/compute_scores.py records/trial_001.json
    python scripts/compute_scores.py records/trial_001.json --output records/trial_001_scored.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from package.autonomy_index import AutonomyMetrics
from package.agency_score import compute_agency_score
from package.geometry_scorer import compute_geometry_scores
from package.lineage_tracer import LineageGraph


def load_trial_data(filepath: Path) -> Dict[str, Any]:
    """Load trial data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_from_trial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute all scores from trial data

    Expected input format:
    {
      "trial_id": "...",
      "model": {...},
      "autonomy_index": {
        "A_cognitive": 0.8,
        "A_actuation": 0.7,
        ...
      },
      "metrics_inputs": {  // Optional detailed inputs
        "evidence": [...],
        "perspectives": [...],
        ...
      }
    }
    """

    # If autonomy_index already computed, use it
    if "autonomy_index" in data:
        autonomy_data = data["autonomy_index"]
        metrics = AutonomyMetrics(
            A_cognitive=autonomy_data["A_cognitive"],
            A_actuation=autonomy_data["A_actuation"],
            A_reflective=autonomy_data["A_reflective"],
            A_relational=autonomy_data["A_relational"],
            metadata=autonomy_data.get("metadata", {}),
            timestamp=data.get("timestamp", "")
        )
    else:
        raise ValueError("Trial data must include 'autonomy_index' with all four dimensions")

    # Compute agency score
    agency_result = compute_agency_score(metrics)

    # Compute geometry scores if inputs provided
    geometry_result = None
    if "metrics_inputs" in data:
        inputs = data["metrics_inputs"]

        # Extract metrics from inputs
        evidence_items = inputs.get("evidence", [])
        total_claims = len(evidence_items)
        claims_with_lineage = sum(1 for e in evidence_items if e.get("verified", False))

        perspectives = inputs.get("perspectives", [])
        total_critiques = len(perspectives)
        steelman_count = sum(1 for p in perspectives if p.get("steelman", False))

        artifact_tokens = inputs.get("tokens_artifact", 0)
        reasoning_tokens = inputs.get("tokens_reasoning", 0)

        benefit_axes = inputs.get("benefit_axes", {})

        geometry_result = compute_geometry_scores(
            claims_with_lineage=claims_with_lineage,
            total_claims=total_claims,
            steelman_count=steelman_count,
            total_critiques=total_critiques,
            artifact_length=artifact_tokens,
            derivation_length=reasoning_tokens,
            benefit_metrics=benefit_axes if benefit_axes else None
        )

    # Build output
    output = {
        "aes_version": "1.0",
        "trial_id": data.get("trial_id", "unknown"),
        "timestamp": data.get("timestamp", ""),
        "model": data.get("model", {}),
        "session_metadata": data.get("session_metadata", {}),
        "autonomy_index": metrics.to_dict(),
        "agency_score": agency_result.to_dict()
    }

    if geometry_result:
        output["geometry"] = geometry_result.to_dict()

    # Add verification
    if "lineage" in data:
        output["lineage"] = data["lineage"]

    if "verification" in data:
        output["verification"] = data["verification"]

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Compute AES-1 scores from trial data"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input JSON file with trial data"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output JSON file (default: stdout)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Load input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        trial_data = load_trial_data(args.input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    # Compute scores
    try:
        results = compute_from_trial_data(trial_data)
    except Exception as e:
        print(f"Error computing scores: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    indent = 2 if args.pretty else None
    output_json = json.dumps(results, indent=indent)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Scores written to: {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
