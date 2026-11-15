import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import config
import detector
import run_capstone_eval


class CapstoneRunnerTests(unittest.TestCase):
    def test_three_trials_save_real_evidence_and_pass_with_available_detector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(config, "LOG_DIR", root / "logs"),
                patch.object(config, "AUDIT_LOG", root / "logs" / "audit.jsonl"),
                patch.object(config, "REQUEST_LOG", root / "logs" / "requests.jsonl"),
                patch.object(config, "RESULTS_DIR", root / "results"),
                patch.object(detector, "model_signal", return_value=0.2),
            ):
                client = app.app.test_client()
                trials = [run_capstone_eval.evaluate_trial(client, i) for i in range(1, 4)]
                report, evidence, passed = run_capstone_eval.write_results(trials)
                data = json.loads(evidence.read_text(encoding="utf-8"))
                report_text = report.read_text(encoding="utf-8")

            self.assertTrue(passed)
            self.assertEqual(len(data["trials"]), 3)
            self.assertTrue(all(result["passed"] for trial in data["trials"] for result in trial))
            self.assertEqual(report_text.count(" | MET |"), 5)
            rate_events = data["trials"][0][1]["evidence"]
            self.assertEqual([item["status"] for item in rate_events], [200] * 10 + [429])
            self.assertEqual(data["trials"][0][2]["evidence"]["timeout"]["status"], 504)
            self.assertEqual(data["trials"][0][3]["evidence"]["duplicate"]["status"], 409)
            self.assertEqual(len(data["trials"][0][4]["evidence"]["successful"]), 10)

    def test_missing_request_log_is_not_a_pass(self):
        event = {"status": 200, "output": {}, "request_id": "id", "request_log": []}
        self.assertFalse(run_capstone_eval.valid_request_record(event))

    def test_missing_rejection_audit_is_not_a_pass(self):
        self.assertFalse(run_capstone_eval.rejected({"audit_log": []}, "rate_limited"))

    def test_unavailable_detector_does_not_pass_real_submission_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(config, "LOG_DIR", root),
                patch.object(config, "AUDIT_LOG", root / "audit.jsonl"),
                patch.object(config, "REQUEST_LOG", root / "requests.jsonl"),
                patch.object(
                    detector,
                    "model_signal",
                    side_effect=detector.DetectorUnavailable("test detector unavailable"),
                ),
                self.assertLogs("app", level="WARNING"),
            ):
                client = app.app.test_client()
                rate = run_capstone_eval.check_rate_limit(client, "unavailable-rate")
                logs = run_capstone_eval.check_request_logs(client, "unavailable-logs")
            self.assertFalse(rate["passed"])
            self.assertFalse(logs["passed"])
            self.assertIsNone(logs["mean_duration_ms"])


if __name__ == "__main__":
    unittest.main()
