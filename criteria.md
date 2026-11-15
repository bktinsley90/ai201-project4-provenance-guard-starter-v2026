# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

In each of three evaluation runs, no more than 1 of 10 pieces of my own writing
will receive the high-confidence AI label.

**Why this target:**

False accusations are more harmful to writers than missed detections are to
the site, so I would rather send borderline writing to "unsure" than label
more than 1 in 10 of my own pieces as AI.

---

## 2.

In each of three runs, the average combined score for five confidently
AI-generated samples will be at least 0.15 higher than the average score for
five pieces of my own writing.

**Why this target:**

A 0.15 gap is a modest, measurable separation on the 0-to-1 scale, without
claiming the detector can perfectly distinguish every individual text.

---

## 3.

In each of three runs, at least one test submission will receive each of the
three labels: high-confidence human, unsure, and high-confidence AI.

**Why this target:**

Every label needs to be reachable for the scoring bands to be useful; including
an unsure outcome also gives uncertain cases a path that is not an accusation.

---

## 4.

For 3 out of 3 valid appeals against existing submissions, the appeal will be
recorded with its content ID and reasoning, the item's status will become
`under_review`, and the original decision will remain in the audit log.

**Why this target:**

An appeal must reliably create a review trail without erasing the decision
being contested; requiring all three checks makes both the status change and
the audit history observable.

## 5.

All 4 malformed submission cases I test (missing `text`, empty `text`, null
`text`, and non-string `text`) will receive a 4xx response and will not create
a detection decision.

**Why this target:**

These common invalid requests should fail clearly instead of being scored as
real submissions; 4xx responses and the absence of a decision are both
straightforward to verify.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone acceptance criteria — failure hardening

These criteria apply to the capstone extension and do not replace the original
five criteria above. Each criterion will be evaluated across three independent
test runs. A target must hold in all three runs to be met.

## Capstone 1. Invalid and oversized submissions

In each run, 6 out of 6 test cases—missing, empty, null, and non-string
`text`, text over 10,000 characters, and a request body over 64,000 bytes—will
receive a JSON 4xx response, create a rejection audit entry, and create no
detection decision.

**Why this target:**

I require all six to be rejected because even one invalid request could create
an unsupported authorship decision or consume unnecessary model resources.
This target covers the known failure types without requiring the service to
reject every unusual writing style, which could exclude legitimate writers.

---

## Capstone 2. Rate limiting

In each run, with an available detector and a fresh rate-limit window, 11
sequential valid submissions from the same new `creator_id` within one minute
will produce 10 HTTP 200 responses followed by a JSON 429 response. The
rejection will appear in the audit log and will not create a decision.

**Why this target:**

Ten per minute is the configured balance between allowing draft revisions and
limiting automated probing. A lower test target would not verify the actual
boundary; allowing an eleventh request would miss a rate-limit failure and
could increase model load.

---

## Capstone 3. Detector failure and timeout

In each run, 1 injected detector failure will return JSON 503, and 1 injected
detector timeout will return JSON 504. Both requests will create rejection
audit entries and no detection decisions; while the timed-out detector is
still running, 1 subsequent submission will return JSON 503 and create a
rejection audit entry without a decision.

**Why this target:**

Every tested failure must avoid a decision because an unverified label could
unfairly accuse a writer. Testing one of each failure and the busy state in
each run covers the distinct responses without claiming to reproduce every
possible model failure; a looser target could hide a failure as a decision.

---

## Capstone 4. Appeal handling

In each run, 3 out of 3 valid appeals against different existing decisions
will return HTTP 200 and create `under_review` events with the content IDs
and reasoning while preserving the original decisions. A repeated appeal for
one of those submissions will return JSON 409, create a rejection audit entry,
and leave exactly one appeal event for that submission.

**Why this target:**

All three appeals must be recorded because losing even one review request
leaves a writer without a way to challenge a decision. Three submissions
exercise separate records without requiring an impractically large manual
review set; accepting a duplicate could create unnecessary review work.

---

## Capstone 5. Structured request logs

In each run, 10 valid submissions and 1 rejected submission will each produce
1 readable JSON Lines request record containing a timestamp, input, output,
status code, and nonnegative duration. The 10 successful records will be used
to calculate the arithmetic mean request duration; the rejection will not be
included in that average.

**Why this target:**

Ten successful requests provide the required sample for measuring the cost of
a run; fewer would make the average less representative of those requests.
Including a rejection checks that failure evidence is not lost, while excluding
it from the success average avoids making scoring appear faster than it is.
