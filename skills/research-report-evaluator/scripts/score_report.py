#!/usr/bin/env python3
"""Validate human assessments and calculate purpose-specific scores; not a fact checker."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

CONFIG = Path(__file__).resolve().parents[1] / "references" / "profiles.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, name, required=False):
    require(isinstance(value, list), f"{name}: expected a list")
    require(all(nonempty(item) for item in value), f"{name}: blank/non-string entries")
    require(not required or bool(value), f"{name}: at least one entry required")


def weights_valid(weights, dimensions):
    require(isinstance(weights, dict) and set(weights) == set(dimensions),
            "weights must contain exactly the ten dimension IDs")
    require(all(number(v) and 0 <= v <= 100 for v in weights.values()),
            "weights must be finite nonnegative numbers")
    require(math.isclose(sum(weights.values()), 100, rel_tol=0, abs_tol=1e-8),
            "weights must sum to 100")


def load_config():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    for profile in config["profiles"].values():
        weights_valid(profile["weights"], config["dimensions"])
    return config


def new_record(profile, config):
    require(profile in config["profiles"], "unknown profile")
    return {
        "protocol_version": config["version"], "profile": profile,
        "report": {"title": "", "version": "", "publication_date": "",
                   "evidence_cutoff": ""},
        "assessment": {"purpose": "", "assessed_at": "", "materials_received": [],
                       "checks_performed": [], "limitations": [],
                       "confidence": "low", "confidence_basis": ""},
        "gate": {"status": "undetermined", "basis": [],
                 "affected_scope": "", "remediation": ""},
        "ratings": {key: {"rating": None, "observations": "", "locators": []}
                    for key in config["dimensions"]},
        "issues": [],
    }


def score(record, config):
    require(isinstance(record, dict), "record must be an object")
    require(record.get("protocol_version") == config["version"],
            "protocol version mismatch; use the matching skill version or reassess")
    profile = record.get("profile")
    require(profile in config["profiles"], "unknown profile")
    dimensions = config["dimensions"]
    weights = record.get("custom_weights", config["profiles"][profile]["weights"])
    weights_valid(weights, dimensions)
    custom = "custom_weights" in record
    require(not custom or nonempty(record.get("weight_rationale")),
            "custom weights require weight_rationale")
    report = record.get("report", {})
    require(isinstance(report, dict), "report must be an object")
    for key in ("title", "version", "publication_date", "evidence_cutoff"):
        require(nonempty(report.get(key)), f"report.{key} required; state unknown if unavailable")
    assessment = record.get("assessment", {})
    require(isinstance(assessment, dict), "assessment must be an object")
    for key in ("purpose", "assessed_at", "confidence_basis"):
        require(nonempty(assessment.get(key)), f"assessment.{key} required")
    require(assessment.get("confidence") in ("high", "medium", "low"),
            "assessment.confidence must be high/medium/low")
    for key in ("materials_received", "checks_performed", "limitations"):
        strings(assessment.get(key), f"assessment.{key}", key == "materials_received")

    gate = record.get("gate", {})
    require(isinstance(gate, dict), "gate must be an object")
    status = gate.get("status")
    require(status in ("pass", "restricted", "reject", "undetermined"), "invalid gate status")
    strings(gate.get("basis"), "gate.basis", required=True)
    if status != "undetermined":
        require(bool(assessment["checks_performed"]), "a determined gate requires checks_performed")
    if status in ("restricted", "reject"):
        require(nonempty(gate.get("affected_scope")) and nonempty(gate.get("remediation")),
                "restricted/reject require affected_scope and remediation")

    issues = record.get("issues", [])
    require(isinstance(issues, list), "issues must be a list")
    seen = set()
    critical_report = False
    for issue in issues:
        require(isinstance(issue, dict), "each issue must be an object")
        for key in ("id", "description", "consequence", "repair"):
            require(nonempty(issue.get(key)), f"issue.{key} required")
        require(issue["id"] not in seen, "issue IDs must be unique")
        seen.add(issue["id"])
        require(issue.get("primary_dimension") in dimensions, "invalid issue primary_dimension")
        require(issue.get("severity") in ("minor", "major", "critical"), "invalid issue severity")
        require(issue.get("scope") in ("conclusion", "report"), "invalid issue scope")
        strings(issue.get("locators"), "issue.locators", required=True)
        strings(issue.get("checks"), "issue.checks", required=True)
        if issue["severity"] in ("major", "critical"):
            require(status != "pass", "unresolved major/critical issue cannot have gate=pass")
        if issue["severity"] == "critical" and issue["scope"] == "report":
            critical_report = True
    require(not critical_report or status == "reject",
            "confirmed critical report-wide issue requires gate=reject")
    require(status != "reject" or critical_report,
            "gate=reject requires a critical report-wide issue with checks")

    ratings = record.get("ratings", {})
    require(isinstance(ratings, dict) and set(ratings) == set(dimensions),
            "ratings must contain exactly the ten dimension IDs")
    contribution = 0.0
    missing_weight = 0.0
    missing = []
    rows = []
    for key, label in dimensions.items():
        item = ratings[key]
        require(isinstance(item, dict) and "rating" in item, f"{key}: rating field required")
        rating = item["rating"]
        require(rating is None or (number(rating) and 0 <= rating <= 5
                                  and math.isclose(rating * 2, round(rating * 2), abs_tol=1e-8)),
                f"{key}: rating must be null or 0..5 in steps of 0.5")
        require(nonempty(item.get("observations")), f"{key}: observations/reason for unknown required")
        strings(item.get("locators"), f"{key}.locators", required=rating is not None)
        value = None if rating is None else weights[key] * rating / 5
        if rating is None and weights[key] > 0:
            missing_weight += weights[key]
            missing.append(key)
        elif value is not None:
            contribution += value
        rows.append({"id": key, "label": label, "weight": weights[key], "rating": rating,
                     "contribution": None if value is None else round(value, 2),
                     "observations": item["observations"], "locators": item["locators"]})
    complete = not missing
    total = round(contribution, 1) if complete else None
    comparison = {"version": config["version"], "weights": weights, "gate": status}
    comparison_key = hashlib.sha256(json.dumps(comparison, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "protocol_version": config["version"], "report": report, "assessment": assessment,
        "profile": profile, "weight_mode": "custom" if custom else "preset",
        "weight_rationale": record.get("weight_rationale"), "weights": weights,
        "gate": gate, "issues": issues, "complete": complete,
        "headline_total": total if status in ("pass", "restricted") else None,
        "diagnostic_total": total, "assessed_contribution": round(contribution, 1),
        "unassessed_weight": round(missing_weight, 2), "unassessed_dimensions": missing,
        "possible_range": [round(contribution, 1), round(contribution + missing_weight, 1)],
        "comparison_key": comparison_key, "dimensions": rows,
        "notice": "Arithmetic/record validation only; not factual verification. Unknown ranges are not confidence intervals. Compare only with matching purpose, weights, gate restrictions and review depth.",
    }


def write_json(data, path):
    rendered = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if path:
        target = Path(path)
        require(not target.exists(), f"output exists: {target}; use a new versioned path")
        with target.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="generate an unscored record")
    init.add_argument("--profile", default="balanced")
    init.add_argument("--output")
    calc = sub.add_parser("score", help="validate a completed assessment and calculate")
    calc.add_argument("input")
    calc.add_argument("--output")
    args = parser.parse_args()
    try:
        config = load_config()
        if args.command == "init":
            result = new_record(args.profile, config)
        else:
            with Path(args.input).open(encoding="utf-8") as stream:
                result = score(json.load(stream), config)
        write_json(result, args.output)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
