#!/usr/bin/env python3
"""Check structural integrity of research evidence ledgers.

Does NOT independently verify claims, source identities, numerical facts,
source independence, experimental results, or scientific interpretations.

Usage:
  python scripts/check_research_pack.py --claims work/claims.csv --evidence work/evidence.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

CLAIM_COLUMNS = {
    "claim_id", "tier", "claim_type", "claim_text", "entity",
    "observation_period", "as_of_date", "unit", "denominator",
    "decision_implication", "verification_status", "confidence", "limitations"
}
EVIDENCE_COLUMNS = {
    "evidence_id", "claim_id", "source_title", "source_url", "origin_actor",
    "source_type", "publication_date", "observation_period",
    "evidence_chain_id", "independently_generated", "support_relation",
    "verification_status", "exact_location", "limitations"
}
TIERS = {"Tier1", "Tier2", "Tier3"}
CLAIM_STATUSES = {
    "verified_original", "corroborated", "single_source", "secondary_only",
    "conflicting", "not_verified", "stale"
}
EVIDENCE_STATUSES = {"checked", "unchecked", "inaccessible", "conflicting"}
RELATIONS = {"supports", "contradicts", "contextualizes"}
YES_NO_UNKNOWN = {"yes", "no", "unknown"}
JUDGMENT_COLUMNS = {
    "judgment_id", "claim_ids", "judgment_type", "judgment_text",
    "basis_evidence_ids", "strongest_alternative", "decision_implication",
    "horizon", "update_trigger", "confidence", "limitations"
}
CHALLENGE_COLUMNS = {
    "challenge_id", "claim_id", "challenge_type", "challenge_text",
    "evidence_ids", "search_scope", "search_date", "disposition",
    "effect_on_judgment", "independence_check", "remaining_gap"
}
JUDGMENT_TYPES = {"interpretation", "conditional_forecast", "recommendation"}
CHALLENGE_TYPES = {
    "adverse_observation", "alternative_mechanism", "missing_test", "search_no_result"
}
DISPOSITIONS = {
    "retained_with_limits", "revised", "downgraded", "withdrawn", "unresolved"
}
FACT_TYPES = {"observation", "fact", "source_fact", "calculation", "measured_result"}


def ids(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def read_rows(path: Path, required: set[str]) -> tuple[list[dict], list[str]]:
    errors = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rdr = csv.DictReader(f)
            header = set(rdr.fieldnames or [])
            missing = sorted(required - header)
            if missing:
                errors.append(f"{path}: missing headers: {', '.join(missing)}")
            rows = [{k: (v or "").strip() for k, v in row.items() if k is not None}
                    for row in rdr]
    except (OSError, UnicodeError, csv.Error) as e:
        return [], [f"{path}: cannot read CSV: {e}"]
    return rows, errors


def check_date(value: str, location: str, errors: list[str]):
    if not value:
        return
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{location}: expected ISO date YYYY-MM-DD, got {value!r}")


def check(
    claims: list[dict], evidence: list[dict], judgments: list[dict] | None = None,
    challenges: list[dict] | None = None, strict: bool = False,
) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    seen_claims, seen_evidence = set(), set()
    claim_map = {}
    evidence_for = defaultdict(list)
    chains_for_urls = defaultdict(set)

    for idx, c in enumerate(claims, 2):
        cid, tier = c.get("claim_id", ""), c.get("tier", "")
        loc = f"claims.csv:{idx}"
        if not cid or cid in seen_claims:
            errors.append(f"{loc}: blank or repeated claim_id {cid!r}")
        seen_claims.add(cid)
        claim_map[cid] = c
        if tier not in TIERS:
            errors.append(f"{loc}: tier must be Tier1/Tier2/Tier3")
        if not c.get("claim_text", ""):
            errors.append(f"{loc}: claim_text is blank")
        if c.get("verification_status", "") not in CLAIM_STATUSES:
            errors.append(f"{loc}: invalid or blank verification_status")
        if tier == "Tier1" and not c.get("decision_implication", ""):
            warnings.append(f"{loc}: Tier1 claim has no decision_implication")
        if c.get("verification_status") in {"not_verified", "conflicting", "stale"} and not c.get("limitations"):
            warnings.append(f"{loc}: unresolved or stale claim lacks an explicit limitation")
        check_date(c.get("as_of_date", ""), loc + " as_of_date", errors)

    for idx, e in enumerate(evidence, 2):
        eid, cid = e.get("evidence_id", ""), e.get("claim_id", "")
        loc = f"evidence.csv:{idx}"
        if not eid or eid in seen_evidence:
            errors.append(f"{loc}: blank or repeated evidence_id {eid!r}")
        seen_evidence.add(eid)
        if cid not in claim_map:
            errors.append(f"{loc}: claim_id {cid!r} not found in claims.csv")
        if not e.get("source_title"):
            errors.append(f"{loc}: source_title is blank")
        if not (e.get("source_url") or e.get("exact_location")):
            errors.append(f"{loc}: missing both source_url and exact_location")
        if not e.get("evidence_chain_id"):
            errors.append(f"{loc}: evidence_chain_id is blank")
        if e.get("independently_generated", "") not in YES_NO_UNKNOWN:
            errors.append(f"{loc}: independently_generated must be yes/no/unknown")
        if e.get("support_relation", "") not in RELATIONS:
            errors.append(f"{loc}: support_relation must be supports/contradicts/contextualizes")
        if e.get("verification_status", "") not in EVIDENCE_STATUSES:
            errors.append(f"{loc}: verification_status must be checked/unchecked/inaccessible/conflicting")
        if e.get("verification_status") == "checked" and not e.get("exact_location"):
            warnings.append(f"{loc}: checked evidence lacks exact page/section/table location")
        if e.get("independently_generated") == "yes":
            missing = [key for key in ("observation_path", "independence_basis") if not e.get(key)]
            if missing:
                message = f"{loc}: declared independence lacks {', '.join(missing)}; metadata is not proof"
                (errors if strict else warnings).append(message)
        check_date(e.get("publication_date", ""), loc + " publication_date", errors)
        evidence_for[cid].append(e)
        if e.get("source_url"):
            chains_for_urls[e["source_url"]].add(e.get("evidence_chain_id"))

    for url, chains in chains_for_urls.items():
        if len(chains) > 1:
            warnings.append(f"source URL assigned multiple evidence_chain_id values: {url}")

    for cid, c in claim_map.items():
        es = evidence_for[cid]
        checked = [e for e in es if e.get("verification_status") == "checked"]
        supporting = [e for e in checked if e.get("support_relation") == "supports"]
        chains = {e.get("evidence_chain_id") for e in supporting if e.get("evidence_chain_id") not in ("", "unknown")}
        independent = [e for e in supporting if e.get("independently_generated") == "yes"]
        status = c.get("verification_status")
        if c.get("tier") == "Tier1" and not checked:
            warnings.append(f"Tier1 {cid}: no checked evidence; keep conclusion qualified")
        if status == "corroborated" and (len(chains) < 2 or not independent):
            errors.append(f"{cid}: marked corroborated without >=2 checked, distinct chains and any independently_generated=yes")
        if status == "verified_original" and not supporting:
            errors.append(f"{cid}: marked verified_original without checked supporting evidence")
        if status == "single_source" and len(chains) >= 2 and independent:
            warnings.append(f"{cid}: labeled single_source, though multiple evidence paths are marked; check status manually")
        if c.get("tier") == "Tier1" and status not in {"not_verified", "conflicting", "stale"}:
            if challenges is None and not any(e.get("support_relation") == "contradicts" for e in es):
                warnings.append(f"Tier1 {cid}: no direct contradiction recorded; inspect adverse context, alternatives or bounded search in a challenge log")
        if status == "secondary_only" and any(e.get("source_type") == "original_record" for e in checked):
            warnings.append(f"{cid}: secondary_only despite a checked original_record; revisit narrow supported claim")

    evidence_map = {e.get("evidence_id"): e for e in evidence}
    challenges_for = defaultdict(list)
    seen = set()
    for index, row in enumerate(challenges or [], 2):
        loc = f"challenges.csv:{index}"
        key, cid = row.get("challenge_id", ""), row.get("claim_id", "")
        if not key or key in seen:
            errors.append(f"{loc}: blank or repeated challenge_id {key!r}")
        seen.add(key)
        if cid not in claim_map:
            errors.append(f"{loc}: unknown claim_id {cid!r}")
        kind = row.get("challenge_type")
        if kind not in CHALLENGE_TYPES:
            errors.append(f"{loc}: invalid challenge_type")
        if row.get("disposition") not in DISPOSITIONS:
            errors.append(f"{loc}: invalid disposition")
        for field in ("challenge_text", "effect_on_judgment", "independence_check"):
            if not row.get(field):
                errors.append(f"{loc}: missing {field}")
        refs = ids(row.get("evidence_ids", ""))
        for eid in refs:
            e = evidence_map.get(eid)
            if e is None:
                errors.append(f"{loc}: unknown evidence ID {eid!r}")
            elif e.get("claim_id") != cid:
                errors.append(f"{loc}: evidence {eid} is not linked to claim {cid}")
        if kind == "adverse_observation":
            if not refs or not any(evidence_map.get(eid, {}).get("verification_status") == "checked" for eid in refs):
                errors.append(f"{loc}: adverse observation needs checked evidence")
        if kind == "search_no_result":
            if refs:
                errors.append(f"{loc}: search_no_result cannot contain found evidence IDs")
            for field in ("search_scope", "search_date", "remaining_gap"):
                if not row.get(field):
                    errors.append(f"{loc}: search_no_result needs {field}")
        if kind == "missing_test" and not row.get("remaining_gap"):
            errors.append(f"{loc}: missing_test needs remaining_gap")
        check_date(row.get("search_date", ""), loc + " search_date", errors)
        challenges_for[cid].append(row)

    judgments_for = defaultdict(list)
    seen = set()
    for index, row in enumerate(judgments or [], 2):
        loc = f"judgments.csv:{index}"
        key = row.get("judgment_id", "")
        if not key or key in seen:
            errors.append(f"{loc}: blank or repeated judgment_id {key!r}")
        seen.add(key)
        cids, refs = ids(row.get("claim_ids", "")), ids(row.get("basis_evidence_ids", ""))
        if not cids:
            errors.append(f"{loc}: no linked claims")
        for cid in cids:
            if cid not in claim_map:
                errors.append(f"{loc}: unknown claim ID {cid!r}")
            judgments_for[cid].append(row)
        kind = row.get("judgment_type")
        if kind not in JUDGMENT_TYPES:
            errors.append(f"{loc}: invalid judgment_type")
        for field in ("judgment_text", "basis_evidence_ids", "strongest_alternative", "decision_implication", "update_trigger", "confidence"):
            if not row.get(field):
                errors.append(f"{loc}: missing {field}")
        if kind == "conditional_forecast" and not row.get("horizon"):
            errors.append(f"{loc}: conditional forecast needs horizon")
        for eid in refs:
            e = evidence_map.get(eid)
            if e is None:
                errors.append(f"{loc}: unknown evidence ID {eid!r}")
            elif e.get("claim_id") not in cids:
                errors.append(f"{loc}: basis evidence {eid} is not linked to listed claims")
        for cid in cids:
            if cid in claim_map and not any(evidence_map.get(eid, {}).get("claim_id") == cid for eid in refs):
                errors.append(f"{loc}: listed claim {cid} has no basis evidence in this judgment")
        if refs and not any(
            evidence_map.get(eid, {}).get("verification_status") == "checked"
            and evidence_map.get(eid, {}).get("support_relation") in {"supports", "contextualizes"}
            for eid in refs
        ):
            warnings.append(f"{loc}: no checked supporting/contextual basis; qualify the judgment")

    for cid, c in claim_map.items():
        if c.get("tier") != "Tier1":
            continue
        if not challenges_for[cid] and (strict or challenges is not None):
            (errors if strict else warnings).append(f"Tier1 {cid}: no challenge coverage")
        if strict and c.get("claim_type", "").lower() not in FACT_TYPES and not judgments_for[cid]:
            errors.append(f"Tier1 {cid}: inference lacks linked author judgment")
    if strict and not claims:
        errors.append("strict mode requires a nonempty claim register")
    return errors, warnings


def review_summary(claims: list[dict], evidence: list[dict], judgments: list[dict], challenges: list[dict]) -> dict:
    """Export declared traceability, never a substantive verification badge."""
    es = {e["evidence_id"]: e for e in evidence}
    rows = []
    for claim in claims:
        cid = claim["claim_id"]
        rows.append({
            "claim_id": cid, "claim_text": claim["claim_text"], "tier": claim["tier"],
            "verification_status": claim["verification_status"],
            "judgments": [r for r in judgments if cid in ids(r.get("claim_ids", ""))],
            "challenges": [{**r, "evidence_relations": [
                {"evidence_id": eid, "support_relation": es[eid]["support_relation"],
                 "source_url": es[eid]["source_url"], "evidence_chain_id": es[eid]["evidence_chain_id"]}
                for eid in ids(r.get("evidence_ids", ""))
            ]} for r in challenges if r.get("claim_id") == cid],
        })
    return {"schema_version": "2.2", "structural_check_only": True,
            "substantive_verification": "not_established_by_this_script", "rows": rows}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--claims", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--judgments", type=Path)
    p.add_argument("--challenges", type=Path)
    p.add_argument("--strict", action="store_true", help="Require V2.2 Tier1 judgment/challenge coverage")
    p.add_argument("--review-output", type=Path, help="Write a new ledger-derived JSON review summary; never overwrites")
    args = p.parse_args()
    claims, ce = read_rows(args.claims, CLAIM_COLUMNS)
    evidence, ee = read_rows(args.evidence, EVIDENCE_COLUMNS)
    judgments, je = read_rows(args.judgments, JUDGMENT_COLUMNS) if args.judgments else (None, [])
    challenges, he = read_rows(args.challenges, CHALLENGE_COLUMNS) if args.challenges else (None, [])
    errors, warnings = check(claims, evidence, judgments, challenges, args.strict)
    errors = ce + ee + je + he + errors
    if args.review_output and args.review_output.exists():
        errors.append(f"refusing to overwrite review output: {args.review_output}")
    print("=== STRUCTURAL RESEARCH LEDGER CHECK (NOT FACT VERIFICATION) ===")
    print(f"Claim rows: {len(claims)} | Evidence rows: {len(evidence)}")
    for x in errors:
        print("ERROR:", x)
    for x in warnings:
        print("WARN: ", x)
    if not claims:
        print("INFO: No claims yet; cannot assess research readiness.")
    if errors:
        print(f"STRUCTURE FAIL: {len(errors)} errors, {len(warnings)} warnings")
        return 1
    if args.review_output:
        try:
            with args.review_output.open("x", encoding="utf-8") as f:
                json.dump(review_summary(claims, evidence, judgments or [], challenges or []), f, ensure_ascii=False, indent=2)
                f.write("\n")
        except (OSError, KeyError) as e:
            print(f"ERROR: cannot export review summary: {e}")
            return 1
    print(f"STRUCTURE CHECK COMPLETE: 0 errors, {len(warnings)} warnings")
    print("IMPORTANT: Original documents, numerical accuracy, source independence and causal claims still require human/independent substantive review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
