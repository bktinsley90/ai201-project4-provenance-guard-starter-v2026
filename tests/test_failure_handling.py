import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import app
import config
import detector


class FailureHandlingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        log_dir = Path(self.temp_dir.name)
        self.log_dir_patch = patch.object(config, "LOG_DIR", log_dir)
        self.audit_log_patch = patch.object(config, "AUDIT_LOG", log_dir / "audit.jsonl")
        self.log_dir_patch.start()
        self.audit_log_patch.start()
        self.client = app.app.test_client()

    def tearDown(self):
        self.audit_log_patch.stop()
        self.log_dir_patch.stop()
        self.temp_dir.cleanup()

    def submit(self, creator_id="failure-test", text="A valid three word submission"):
        return self.client.post(
            "/submit",
            json={"creator_id": creator_id, "text": text},
        )

    def entries(self):
        return [
            json.loads(line)
            for line in config.AUDIT_LOG.read_text(encoding="utf-8").splitlines()
        ] if config.AUDIT_LOG.exists() else []

    def test_invalid_and_oversized_submissions_are_rejected_and_logged(self):
        with patch.object(app.detector, "model_signal") as model_signal:
            invalid = self.client.post("/submit", json={"text": "  "})
            oversized = self.submit(
                creator_id="large-input",
                text="word " * (config.MAX_TEXT_LENGTH // 5 + 2),
            )

        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(oversized.status_code, 413)
        model_signal.assert_not_called()
        self.assertEqual(
            [entry["reason"] for entry in self.entries()],
            ["invalid_request", "text_too_large"],
        )

    def test_oversized_request_body_is_rejected_and_logged(self):
        response = self.client.post(
            "/submit",
            data=b'{"text":"' + b"x" * config.MAX_REQUEST_BYTES + b'"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.get_json()["error"], "request_too_large")
        self.assertEqual(self.entries()[0]["reason"], "request_too_large")

    def test_rate_limit_returns_json_and_audits_rejection(self):
        creator_id = f"rate-limit-{time.time_ns()}"
        with (
            patch.object(app.detector, "model_signal", return_value=0.2),
            patch.object(app.stylometry, "style_signal", return_value=0.3),
        ):
            responses = [self.submit(creator_id=creator_id) for _ in range(11)]

        self.assertEqual([response.status_code for response in responses[:10]], [200] * 10)
        self.assertEqual(responses[10].status_code, 429)
        self.assertEqual(responses[10].get_json()["error"], "rate_limited")
        self.assertTrue(any(
            entry.get("reason") == "rate_limited" and entry["creator_id"] == creator_id
            for entry in self.entries()
        ))

    def test_detector_failure_returns_service_error_without_a_decision(self):
        with (
            patch.object(app.detector, "model_signal", side_effect=RuntimeError("model failed")),
            self.assertLogs("app", level="ERROR"),
        ):
            response = self.submit(creator_id="model-failure")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "detector_failed")
        entries = self.entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["reason"], "detector_failed")
        self.assertEqual(entries[0]["error_type"], "RuntimeError")
        self.assertNotEqual(entries[0]["status"], "decided")

    def test_unavailable_detector_returns_explicit_service_error(self):
        with patch.object(
            app.detector,
            "model_signal",
            side_effect=detector.DetectorUnavailable("model is not installed"),
        ):
            response = self.submit(creator_id="model-unavailable")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "detector_unavailable")
        self.assertEqual(self.entries()[0]["reason"], "detector_unavailable")

    def test_style_signal_failure_returns_service_error_without_a_decision(self):
        with (
            patch.object(app.detector, "model_signal", return_value=0.2),
            patch.object(
                app.stylometry,
                "style_signal",
                side_effect=RuntimeError("style signal failed"),
            ),
            self.assertLogs("app", level="ERROR"),
        ):
            response = self.submit(creator_id="style-failure")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "style_signal_failed")
        entry = self.entries()[0]
        self.assertEqual(entry["reason"], "style_signal_failed")
        self.assertEqual(entry["status"], "rejected")

    def test_detector_timeout_and_busy_state_are_audited(self):
        release_detector = threading.Event()
        detector_started = threading.Event()

        def slow_detector(_text):
            self.assertTrue(_text)
            detector_started.set()
            release_detector.wait(timeout=2)
            return 0.2

        with (
            patch.object(config, "DETECTOR_TIMEOUT_SECONDS", 0.02),
            patch.object(app.detector, "model_signal", side_effect=slow_detector),
        ):
            timed_out = self.submit(creator_id="slow-detector")
            self.assertTrue(detector_started.wait(timeout=1))
            busy = self.submit(creator_id="busy-detector")
            release_detector.set()
            app._detector_future.result(timeout=1)

        self.assertEqual(timed_out.status_code, 504)
        self.assertEqual(timed_out.get_json()["error"], "detector_timeout")
        self.assertEqual(busy.status_code, 503)
        self.assertEqual(busy.get_json()["error"], "detector_busy")
        self.assertEqual(
            [entry["reason"] for entry in self.entries()],
            ["detector_timeout", "detector_busy"],
        )
        self.assertTrue(all(entry["status"] == "rejected" for entry in self.entries()))

    def test_appeal_is_recorded_once_and_duplicate_is_rejected(self):
        with (
            patch.object(app.detector, "model_signal", return_value=0.2),
            patch.object(app.stylometry, "style_signal", return_value=0.3),
        ):
            submission = self.submit(creator_id="appeal-writer")

        content_id = submission.get_json()["content_id"]
        appeal_payload = {
            "content_id": content_id,
            "reasoning": "I wrote this and would like a review.",
        }
        first = self.client.post("/appeal", json=appeal_payload)
        duplicate = self.client.post("/appeal", json=appeal_payload)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["status"], "under_review")
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.get_json()["error"], "already_under_review")
        entries = self.entries()
        self.assertEqual(sum(entry.get("event") == "appeal" for entry in entries), 1)
        self.assertEqual(entries[-1]["reason"], "duplicate_appeal")

    def test_invalid_and_unknown_appeals_are_audited(self):
        invalid = self.client.post("/appeal", json={"content_id": "missing-reason"})
        unknown = self.client.post(
            "/appeal",
            json={"content_id": "not-a-submission", "reasoning": "Please review."},
        )
        oversized = self.client.post(
            "/appeal",
            json={
                "content_id": "oversized-reason",
                "reasoning": "x" * (config.MAX_APPEAL_REASONING_LENGTH + 1),
            },
        )

        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(oversized.status_code, 413)
        self.assertEqual(
            [entry["reason"] for entry in self.entries()],
            ["invalid_appeal", "appeal_not_found", "appeal_reasoning_too_large"],
        )

    def test_concurrent_duplicate_appeals_create_only_one_review_event(self):
        with (
            patch.object(app.detector, "model_signal", return_value=0.2),
            patch.object(app.stylometry, "style_signal", return_value=0.3),
        ):
            submission = self.submit(creator_id="concurrent-appeal-writer")
        content_id = submission.get_json()["content_id"]
        payload = {"content_id": content_id, "reasoning": "Please review this."}

        def send_appeal():
            with app.app.test_client() as client:
                return client.post("/appeal", json=payload).status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(send_appeal) for _ in range(2)]
            statuses = [future.result() for future in futures]

        self.assertCountEqual(statuses, [200, 409])
        self.assertEqual(
            sum(entry.get("event") == "appeal" for entry in self.entries()),
            1,
        )


if __name__ == "__main__":
    unittest.main()
