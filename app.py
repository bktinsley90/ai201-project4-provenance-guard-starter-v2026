#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        worked example
    POST /submit      score text, with validation, rate limits, and failure handling
    POST /appeal      record an appeal for a completed decision
    GET  /log         inspect the audit log
    GET  /health      check the service and detector status
"""

import logging
import threading
import time
import uuid
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    TimeoutError as FutureTimeoutError,
)

from datetime import datetime, timezone

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

import audit
import config
import detector
import request_log
import scoring
import stylometry

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_REQUEST_BYTES

_logger = logging.getLogger(__name__)
_detector_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="detector")
_detector_lock = threading.Lock()
_detector_future: Future[float] | None = None
_appeal_lock = threading.Lock()


def _request_input() -> object:
    if not request.is_json:
        return {
            "content_type": request.content_type,
            "content_length": request.content_length,
        }
    try:
        return request.get_json(silent=True)
    except RequestEntityTooLarge:
        return {
            "unavailable": "request_too_large",
            "content_length": request.content_length,
        }


@app.before_request
def start_request_record():
    g.request_id = str(uuid.uuid4())
    g.request_started_ns = time.perf_counter_ns()
    g.request_input = _request_input()


@app.after_request
def write_request_record(response):
    started_ns = getattr(g, "request_started_ns", time.perf_counter_ns())
    request_input = getattr(g, "request_input", None)
    creator_id = (
        request_input.get("creator_id")
        if isinstance(request_input, dict)
        else None
    )
    output = (
        response.get_json(silent=True)
        if response.is_json
        else {
            "content_type": response.content_type,
            "body_bytes": response.calculate_content_length(),
        }
    )
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "request_id": getattr(g, "request_id", str(uuid.uuid4())),
        "method": request.method,
        "path": request.path,
        "endpoint": request.endpoint,
        "input": request_input,
        "output": output,
        "status_code": response.status_code,
        "duration_ms": round((time.perf_counter_ns() - started_ns) / 1_000_000, 3),
        "creator_id": creator_id,
    }
    if isinstance(output, dict) and output.get("content_id"):
        record["content_id"] = output["content_id"]
    response.headers["X-Request-ID"] = record["request_id"]
    try:
        request_log.append_record(config.REQUEST_LOG, record)
    except OSError:
        _logger.exception(
            "Could not write structured request log for request_id=%s",
            record["request_id"],
        )
    return response


class DetectorBusyError(RuntimeError):
    """A previous detector call is still running after its request timed out."""


class DetectorTimeoutError(TimeoutError):
    """The detector did not finish before the configured request deadline."""


class DetectorExecutionError(RuntimeError):
    """The detector raised an exception while scoring a submission."""

    def __init__(self, cause: Exception):
        super().__init__(str(cause))
        self.cause = cause


def _run_detector(text: str) -> float:
    try:
        return detector.model_signal(text)
    except Exception as exc:
        raise DetectorExecutionError(exc) from exc


def _log_late_detector_failure(future: Future[float]) -> None:
    try:
        future.result()
    except DetectorExecutionError:
        _logger.exception("Detector failed after its request timed out")


def _model_score_with_timeout(text: str) -> float:
    global _detector_future

    with _detector_lock:
        if _detector_future is not None and not _detector_future.done():
            raise DetectorBusyError("A previous detector request is still running.")
        future = _detector_executor.submit(_run_detector, text)
        _detector_future = future

    try:
        return future.result(timeout=config.DETECTOR_TIMEOUT_SECONDS)
    except FutureTimeoutError as exc:
        future.add_done_callback(_log_late_detector_failure)
        raise DetectorTimeoutError from exc
    finally:
        if future.done():
            with _detector_lock:
                if _detector_future is future:
                    _detector_future = None


def _json_object_from_request() -> dict | None:
    try:
        payload = request.get_json(silent=True)
    except RequestEntityTooLarge:
        return None
    return payload if isinstance(payload, dict) else None


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Rate limiting can be disabled with RATE_LIMITING_ENABLED=False in config.py.
# When enabled, /submit is limited per creator_id, falling back to caller IP.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Count valid creator IDs separately and fall back to the caller address.
        """
        payload = _json_object_from_request()
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if payload is None:
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = _json_object_from_request() or {}
        creator_id = payload.get("creator_id")
        if not isinstance(creator_id, str) or not creator_id.strip():
            creator_id = "unknown"
        audit.log_rejection(
            creator_id=creator_id,
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


@app.errorhandler(413)
def request_too_large(exc):
    audit.log_rejection(
        creator_id="unknown",
        reason="request_too_large",
        max_request_bytes=config.MAX_REQUEST_BYTES,
        http_status=exc.code,
    )
    return jsonify({
        "error": "request_too_large",
        "message": f"Request body must not exceed {config.MAX_REQUEST_BYTES} bytes.",
    }), 413


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── Submission route ──────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, and answer.

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
         "model_score": 0.0, "style_score": 0.0, "combined_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next unit's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
      1. Return a hardcoded response. Confirm `curl` gets it back before you
         add any logic at all.
      2. Then pull `text` and `creator_id` out of the payload.
      3. Then call ONE signal — `detector.model_signal(text)` — and put the
         real number in. Leave confidence and label as placeholders.
      4. Log every submission with `audit.log_decision(...)`. The content_id
         matters: `/appeal` needs it, and a student who skips it rebuilds this
         whole flow later.

    **Milestone 4 — the second signal and the score.**
      5. Add `stylometry.style_signal(text)`.
      6. Combine them with `scoring.combine_signals(...)`.
      7. Log BOTH signal scores alongside the combined one, and put them in the
         response too. Next unit you can't diagnose anything without them.

    **Milestone 5 — the label.**
      8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Invalid request bodies and text are rejected before either signal runs.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        audit.log_rejection(
            creator_id="unknown",
            reason="invalid_request",
            field="body",
        )
        return jsonify({
            "error": "invalid_request",
            "message": "Request body must be a JSON object.",
        }), 400

    creator_id = payload.get("creator_id", "unknown")
    audit_creator_id = (
        creator_id if isinstance(creator_id, str) and creator_id.strip()
        else "unknown"
    )
    if not isinstance(creator_id, str) or not creator_id.strip():
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="invalid_request",
            field="creator_id",
        )
        return jsonify({
            "error": "invalid_request",
            "message": "creator_id must be a non-empty string when provided.",
        }), 400

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="invalid_request",
            field="text",
        )
        return jsonify({
            "error": "invalid_request",
            "message": "text must be a non-empty string.",
        }), 400
    if len(text.split()) < 3:
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="invalid_request",
            field="text",
        )
        return jsonify({
            "error": "invalid_request",
            "message": "text must contain at least three words to score.",
        }), 400
    if len(text) > config.MAX_TEXT_LENGTH:
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="text_too_large",
            text_length=len(text),
            max_text_length=config.MAX_TEXT_LENGTH,
        )
        return jsonify({
            "error": "text_too_large",
            "message": f"text must not exceed {config.MAX_TEXT_LENGTH} characters.",
        }), 413

    content_id = str(uuid.uuid4())
    try:
        model_score = _model_score_with_timeout(text)
    except DetectorBusyError:
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="detector_busy",
            content_id=content_id,
        )
        return jsonify({
            "error": "detector_busy",
            "message": "The detector is still processing another request. Try again shortly.",
        }), 503
    except DetectorTimeoutError:
        _logger.warning(
            "Detector timed out for content_id=%s after %s seconds",
            content_id,
            config.DETECTOR_TIMEOUT_SECONDS,
        )
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="detector_timeout",
            content_id=content_id,
            timeout_seconds=config.DETECTOR_TIMEOUT_SECONDS,
        )
        return jsonify({
            "error": "detector_timeout",
            "message": "The detector did not finish in time. Please try again.",
        }), 504
    except DetectorExecutionError as exc:
        if isinstance(exc.cause, detector.DetectorUnavailable):
            _logger.warning(
                "Detector unavailable for content_id=%s: %s",
                content_id,
                exc.cause,
            )
            error = "detector_unavailable"
            message = "The detector is unavailable. Please try again later."
        else:
            _logger.exception("Detector failed for content_id=%s", content_id)
            error = "detector_failed"
            message = "The detector could not score this submission. Please try again."
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason=error,
            content_id=content_id,
            error_type=type(exc.cause).__name__,
        )
        return jsonify({"error": error, "message": message}), 503

    try:
        style_score = stylometry.style_signal(text)
    except Exception as exc:
        _logger.exception("Style signal failed for content_id=%s", content_id)
        audit.log_rejection(
            creator_id=audit_creator_id,
            reason="style_signal_failed",
            content_id=content_id,
            error_type=type(exc).__name__,
        )
        return jsonify({
            "error": "style_signal_failed",
            "message": "The detector could not score this submission. Please try again.",
        }), 503

    combined_score = scoring.combine_signals(model_score, style_score)
    guess, label = scoring.score_to_label(combined_score)

    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        status="decided",
    )

    return jsonify({
        "content_id": content_id,
        "guess": guess,
        "confidence": 0.0,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        "combined_score": combined_score,
    })


@app.post("/appeal")
def appeal():
    """
    Record one appeal for a completed decision.

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}

    Invalid, unknown, oversized, and duplicate appeals are rejected and logged.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        audit.log_rejection(
            creator_id="unknown",
            reason="invalid_appeal",
            field="body",
        )
        return jsonify({
            "error": "invalid_request",
            "message": "Request body must be a JSON object.",
        }), 400

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")
    if not isinstance(content_id, str) or not content_id.strip():
        audit.log_rejection(
            creator_id="unknown",
            reason="invalid_appeal",
            field="content_id",
        )
        return jsonify({
            "error": "invalid_request",
            "message": "A non-empty content_id is required.",
        }), 400
    if not isinstance(reasoning, str) or not reasoning.strip():
        audit.log_rejection(
            creator_id="unknown",
            reason="invalid_appeal",
            field="reasoning",
            content_id=content_id,
        )
        return jsonify({
            "error": "invalid_request",
            "message": "Non-empty reasoning is required.",
        }), 400
    if len(reasoning) > config.MAX_APPEAL_REASONING_LENGTH:
        audit.log_rejection(
            creator_id="unknown",
            reason="appeal_reasoning_too_large",
            content_id=content_id,
            reasoning_length=len(reasoning),
            max_reasoning_length=config.MAX_APPEAL_REASONING_LENGTH,
        )
        return jsonify({
            "error": "appeal_reasoning_too_large",
            "message": (
                "reasoning must not exceed "
                f"{config.MAX_APPEAL_REASONING_LENGTH} characters."
            ),
        }), 413

    with _appeal_lock:
        entries = audit.entries_for(content_id)
        decisions = [
            entry for entry in entries
            if entry.get("status") == "decided"
        ]
        if not decisions:
            audit.log_rejection(
                creator_id="unknown",
                reason="appeal_not_found",
                content_id=content_id,
            )
            return jsonify({
                "error": "not_found",
                "message": "No submission found for that content_id.",
            }), 404

        creator_id = decisions[0].get("creator_id", "unknown")
        if any(entry.get("event") == "appeal" for entry in entries):
            audit.log_rejection(
                creator_id=creator_id,
                reason="duplicate_appeal",
                content_id=content_id,
            )
            return jsonify({
                "error": "already_under_review",
                "message": "An appeal for this submission has already been recorded.",
            }), 409

        appeal_entry = audit.log_appeal(
            content_id=content_id,
            creator_id=creator_id,
            reasoning=reasoning.strip(),
        )
    return jsonify({
        "ok": True,
        "content_id": content_id,
        "status": appeal_entry["status"],
        "message": "Your appeal has been recorded for review.",
    })


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'OFF'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
