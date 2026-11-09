# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 20:07
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `91feaffd-f28c-4635-8de1-5b4b3fd78be0` | human | 0.000 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `6d3818d6-88e9-43d5-acbd-6902cdf8b191` | unsure | 0.000 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `0b3e89ba-6c9f-4580-a68d-4a614ac62928` | unsure | 0.000 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `566c4b8d-45e6-49e6-8a08-ae9da7decb54` | unsure | 0.000 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `8a112cc1-cef5-48b1-a6a6-119058dbb058` | human | 0.000 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `2380bdeb-c193-42ad-b859-c02f5126d12e` | unsure | 0.000 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `1239e8ce-db7d-4ae6-984c-33dabb740d96` | unsure | 0.000 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `630d50e5-d300-4169-a428-7b1104eb65ed` | human | 0.000 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `f9bcdcfd-ddcb-466f-9b0e-7049d69105ee` | unsure | 0.000 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `676e9912-450b-4e38-aa94-cf0e7041a09e` | ai | 0.000 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `8d46403f-c19b-49d3-93df-1287aa6e0541` | unsure | 0.000 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `4141cad9-f9b2-4373-850c-e35e9648cc73` | unsure | 0.000 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c7119a60-267a-4697-bee5-bf086d795694` | unsure | 0.000 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `f73e791b-fe2c-41bc-8cf9-495cfee384b7` | unsure | 0.000 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `758819f9-4897-44c7-b071-3254386b3b6f` | unsure | 0.000 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `1a8a317f-6261-43a6-a398-f5fdc84f875c` | unsure | 0.000 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `86a06e70-6366-4789-b4f1-d4b0195f4323` | unsure | 0.000 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `6b8a024a-5d3e-4391-844a-9d2dc254e1ab` | human | 0.000 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `3fa982a7-b009-471a-b1b9-622ceeb513cb` | human | 0.000 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `f2c87ff8-8b36-404e-9c16-13cdf943fd5f` | human | 0.000 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `f1290985-6565-4ae3-baad-e775ebeeb39c` | unsure | 0.000 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `161c0837-b1ca-4b96-b1f7-3899c106297d` | unsure | 0.000 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `bff40a18-3047-4e79-8080-eca06cfb21cb` | unsure | 0.000 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `44df05b7-9ddf-4424-ab82-1e96fd16d7da` | unsure | 0.000 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `69cf0e92-71f1-4679-8c2a-98448ae2de1c` | human | 0.000 |  |
| MF04 | malformed | text is only punctuation | 200 | `a2d5ca0d-0384-45d1-ad1c-bdb3102c5f47` | human | 0.000 |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `24b17d5a-528d-4ff9-8abd-27247eb071bd` | ai | 0.000 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `acba3757-87ab-46be-85fa-afb199d55c3c` | ai | 0.000 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `8b7c5272-aa27-4235-a6de-c512f2a1ca64` | human | 0.000 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b558e254-ecc6-45b2-97e5-6c5432641f9a` | human | 0.000 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `695031d4-d498-4cd2-8ee5-50060bcfda05` | human | 0.000 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d2e72b73-75f1-4ca5-8736-5a2b472f5d1a` | human | 0.000 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f7923146-4035-425d-ade9-89eb6db020a5` | human | 0.000 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `fa525f8d-b530-4b9d-bd7a-398f2c6a398a` | human | 0.000 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8f128801-590a-4277-b49e-a6d5c0497052` | human | 0.000 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `765615fa-4b50-446f-93ee-d3af6a5b6583` | human | 0.000 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0ffcc97f-febb-44e0-9089-d67620975bd5` | human | 0.000 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ec0775e4-cd95-4aa1-85c4-cd87ae82e7bc` | human | 0.000 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0191a2ec-0480-44b1-ae21-2ec2d8c49868` | human | 0.000 |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "91feaffd-f28c-4635-8de1-5b4b3fd78be0",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.1635,
  "style_score": 0.3358921737062701,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "6d3818d6-88e9-43d5-acbd-6902cdf8b191",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.5943,
  "style_score": 0.24687295109543342,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "0b3e89ba-6c9f-4580-a68d-4a614ac62928",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.6662,
  "style_score": 0.2930013007941186,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "566c4b8d-45e6-49e6-8a08-ae9da7decb54",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.6114,
  "style_score": 0.33263687714922163,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "8a112cc1-cef5-48b1-a6a6-119058dbb058",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.3212,
  "style_score": 0.2863545681671888,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "2380bdeb-c193-42ad-b859-c02f5126d12e",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.5727,
  "style_score": 0.23999047761449513,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "1239e8ce-db7d-4ae6-984c-33dabb740d96",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.5862,
  "style_score": 0.2525039112860676,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "630d50e5-d300-4169-a428-7b1104eb65ed",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.2452,
  "style_score": 0.27009600718589616,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "f9bcdcfd-ddcb-466f-9b0e-7049d69105ee",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.7042,
  "style_score": 0.2860565924578427,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "676e9912-450b-4e38-aa94-cf0e7041a09e",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.0,
  "model_score": 0.9792,
  "style_score": 0.46747031241662723,
  "label": "This text appears more consistent with AI-generated writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "8d46403f-c19b-49d3-93df-1287aa6e0541",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.6175,
  "style_score": 0.33216231086046,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "4141cad9-f9b2-4373-850c-e35e9648cc73",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.7387,
  "style_score": 0.3708232308786487,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c7119a60-267a-4697-bee5-bf086d795694",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.8051,
  "style_score": 0.3489199364039249,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "f73e791b-fe2c-41bc-8cf9-495cfee384b7",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.8329,
  "style_score": 0.314397666026256,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "758819f9-4897-44c7-b071-3254386b3b6f",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.8005,
  "style_score": 0.4067802836081152,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "1a8a317f-6261-43a6-a398-f5fdc84f875c",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.8814,
  "style_score": 0.3145706033703409,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "86a06e70-6366-4789-b4f1-d4b0195f4323",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.8816,
  "style_score": 0.3823228073048668,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "6b8a024a-5d3e-4391-844a-9d2dc254e1ab",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.3223,
  "style_score": 0.26038795136045706,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "3fa982a7-b009-471a-b1b9-622ceeb513cb",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.4625,
  "style_score": 0.22791316602182565,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "f2c87ff8-8b36-404e-9c16-13cdf943fd5f",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.2044,
  "style_score": 0.2248921669357173,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "f1290985-6565-4ae3-baad-e775ebeeb39c",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.5943,
  "style_score": 0.2846828360544344,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "161c0837-b1ca-4b96-b1f7-3899c106297d",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.4998,
  "style_score": 0.2977417914155376,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "bff40a18-3047-4e79-8080-eca06cfb21cb",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.6401,
  "style_score": 0.2689509353104387,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "44df05b7-9ddf-4424-ab82-1e96fd16d7da",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.0,
  "model_score": 0.5583,
  "style_score": 0.3341398474638084,
  "label": "We can't reliably tell whether this text was written by a person or generated by AI. This result is not an accusation.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "69cf0e92-71f1-4679-8c2a-98448ae2de1c",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0,
  "style_score": 0.1984126984126984,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "a2d5ca0d-0384-45d1-ad1c-bdb3102c5f47",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "24b17d5a-528d-4ff9-8abd-27247eb071bd",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.0,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "This text appears more consistent with AI-generated writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "acba3757-87ab-46be-85fa-afb199d55c3c",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.0,
  "model_score": 0.9876,
  "style_score": 0.5709410766432871,
  "label": "This text appears more consistent with AI-generated writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "8b7c5272-aa27-4235-a6de-c512f2a1ca64",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.2395,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "b558e254-ecc6-45b2-97e5-6c5432641f9a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "695031d4-d498-4cd2-8ee5-50060bcfda05",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "d2e72b73-75f1-4ca5-8736-5a2b472f5d1a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "f7923146-4035-425d-ade9-89eb6db020a5",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "fa525f8d-b530-4b9d-bd7a-398f2c6a398a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "8f128801-590a-4277-b49e-a6d5c0497052",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "765615fa-4b50-446f-93ee-d3af6a5b6583",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "0ffcc97f-febb-44e0-9089-d67620975bd5",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "ec0775e4-cd95-4aa1-85c4-cd87ae82e7bc",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "0191a2ec-0480-44b1-ae21-2ec2d8c49868",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.0,
  "model_score": 0.0287,
  "style_score": 0.17272727272727273,
  "label": "This text appears more consistent with human writing, though this assessment can be wrong.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
