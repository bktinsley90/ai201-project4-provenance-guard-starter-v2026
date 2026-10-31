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
