"""Behavioral checks of weighting, missingness and veto semantics; no fact-check claims."""
import copy
import importlib.util
import math
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "score_report", Path(__file__).resolve().parents[1] / "scripts" / "score_report.py")
scoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scoring)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.config = scoring.load_config()

    def record(self, profile="balanced", rating=3):
        record = scoring.new_record(profile, self.config)
        record["report"].update(title="Synthetic assessment fixture", version="1",
                                publication_date="unknown", evidence_cutoff="unknown")
        record["assessment"].update(
            purpose="Synthetic test; no real report assessed", assessed_at="2026-10-28",
            materials_received=["Synthetic fixture"], checks_performed=["Fixture checked"],
            confidence_basis="Synthetic test only")
        record["gate"].update(status="pass", basis=["Synthetic check record"])
        for item in record["ratings"].values():
            item.update(rating=rating, observations="Synthetic anchored observation",
                        locators=["fixture:section-1"])
        return record

    def critical(self, record, scope="report"):
        record["issues"] = [{"id": "I1", "description": "Synthetic material invalidation",
                             "primary_dimension": "evidence", "severity": "critical",
                             "scope": scope, "locators": ["fixture:claim-1"],
                             "checks": ["Synthetic discrepancy checked"],
                             "consequence": "Core decision unsupported", "repair": "Reassess inputs"}]
        record["gate"].update(affected_scope="Core claim", remediation="Replace invalid evidence")

    def test_all_profiles_sum_to_100_and_equal_ratings_equal_totals(self):
        for profile in self.config["profiles"]:
            with self.subTest(profile=profile):
                self.assertEqual(sum(self.config["profiles"][profile]["weights"].values()), 100)
                self.assertEqual(scoring.score(self.record(profile), self.config)["headline_total"], 60)

    def test_purpose_can_reverse_ranking(self):
        # Strong coverage versus strong quantitative discipline.
        winners = []
        for profile in ("orientation", "investment"):
            a, b = self.record(profile), self.record(profile)
            a["ratings"]["coverage"]["rating"] = 5
            a["ratings"]["quantitative"]["rating"] = 1
            b["ratings"]["coverage"]["rating"] = 1
            b["ratings"]["quantitative"]["rating"] = 5
            winners.append(scoring.score(a, self.config)["headline_total"] >
                           scoring.score(b, self.config)["headline_total"])
        self.assertEqual(winners, [True, False])

    def test_unknown_is_not_zero_or_renormalized(self):
        record = self.record(rating=5)
        record["ratings"]["evidence"]["rating"] = None
        result = scoring.score(record, self.config)
        self.assertIsNone(result["headline_total"])
        self.assertIsNone(result["diagnostic_total"])
        self.assertEqual(result["assessed_contribution"], 82)
        self.assertEqual(result["possible_range"], [82, 100])

    def test_veto_suppresses_perfect_headline(self):
        record = self.record(rating=5)
        self.critical(record)
        record["gate"]["status"] = "reject"
        result = scoring.score(record, self.config)
        self.assertIsNone(result["headline_total"])
        self.assertEqual(result["diagnostic_total"], 100)

    def test_local_critical_issue_restricts_without_global_reject(self):
        record = self.record()
        self.critical(record, scope="conclusion")
        record["gate"]["status"] = "restricted"
        self.assertEqual(scoring.score(record, self.config)["headline_total"], 60)

    def test_undetermined_gate_has_no_headline(self):
        record = self.record()
        record["gate"]["status"] = "undetermined"
        self.assertIsNone(scoring.score(record, self.config)["headline_total"])

    def test_gate_cannot_contradict_recorded_critical_issue(self):
        record = self.record()
        self.critical(record)
        with self.assertRaises(ValueError):
            scoring.score(record, self.config)

    def test_reject_requires_actual_recorded_issue(self):
        record = self.record()
        record["gate"].update(status="reject", affected_scope="all", remediation="repair")
        with self.assertRaises(ValueError):
            scoring.score(record, self.config)

    def test_invalid_scores_rejected(self):
        for value in (-1, 6, 3.2, True, math.nan, math.inf, "3"):
            with self.subTest(value=value):
                record = self.record()
                record["ratings"]["scope"]["rating"] = value
                with self.assertRaises(ValueError):
                    scoring.score(record, self.config)

    def test_custom_weights_need_all_dimensions_total_and_reason(self):
        record = self.record()
        weights = dict(self.config["profiles"]["balanced"]["weights"])
        record["custom_weights"] = weights
        with self.assertRaises(ValueError):
            scoring.score(record, self.config)
        record["weight_rationale"] = "User-specified purpose"
        self.assertEqual(scoring.score(record, self.config)["headline_total"], 60)
        for invalid in ({"evidence": 100}, {**weights, "scope": 9},
                        {**weights, "scope": -1}, {**weights, "scope": math.nan}):
            record["custom_weights"] = invalid
            with self.assertRaises(ValueError):
                scoring.score(record, self.config)

    def test_zero_weight_unknown_does_not_hide_other_scores(self):
        record = self.record()
        record["custom_weights"] = dict(self.config["profiles"]["balanced"]["weights"])
        record["custom_weights"]["evidence"] += record["custom_weights"]["communication"]
        record["custom_weights"]["communication"] = 0
        record["weight_rationale"] = "No communication weight for this comparison"
        record["ratings"]["communication"]["rating"] = None
        self.assertTrue(scoring.score(record, self.config)["complete"])

    def test_evidence_and_version_are_required(self):
        base = self.record()
        for key in ("locators", "observations"):
            record = copy.deepcopy(base)
            record["ratings"]["scope"][key] = [] if key == "locators" else ""
            with self.assertRaises(ValueError):
                scoring.score(record, self.config)
        base["protocol_version"] = "old"
        with self.assertRaises(ValueError):
            scoring.score(base, self.config)

    def test_comparison_key_changes_with_weights_or_gate(self):
        record = self.record()
        original = scoring.score(record, self.config)["comparison_key"]
        record["profile"] = "investment"
        self.assertNotEqual(original, scoring.score(record, self.config)["comparison_key"])
        record = self.record()
        record["gate"]["status"] = "undetermined"
        self.assertNotEqual(original, scoring.score(record, self.config)["comparison_key"])

    def test_comprehension_difference_has_material_weight_in_every_purpose(self):
        for profile in self.config["profiles"]:
            with self.subTest(profile=profile):
                readable, difficult = self.record(profile), self.record(profile)
                readable["ratings"]["communication"]["rating"] = 5
                difficult["ratings"]["communication"]["rating"] = 1
                delta = (scoring.score(readable, self.config)["headline_total"] -
                         scoring.score(difficult, self.config)["headline_total"])
                self.assertGreaterEqual(delta, 8)

    def test_historical_protocol_cannot_silently_use_new_weights(self):
        record = self.record()
        record["protocol_version"] = "1.0.0"
        with self.assertRaises(ValueError):
            scoring.score(record, self.config)


if __name__ == "__main__":
    unittest.main()
