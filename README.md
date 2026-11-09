# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

1. A writer sends `text` and `creator_id` as JSON to `POST /submit`.
2. The service assigns a unique `content_id` so this submission can be found
   later if the writer appeals.
3. The model signal measures how predictable the text is to GPT-2; the style
   signal measures sentence-length variation, vocabulary repetition, and
   punctuation density.
4. `scoring.py::combine_signals` calculates the equal-weight average of those
   two 0–1 scores.
5. `scoring.py::score_to_label` maps the combined score to human (0.00–0.35),
   unsure (above 0.35 and below 0.65), or AI (0.65–1.00).
6. The service appends the scores, label, content ID, creator ID, and
   `decided` status to `logs/audit.jsonl`, then returns the result as JSON.
7. If the writer appeals, `POST /appeal` checks the content ID, records their
   reasoning as a new `under_review` event beside the original decision, and
   confirms the appeal. `GET /log` lets someone inspect the audit trail.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** GPT-2's perplexity for the text: how predictable each
next token is to the model. The detector maps perplexity to a 0–1 score, with
lower perplexity producing a higher score (more AI-like). In this project,
perplexity 45 maps to 0.5; the calculation uses text truncated to at most 400
tokens.

**Why that might differ between human and AI writing:** Language models tend
to produce likely, conventional next words, so generated text may be easier
for GPT-2 to predict. Human writing can include unexpected details, unusual
word choices, and abrupt shifts that raise perplexity.

**What it can't see:** Predictability does not prove who wrote a passage.
Plain, conventional writing—including writing by a second-language learner or
someone choosing simple wording—can look AI-like, while unusual or ornate
generated text can look human-like. The score also does not understand meaning
or authorship, and text beyond the 400-token limit is not considered.

### Signal two — the style signal

**What it measures:** It equally averages sentence regularity, vocabulary
repetition, and punctuation density. Sentence regularity is
`1 / (1 + sentence_length_spread)`; vocabulary repetition is
`1 - type_token_ratio`; punctuation density is used as measured. Each feature
is on a 0-to-1 scale, and higher values are treated as more AI-like. If a
measure is unavailable because there are no words or fewer than two
sentences, that feature contributes a neutral 0.5.

**Why that might differ between human and AI writing:** This heuristic treats
even sentence lengths and repeated vocabulary as more machine-like. It also
assumes denser punctuation is more machine-like; punctuation density alone
does not establish authorship.

**What it can't see:** It cannot understand meaning or distinguish deliberate
style from authorship. Vocabulary ratio depends on text length, and short
samples provide little sentence-length evidence. Editing punctuation or
sentence breaks can also change the score without changing who wrote the text.

### The combining rule

**The rule:** I use a weighted average of the model and style scores. When
they disagree, the average moves toward the unsure band; a split of 0.90 and
0.10 produces 0.50, which is unsure rather than an accusation.

**The numbers:** model weight 0.50, style weight 0.50. The high-confidence
human threshold is 0.35 and the high-confidence AI threshold is 0.65; scores
between them are unsure.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:** If the
model signal is 0.90 and the style signal is 0.10, the equal-weight average is
0.50, so the result is unsure. This favors avoiding a false accusation when
the signals conflict, while accepting that some AI writing may also land in
the unsure band.



---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00–0.35, inclusive | This text appears more consistent with human writing, though this assessment can be wrong. |
| unsure | Greater than 0.35 and less than 0.65 | We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation. |
| high-confidence AI | 0.65–1.00, inclusive | This text appears more consistent with AI-generated writing, though this assessment can be wrong. |

**Label reachability check:** Each text below was submitted to `POST /submit`
on the local service. These examples reached all three labels with the current
model and thresholds.

| Returned label | Submitted text | Combined score |
|---|---|---:|
| human | No. I walked home past the shuttered bakery, carrying a jar of buttons for my neighbor, whose old sewing machine has been making a noise like a pigeon trapped inside a cupboard. | 0.2419 |
| unsure | The history of a city can be read in its streets, buildings, and public spaces. Each generation leaves traces of its needs and ambitions. Looking closely at these details helps explain how communities change over time. | 0.4690 |
| ai | The system works well. It handles most cases correctly and provides good results. Users generally find it easy to use and understand. The system works well. It handles most cases correctly and provides good results. Users generally find it easy to use and understand. | 0.6965 |

**Why I worded the "unsure" one this way:**

I say we can't reliably tell instead of calling it suspicious, because the
score is uncertain and a writer should not be treated as guilty based on it.

---

## Sample Run
**A submission**

Port 5000 was already in use during this run, so the service was started on
port 5001.

```bash
$ curl -X POST http://127.0.0.1:5001/submit \
  -H "Content-Type: application/json" \
  -d '{"text":"The history of a city can be read in its streets, buildings, and public spaces. Each generation leaves traces of its needs and ambitions. Looking closely at these details helps explain how communities change over time.","creator_id":"sample-unsure"}'
```

```json
{
  "combined_score": 0.46899485219164117,
  "confidence": 0.0,
  "content_id": "d9941a02-6f08-497b-a374-02cac9f1ece4",
  "guess": "unsure",
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "model_score": 0.6359,
  "style_score": 0.30208970438328236
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5001/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id":"d9941a02-6f08-497b-a374-02cac9f1ece4","reasoning":"I am appealing this result. I have my drafts and version history showing how I wrote this submission."}'
```

```json
{
  "content_id": "d9941a02-6f08-497b-a374-02cac9f1ece4",
  "message": "Your appeal has been recorded for review.",
  "ok": true,
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5001/log?limit=5"
```

```json
{
  "count": 4,
  "entries": [
    {
      "combined_score": 0.24185063209665225,
      "content_id": "4e0afba1-efda-448e-a033-f7462973147f",
      "creator_id": "sample-human",
      "guess": "human",
      "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
      "model_score": 0.3016,
      "status": "decided",
      "style_score": 0.18210126419330455,
      "timestamp": "2026-11-01T00:17:03+00:00"
    },
    {
      "combined_score": 0.46899485219164117,
      "content_id": "d9941a02-6f08-497b-a374-02cac9f1ece4",
      "creator_id": "sample-unsure",
      "guess": "unsure",
      "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
      "model_score": 0.6359,
      "status": "decided",
      "style_score": 0.30208970438328236,
      "timestamp": "2026-11-01T00:17:03+00:00"
    },
    {
      "combined_score": 0.6965204205688842,
      "content_id": "c1867a96-ca45-4ee2-93a5-3fac5a24252b",
      "creator_id": "sample-ai",
      "guess": "ai",
      "label": "This text appears more consistent with AI-generated writing, though this assessment can be wrong.",
      "model_score": 0.9572,
      "status": "decided",
      "style_score": 0.4358408411377684,
      "timestamp": "2026-11-01T00:17:03+00:00"
    },
    {
      "content_id": "d9941a02-6f08-497b-a374-02cac9f1ece4",
      "creator_id": "sample-unsure",
      "event": "appeal",
      "reasoning": "I am appealing this result. I have my drafts and version history showing how I wrote this submission.",
      "status": "under_review",
      "timestamp": "2026-11-01T00:20:41+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* Help filling in `sentence_length_spread`,
  `type_token_ratio`, and `punctuation_density` in `stylometry.py`.
- *What came back:* Implementations based on normalized sentence-length
  variation, unique words divided by total words, and punctuation characters
  divided by total characters.
- *What I changed:* I handled short or empty inputs explicitly, counted
  Unicode punctuation, and used the three normalized measures to build the
  style score. I tested representative inputs and documented the limitations
  of these heuristics.

**Moment 2**

- *What I asked for:* Help writing the combining rule in
  `scoring.py::combine_signals` and deciding what should happen when the two
  signals disagree.
- *What came back:* An equal-weight average so conflicting scores move toward
  the unsure range instead of letting either signal dominate.
- *What I changed:* I kept weights configurable in `config.py`, normalized by
  their total in the implementation, and documented that a 0.90/0.10 split
  returns 0.50. I checked the rule with equal and unequal weights.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 per minute, 200 per day

**Why those numbers and not others:**
Ten submissions per minute leaves room for a writer to submit a few drafts or
revisions quickly, while stopping a burst of automated requests. The 200-per-day
limit allows sustained use throughout the day but makes it harder to probe the
detector with thousands of variations. I chose limits that protect against
abuse without making ordinary writing and revision impractical.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
15 submissions as 'flood_tester' against http://127.0.0.1:5000
The first one is slow while the model loads.

  [ 1/15] 200
  [ 2/15] 200
  [ 3/15] 200
  [ 4/15] 200
  [ 5/15] 200
  [ 6/15] 200
  [ 7/15] 200
  [ 8/15] 200
  [ 9/15] 200
  [10/15] 200
  [11/15] 429
  [12/15] 429
  [13/15] 429
  [14/15] 429
  [15/15] 429

============================================================
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
============================================================

5 of 15 were rate limited.
```

---

## Attack Run — Before

**Ten audit log entries from the run**

```json
{"timestamp":"2026-11-05T00:28:59+00:00","content_id":"26214fe3-f2c7-4593-b880-8aed8345c160","creator_id":"attacker_EV01","guess":"human","model_score":0.1635,"style_score":0.3358921737062701,"combined_score":0.24969608685313505,"label":"This text appears more consistent with human writing, though this assessment can be wrong.","status":"decided"}
{"timestamp":"2026-11-05T00:28:59+00:00","content_id":"9fb1690e-00ec-4483-8e74-f512fa55afa5","creator_id":"attacker_EV09","guess":"unsure","model_score":0.7042,"style_score":0.2860565924578427,"combined_score":0.4951282962289214,"label":"We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.","status":"decided"}
{"timestamp":"2026-11-05T00:29:00+00:00","content_id":"a7b1e011-3ae2-478d-9df2-aa0721366cbf","creator_id":"attacker_FP07","guess":"unsure","model_score":0.8816,"style_score":0.3823228073048668,"combined_score":0.6319614036524335,"label":"We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.","status":"decided"}
{"timestamp":"2026-11-05T00:29:00+00:00","content_id":"f545f88c-aec9-44d0-9102-825a2eaaf6bf","creator_id":"attacker_PI01","guess":"human","model_score":0.4625,"style_score":0.22791316602182565,"combined_score":0.34520658301091284,"label":"This text appears more consistent with human writing, though this assessment can be wrong.","status":"decided"}
{"timestamp":"2026-11-05T00:29:00+00:00","content_id":"c66e758b-6343-4333-bcc7-b9fde7e67b3a","creator_id":"attacker_PI05","guess":"unsure","model_score":0.6401,"style_score":0.2689509353104387,"combined_score":0.45452546765521934,"label":"We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.","status":"decided"}
{"timestamp":"2026-11-05T00:29:01+00:00","content_id":"5fc86eeb-fc0e-43ac-a57e-ff1080a572f6","creator_id":"attacker_MF06","guess":"ai","model_score":0.9969,"style_score":0.5,"combined_score":0.7484500000000001,"label":"This text appears more consistent with AI-generated writing, though this assessment can be wrong.","status":"decided"}
{"timestamp":"2026-11-05T00:29:01+00:00","content_id":"85746745-574b-4300-8280-60add932c800","creator_id":"attacker_MF07","guess":"ai","model_score":0.9064,"style_score":0.5,"combined_score":0.7032,"label":"This text appears more consistent with AI-generated writing, though this assessment can be wrong.","status":"decided"}
{"timestamp":"2026-11-05T00:29:01+00:00","content_id":"4511a670-2bde-40e6-97e3-554602c65505","creator_id":"attacker_MF08","guess":"ai","model_score":0.9876,"style_score":0.5709410766432871,"combined_score":0.7792705383216436,"label":"This text appears more consistent with AI-generated writing, though this assessment can be wrong.","status":"decided"}
{"timestamp":"2026-11-05T00:29:01+00:00","content_id":"d0c00572-ab24-4d9b-8224-05df2ce47f9c","creator_id":"attacker_flood","guess":"human","model_score":0.0287,"style_score":0.17272727272727273,"combined_score":0.10071363636363637,"label":"This text appears more consistent with human writing, though this assessment can be wrong.","status":"decided"}
{"timestamp":"2026-11-05T00:29:01+00:00","creator_id":"attacker_flood","event":"rejected","status":"rejected","reason":"rate_limited","limit":"10 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

The worst potential false positive is MF07: the submission was right-to-left
script, but the service returned `guess: "ai"` with a combined score of
`0.7032`. The test input alone does not establish that it was human-written,
but a legitimate submission in an RTL language could receive the same
accusation. FP07 is the strongest direct human-writing warning in the false
positive set: deliberately repeated phrasing scored `0.8816` on the model
signal, though the final result was `unsure` rather than an AI accusation.

---

## Run Log and Verdicts

<!-- Selected report: results/run_2026-11-08_1951_before.md -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Own writing | At most 1 of 10 gets the high-confidence AI label in each run | 10/10 returned 403; no labels | 10/10 returned 403; no labels | 10/10 returned 403; no labels | MISSED |
| 2. Score spread | AI-generated average is at least 0.15 above own-writing average | All 10 returned 403; no scores | All 10 returned 403; no scores | All 10 returned 403; no scores | MISSED |
| 3. Label coverage | Each run reaches human, unsure, and AI labels | 3/3 returned 403; no guesses | 3/3 returned 403; no guesses | 3/3 returned 403; no guesses | MISSED |
| 4. Appeal path | 3/3 appeals are logged and set status to `under_review` | Not tested by `run_eval.py` | Not tested by `run_eval.py` | Not tested by `run_eval.py` | MISSED |
| 5. Malformed input | All 4 cases return 4xx and create no detection decision | 4/4 returned 403; no decision records found | 4/4 returned 403; no decision records found | 4/4 returned 403; no decision records found | MET |

Selected report: `results/run_2026-11-08_1951_before.md`, produced by
`run_eval.py::main`. All 81 requests in this report returned 403, including
valid submissions. The run did not produce detector scores or guesses, so the
scoring criteria cannot be assessed from these results. The malformed cases
did receive 4xx responses; I also checked the audit log and found no decision
records for their evaluation creator IDs.

**Real output from one trial** — label coverage, Trial 1:

```json
[
  {
    "status": 403,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "Went for a run. Legs hurt. Worth it."
  },
  {
    "status": 403,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "We got to the campsite about four. The pitch was fine, a bit sloped, b"
  },
  {
    "status": 403,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "The importance of effective communication in the workplace cannot be o"
  }
]
```

**Diagnoses**

**Criterion verdicts**

1. **MISSED** — The target requires labels for the ten pieces in every run.
   All ten requests in each run returned 403, so none were scored and the
   false-positive rate cannot be measured. **Stage: route/request boundary.**
   **Mechanism:** requests were rejected before a decision was returned. The
   reports do not identify which component generated the 403, so I cannot
   diagnose that component more precisely.
2. **MISSED** — There were no model, style, or combined scores in any of the
   three runs, so the 0.15 average-score gap cannot be calculated.
   **Stage: route/request boundary; mechanism:** the same 403 rejection
   prevented the requests from reaching observable scoring output. This is not
   evidence that either signal failed.
3. **MISSED** — No run produced any guesses, so the three-label coverage target
   was not demonstrated. **Stage: route/request boundary; mechanism:** all
   three label-coverage requests were rejected with 403 before labels appeared.
4. **MISSED (not run)** — `run_eval.py` sends submissions only; it does not
   create and submit appeals. **Stage: evaluation harness, not one of the five
   service stages. Mechanism:** the runner has no appeal request flow, so no
   appeal trial was performed and there is no evidence about appeal routing,
   status changes, or audit logging.
5. **MET** — All four malformed cases returned 403 in each trial, and no
   matching evaluation decision records appear in the audit log. That meets
   the stated 4xx/no-decision target, though it does not show that the
   application itself handled or validated the malformed bodies.

**Attack-run diagnoses — 23 BROKE**

- **Nine evasion attacks (EV01–EV09):** **Stages: signal one, signal two, and
  the combining rule.** Five attacks manipulated surface style (typos, sentence
  breaks, a quotation, sentence-length extremes, or punctuation); their style
  scores were low and pulled the equal-weight combined score toward human or
  unsure. EV04's unusual vocabulary and EV08's very short text lowered the
  model score; EV05 changed both signals through editing. In EV09, the model
  score was 0.7042 but the style score was 0.2861, bringing the combined score
  to 0.4951 and the label to unsure. The shared mechanism is that edits can
  move one or both heuristic signals, and averaging them can erase an AI-like
  model score.
- **Three prompt-injection attempts (PI01–PI03):** **Stages: the signals and
  combining rule, followed by label mapping.** The instruction-like text was
  included in the text being scored; it was not independently authenticated
  or excluded. The resulting combined scores stayed below the AI threshold,
  yielding human for PI01/PI02 and unsure for PI03. These are text-scoring
  evasions rather than evidence of an instruction-following LLM being
  hijacked.
- **Eleven malformed-request attacks (MF02, RQ01, RQ03–RQ05, RQ07–RQ12):**
  **Primary stage: route; secondary failure: signal one.** The route passed
  missing, too-short, null, or non-string inputs through instead of rejecting
  them with a client error. The model/tokenizer then raised exceptions that
  escaped as 500 responses. RQ07 also shows the route assuming the decoded
  JSON root is an object and calling `.get` on a list. The common mechanism is
  missing request-shape/type validation and no conversion of these failures to
  a controlled 4xx response.

The evaluation blocker is the clearest shared problem: every request returned
403, including valid writing. The recorded reports do not establish which
component produced that response, so the next step is to identify and fix the
request rejection before drawing conclusions about detector quality. The
attack run does independently show signal/combining weaknesses and uncaught
invalid-input errors. Criterion 4 remains untested.

---

## The Improvement

**What I changed:** In `app.py::submit`, I added route-level checks before
either detector signal runs. The request must be a JSON object; `text` must be
a non-empty string with at least three whitespace-separated words; and a
provided `creator_id` must be a non-empty string. Invalid requests now get a
JSON 400 response and a rejection audit entry instead of reaching the model
and potentially producing an unhandled 500.

**Which diagnosis pointed at it:** Eleven malformed attack cases returned
500s. The route passed missing, null, too-short, or non-string text into the
signals, and assumed a parsed JSON body was always an object. This is a route
validation failure; for the short-text case, the invalid input then triggered
an error in signal one. I chose validation rather than changing signal weights
or thresholds because the observed failure was an unhandled request, not a
scoring trade-off.

### Attack Run — After

Report: `results/attack_run_2026-11-08_2007_after.md` — 56 attacks. The runner
auto-marked no 5xx failures; the target-based verdicts below are my review.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---:|---|---|---:|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `91feaffd-f28c-4635-8de1-5b4b3fd78be0` | human | 0.000 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `6d3818d6-88e9-43d5-acbd-6902cdf8b191` | unsure | 0.000 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `0b3e89ba-6c9f-4580-a68d-4a614ac62928` | unsure | 0.000 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `566c4b8d-45e6-49e6-8a08-ae9da7decb54` | unsure | 0.000 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `8a112cc1-cef5-48b1-a6a6-119058dbb058` | human | 0.000 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `2380bdeb-c193-42ad-b859-c02f5126d12e` | unsure | 0.000 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `1239e8ce-db7d-4ae6-984c-33dabb740d96` | unsure | 0.000 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `630d50e5-d300-4169-a428-7b1104eb65ed` | human | 0.000 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `f9bcdcfd-ddcb-466f-9b0e-7049d69105ee` | unsure | 0.000 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `676e9912-450b-4e38-aa94-cf0e7041a09e` | ai | 0.000 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `8d46403f-c19b-49d3-93df-1287aa6e0541` | unsure | 0.000 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `4141cad9-f9b2-4373-850c-e35e9648cc73` | unsure | 0.000 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c7119a60-267a-4697-bee5-bf086d795694` | unsure | 0.000 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `f73e791b-fe2c-41bc-8cf9-495cfee384b7` | unsure | 0.000 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `758819f9-4897-44c7-b071-3254386b3b6f` | unsure | 0.000 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | `1a8a317f-6261-43a6-a398-f5fdc84f875c` | unsure | 0.000 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `86a06e70-6366-4789-b4f1-d4b0195f4323` | unsure | 0.000 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `6b8a024a-5d3e-4391-844a-9d2dc254e1ab` | human | 0.000 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `3fa982a7-b009-471a-b1b9-622ceeb513cb` | human | 0.000 | BROKE |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `f2c87ff8-8b36-404e-9c16-13cdf943fd5f` | human | 0.000 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `f1290985-6565-4ae3-baad-e775ebeeb39c` | unsure | 0.000 | BROKE |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `161c0837-b1ca-4b96-b1f7-3899c106297d` | unsure | 0.000 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `bff40a18-3047-4e79-8080-eca06cfb21cb` | unsure | 0.000 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `44df05b7-9ddf-4424-ab82-1e96fd16d7da` | unsure | 0.000 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `69cf0e92-71f1-4679-8c2a-98448ae2de1c` | human | 0.000 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `a2d5ca0d-0384-45d1-ad1c-bdb3102c5f47` | human | 0.000 | HELD |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `24b17d5a-528d-4ff9-8abd-27247eb071bd` | ai | 0.000 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `acba3757-87ab-46be-85fa-afb199d55c3c` | ai | 0.000 | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `8b7c5272-aa27-4235-a6de-c512f2a1ca64` | human | 0.000 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b558e254-ecc6-45b2-97e5-6c5432641f9a` | human | 0.000 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `695031d4-d498-4cd2-8ee5-50060bcfda05` | human | 0.000 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d2e72b73-75f1-4ca5-8736-5a2b472f5d1a` | human | 0.000 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f7923146-4035-425d-ade9-89eb6db020a5` | human | 0.000 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `fa525f8d-b530-4b9d-bd7a-398f2c6a398a` | human | 0.000 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8f128801-590a-4277-b49e-a6d5c0497052` | human | 0.000 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `765615fa-4b50-446f-93ee-d3af6a5b6583` | human | 0.000 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0ffcc97f-febb-44e0-9089-d67620975bd5` | human | 0.000 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ec0775e4-cd95-4aa1-85c4-cd87ae82e7bc` | human | 0.000 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0191a2ec-0480-44b1-ae21-2ec2d8c49868` | human | 0.000 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

| Family | Attacks | BROKE | HELD |
|---|---:|---:|---:|
| `evasion` | 10 | 9 | 1 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 3 | 3 |
| **Total** | **56** | **12** | **44** |

**Did it help, and how do I know:** Yes, for the malformed-input failure.
Before the change, 11 malformed attacks returned 500; after it, all 20
malformed attacks returned either 400 or 200 and none returned 5xx. Fifteen
malformed attack requests were rejected with 400. The evaluation's four
malformed cases returned 400 in all three trials, with rejection entries and
no detection decisions. Five malformed cases remain accepted with 200
(control characters, punctuation, right-to-left text, very long text, and
missing `creator_id`), so validation coverage is incomplete.

The after attack run still has nine evasion failures and three
prompt-injection failures, so input validation did not change detector
behavior. In the after criteria report
(`results/run_2026-11-08_2007_after.md`), criterion 1 was MET: zero of ten
personal samples received the AI label in each run. Criterion 3 was MET: all
three labels appeared in every run. Criterion 5 was MET: all four malformed
cases returned 400 in every run, and the audit log contains rejection entries
instead of detection decisions. Criterion 2 could not be measured: all five
own-writing and all five AI-generated comparison requests returned 429 in
every trial, leaving no scores for the 0.15 comparison. Criterion 4 remains
untested because `run_eval.py` does not send appeals.

The score-spread groups exceed the 10-per-minute rate limit when run
back-to-back. They need to be rerun after the limit window resets or with a
suitable test limit before criterion 2 can be judged. This validation change
also rejects legitimate submissions shorter than three words; I accept that
friction rather than sending text too short for the current model signal to
score and risking another server error.

---

## What's Still Broken

**Nine evasion attacks and three prompt-injection attacks still BROKE.** The
main pattern is that ordinary text signals can be moved by edits or by
instruction-like text included in the submission. **Stages: signal one,
signal two, and the combining rule.** Typos, unusual wording, sentence
structure, and human-sounding additions shift the two signal scores; averaging
them can leave AI-targeted text in the human or unsure band. PI01 and PI02
were labeled human, while PI03 was unsure. I stopped short of changing the
weights or thresholds because the score-spread criterion was rate-limited and
could not establish how such a change would affect the target averages.

The route now avoids 5xx responses for the malformed attack set, but it still
accepts some unusual inputs with 200 responses: control characters,
punctuation-only text, right-to-left text, very long text, and a missing
`creator_id`. MF07 (right-to-left text) was labeled AI. That input does not
prove the text was human-written, but it shows the detector can make a strong
claim on text whose language or content may not be represented well by its
signals. **Stages: route validation and both signals.** I would next define a
maximum text length and decide which non-linguistic inputs should be rejected
or marked unsure, then test those policies.

Two criteria still lack evidence: criterion 2's score comparison returned
429 for all samples in both groups, and criterion 4's appeals were not run.
Criterion 1 and label coverage passed in the after evaluation; all four
criterion-5 inputs returned 400. I stopped rather than infer scores from
rate-limited requests or claim the appeal flow worked without testing it.


**The trade I'd make if this ran for real:**

I would prioritize avoiding false accusations: raise the AI threshold (for
example, from 0.65 to 0.75) and send more borderline or unfamiliar-language
text to `unsure` instead of labeling it AI. Writers would pay with more
inconclusive results, while the site would pay with more AI-written
submissions passing without a high-confidence AI label; I would validate that
trade with a rate-limit-safe score-spread run before shipping the threshold
change.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
