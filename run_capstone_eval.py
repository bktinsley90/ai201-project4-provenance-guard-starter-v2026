#!/usr/bin/env python3
"""Evaluate the five capstone criteria in three isolated local trials."""

import json
import statistics
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import app as service
import config
import detector

TEXT = "Rain crossed the street. I waited beside the old station."
REASON = "Please review my writing and the original decision."
CRITERIA = (
    "Invalid and oversized submissions",
    "Rate-limit boundary",
    "Detector failure and timeout",
    "Appeal handling",
    "Structured request logs",
)
TARGETS = (
    "6/6 invalid requests rejected and audited; no decisions",
    "10 successful requests then 429 and rejection audit within one minute",
    "503 failure, 504 timeout, 503 busy; all audited without decisions",
    "3/3 appeals recorded; duplicate returns 409 and is audited",
    "10 successful and 1 rejected request logged; calculate success average",
)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def send(client, endpoint: str, *, payload=None, data=None) -> dict:
    """Capture a response and exactly the log entries appended by that request."""
    audit_before = len(read_jsonl(config.AUDIT_LOG))
    requests_before = len(read_jsonl(config.REQUEST_LOG))
    if data is not None:
        response = client.post(endpoint, data=data, content_type="application/json")
    else:
        response = client.post(endpoint, json=payload)
    return {
        "status": response.status_code,
        "output": response.get_json(silent=True),
        "request_id": response.headers.get("X-Request-ID"),
        "request_log": read_jsonl(config.REQUEST_LOG)[requests_before:],
        "audit_log": read_jsonl(config.AUDIT_LOG)[audit_before:],
    }


def rejected(event: dict, reason: str) -> bool:
    entries = event["audit_log"]
    return (
        len(entries) == 1
        and entries[0].get("event") == "rejected"
        and entries[0].get("status") == "rejected"
        and entries[0].get("reason") == reason
        and all(entry.get("status") != "decided" for entry in entries)
    )


def has_json_error(event: dict, code: int, reason: str) -> bool:
    return (
        event["status"] == code
        and isinstance(event["output"], dict)
        and event["output"].get("error") == reason
    )


def check_invalid(client, prefix: str) -> dict:
    cases = [
        ("missing", {"creator_id": f"{prefix}-missing"}, "invalid_request"),
        ("empty", {"creator_id": f"{prefix}-empty", "text": ""}, "invalid_request"),
        ("null", {"creator_id": f"{prefix}-null", "text": None}, "invalid_request"),
        ("non_string", {"creator_id": f"{prefix}-number", "text": 123}, "invalid_request"),
        (
            "oversized_text",
            {"creator_id": f"{prefix}-large", "text": "word " * 2001},
            "text_too_large",
        ),
    ]
    events = []
    for name, payload, reason in cases:
        event = send(client, "/submit", payload=payload)
        event["case"] = name
        event["passed"] = (
            400 <= event["status"] < 500
            and has_json_error(event, event["status"], reason)
            and rejected(event, reason)
        )
        events.append(event)
    oversized_body = b'{"text":"' + b"x" * 64000 + b'"}'
    event = send(client, "/submit", data=oversized_body)
    event["case"] = "oversized_body"
    event["passed"] = (
        has_json_error(event, 413, "request_too_large")
        and rejected(event, "request_too_large")
    )
    events.append(event)
    count = sum(event["passed"] for event in events)
    return {"passed": count == 6, "summary": f"{count}/6", "evidence": events}


def check_rate_limit(client, prefix: str) -> dict:
    creator_id = f"{prefix}-rate"
    started = time.monotonic()
    events = [
        send(client, "/submit", payload={"creator_id": creator_id, "text": TEXT})
        for _ in range(11)
    ]
    elapsed = time.monotonic() - started
    statuses = [event["status"] for event in events]
    last = events[-1]
    passed = (
        config.RATE_LIMITING_ENABLED
        and elapsed < 60
        and statuses == [200] * 10 + [429]
        and has_json_error(last, 429, "rate_limited")
        and rejected(last, "rate_limited")
    )
    return {
        "passed": passed,
        "summary": f"statuses {statuses}; {elapsed:.3f}s",
        "elapsed_seconds": elapsed,
        "evidence": events,
    }


def check_detector_failures(client, prefix: str) -> dict:
    with patch.object(detector, "model_signal", side_effect=RuntimeError("injected failure")):
        failure = send(client, "/submit", payload={"creator_id": f"{prefix}-failure", "text": TEXT})

    started = threading.Event()
    release = threading.Event()

    def blocked_detector(_text):
        started.set()
        if not release.wait(timeout=10):
            raise RuntimeError("Injected detector was not released within 10 seconds")
        return 0.2

    with (
        patch.object(config, "DETECTOR_TIMEOUT_SECONDS", 0.1),
        patch.object(detector, "model_signal", side_effect=blocked_detector),
    ):
        try:
            timeout = send(client, "/submit", payload={"creator_id": f"{prefix}-timeout", "text": TEXT})
            worker_started = started.wait(timeout=1)
            busy = send(client, "/submit", payload={"creator_id": f"{prefix}-busy", "text": TEXT})
        finally:
            release.set()
            future = service._detector_future
            if started.is_set() and future is not None:
                future.result(timeout=5)

    checks = [
        has_json_error(failure, 503, "detector_failed") and rejected(failure, "detector_failed"),
        worker_started and has_json_error(timeout, 504, "detector_timeout") and rejected(timeout, "detector_timeout"),
        has_json_error(busy, 503, "detector_busy") and rejected(busy, "detector_busy"),
    ]
    return {
        "passed": all(checks),
        "summary": f"failure/timeout/busy: {failure['status']}/{timeout['status']}/{busy['status']}",
        "checks": checks,
        "evidence": {"failure": failure, "timeout": timeout, "busy": busy},
    }


def check_appeals(client, prefix: str) -> dict:
    cases = []
    for index in range(3):
        creator_id = f"{prefix}-appeal-{index}"
        submission = send(client, "/submit", payload={"creator_id": creator_id, "text": TEXT})
        output = submission["output"]
        content_id = output.get("content_id") if isinstance(output, dict) else None
        if not isinstance(content_id, str):
            cases.append({"submission": submission, "appeal": None, "passed": False})
            continue
        appeal = send(client, "/appeal", payload={"content_id": content_id, "reasoning": REASON})
        decisions = [
            row for row in read_jsonl(config.AUDIT_LOG)
            if row.get("content_id") == content_id and row.get("status") == "decided"
        ]
        entries = appeal["audit_log"]
        appeal_output = appeal["output"]
        passed = (
            submission["status"] == 200
            and len(decisions) == 1
            and appeal["status"] == 200
            and isinstance(appeal_output, dict)
            and appeal_output.get("status") == "under_review"
            and appeal_output.get("content_id") == content_id
            and len(entries) == 1
            and entries[0].get("event") == "appeal"
            and entries[0].get("status") == "under_review"
            and entries[0].get("content_id") == content_id
            and entries[0].get("reasoning") == REASON
        )
        cases.append({"submission": submission, "appeal": appeal, "passed": passed})

    first = cases[0]["submission"]["output"]
    first_id = first.get("content_id") if isinstance(first, dict) else None
    duplicate = None
    duplicate_passed = False
    if isinstance(first_id, str):
        duplicate = send(client, "/appeal", payload={"content_id": first_id, "reasoning": REASON})
        appeal_events = [
            row for row in read_jsonl(config.AUDIT_LOG)
            if row.get("content_id") == first_id and row.get("event") == "appeal"
        ]
        duplicate_passed = (
            has_json_error(duplicate, 409, "already_under_review")
            and rejected(duplicate, "duplicate_appeal")
            and len(appeal_events) == 1
        )
    count = sum(case["passed"] for case in cases)
    return {
        "passed": count == 3 and duplicate_passed,
        "summary": f"{count}/3 appeals; duplicate {'passed' if duplicate_passed else 'failed'}",
        "evidence": {"cases": cases, "duplicate": duplicate},
    }


def valid_request_record(event: dict) -> bool:
    records = event["request_log"]
    if len(records) != 1:
        return False
    record = records[0]
    duration = record.get("duration_ms")
    return (
        isinstance(record.get("timestamp"), str)
        and "input" in record
        and record.get("output") == event["output"]
        and record.get("status_code") == event["status"]
        and record.get("request_id") == event["request_id"]
        and isinstance(duration, (int, float))
        and not isinstance(duration, bool)
        and duration >= 0
    )


def check_request_logs(client, prefix: str) -> dict:
    events = [
        send(client, "/submit", payload={"creator_id": f"{prefix}-log-{index}", "text": TEXT})
        for index in range(10)
    ]
    failure = send(client, "/submit", payload={"creator_id": f"{prefix}-log-invalid", "text": ""})
    checked = [
        event["status"] == 200 and valid_request_record(event)
        for event in events
    ]
    checked.append(has_json_error(failure, 400, "invalid_request") and valid_request_record(failure))
    durations = [
        event["request_log"][0]["duration_ms"]
        for event in events
        if event["status"] == 200 and valid_request_record(event)
    ]
    mean = statistics.mean(durations) if len(durations) == 10 else None
    count = sum(checked)
    return {
        "passed": all(checked) and mean is not None,
        "summary": f"{count}/11 records; mean {mean:.3f} ms" if mean is not None else f"{count}/11 records; mean unavailable",
        "mean_duration_ms": mean,
        "evidence": {"successful": events, "rejected": failure},
    }


def evaluate_trial(client, trial: int) -> list[dict]:
    prefix = f"capstone-{uuid.uuid4().hex}-trial{trial}"
    checks = [
        check_invalid(client, prefix),
        check_rate_limit(client, prefix),
        check_detector_failures(client, prefix),
        check_appeals(client, prefix),
        check_request_logs(client, prefix),
    ]
    return checks


def write_results(trials: list[list[dict]]) -> tuple[Path, Path, bool]:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S_%f")
    base = config.RESULTS_DIR / f"capstone_{stamp}_{uuid.uuid4().hex[:8]}"
    json_path = base.with_suffix(".json")
    report_path = base.with_suffix(".md")
    all_passed = all(check["passed"] for trial in trials for check in trial)
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Flask in-process test client; real detector except injected failure and timeout",
        "trial_count": len(trials),
        "criteria": list(CRITERIA),
        "trials": trials,
        "all_passed": all_passed,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Capstone evaluation",
        "",
        f"Created: {payload['created_utc']}",
        "",
        "Three independent trials use the Flask test client and isolated temporary logs.",
        "The real detector is used except for injected failure and timeout cases.",
        f"Full responses and structured log evidence: [{json_path.name}]({json_path.name}).",
        "",
        "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
        "|---|---|---|---|---|---|",
    ]
    for index, name in enumerate(CRITERIA):
        results = [trial[index] for trial in trials]
        cells = [f"{'PASS' if item['passed'] else 'FAIL'}: {item['summary']}" for item in results]
        verdict = "MET" if all(item["passed"] for item in results) else "MISSED"
        lines.append(f"| {index + 1}. {name} | {TARGETS[index]} | {' | '.join(cells)} | {verdict} |")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path, json_path, all_passed


def main() -> int:
    print("Running three capstone trials with isolated logs. No server is required.", flush=True)
    print("Detector error and timeout messages are expected: those failures are injected.", flush=True)
    with tempfile.TemporaryDirectory(prefix="provenance-capstone-") as directory:
        log_dir = Path(directory)
        with (
            patch.object(config, "LOG_DIR", log_dir),
            patch.object(config, "AUDIT_LOG", log_dir / "audit.jsonl"),
            patch.object(config, "REQUEST_LOG", log_dir / "requests.jsonl"),
        ):
            client = service.app.test_client()
            trials = []
            for number in range(1, 4):
                print(f"Running trial {number}/3...", flush=True)
                trials.append(evaluate_trial(client, number))
            report_path, json_path, passed = write_results(trials)
    print(f"Summary: {report_path}")
    print(f"Responses and logs: {json_path}")
    print("Overall: " + ("MET" if passed else "MISSED; inspect the saved evidence"))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
