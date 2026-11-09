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
| 1. Own writing | At most 1 of 10 gets the high-confidence AI label in each run | 10/10 returned 403; no labels | 10/10 returned 403; no labels | 10/10 returned 403; no labels | UNMEASURABLE |
| 2. Score spread | AI-generated average is at least 0.15 above own-writing average | All 10 returned 403; no scores | All 10 returned 403; no scores | All 10 returned 403; no scores | UNMEASURABLE |
| 3. Label coverage | Each run reaches human, unsure, and AI labels | 3/3 returned 403; no guesses | 3/3 returned 403; no guesses | 3/3 returned 403; no guesses | UNMEASURABLE |
| 4. Appeal path | 3/3 appeals are logged and set status to `under_review` | Not tested by `run_eval.py` | Not tested by `run_eval.py` | Not tested by `run_eval.py` | NOT RUN |
| 5. Malformed input | All 4 cases return 4xx and create no detection decision | 4/4 returned 403; decision logging unverified | 4/4 returned 403; decision logging unverified | 4/4 returned 403; decision logging unverified | INCONCLUSIVE |

Selected report: `results/run_2026-11-08_1951_before.md`, produced by
`run_eval.py::main`. All 81 requests in this report returned 403, including
valid submissions. The run did not produce detector scores or guesses, so the
scoring criteria cannot be assessed from these results. The malformed cases
did receive 4xx responses, but the report does not verify whether a detection
decision was written.

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

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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
