"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Replace the placeholders for criteria 1 and 2 with your own writing and
AI-generated samples. Criterion 4 needs an appeal request, which `run_eval.py`
does not send.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Replace each placeholder with a separate piece you wrote yourself.
        "texts": [
            "Teriamisu is my favorite dessert of all time!",
            "I use a notebook to jot down my tasks every day.",
            "I had hoped to play GTA 6 on Thursay Nov 12 but I realized after scheduling my FTO for that day its actually not available till Nov 19th.",
            "Going to the Gym 5 times a week has become my favorite thing to do. I love seeing the progress I am making.",
            "When planning a trip i think about the major things I need such as logging, food, mode of transportation and then I make plan for each of them accordingly.",
            "I recently started using a new app called MyFitnessPal to track my steps, meals, and calories.",
            "I think one change that would make my neighborhood better is having more safe places for young people to gather and socialize.",
            "My gym trainer introduced me to Bench pressing. I am nervous and it was a struggle at first but I plan to keep trying. I love the progress I am making in the gym. It has helped me not only physically but the confidence boost I get from seeing my improvements.",
            "I am contemplating wether its worth continuing to pursue Software Engineering as a career. Or pursue Finanial Engineering instead.",
            "I would not recommend wathing 1883 as it was quite slow and tragic overall.",
        ],
    },
    {
        "name": "score spread — my own writing",
        "criterion": 2,
        # Five of the samples you supplied for criterion 1.
        "texts": [
            "I had hoped to play GTA 6 on Thursay Nov 12 but I realized after scheduling my FTO for that day its actually not available till Nov 19th.",
            "Going to the Gym 5 times a week has become my favorite thing to do. I love seeing the progress I am making.",
            "When planning a trip i think about the major things I need such as logging, food, mode of transportation and then I make plan for each of them accordingly.",
            "My gym trainer introduced me to Bench pressing. I am nervous and it was a struggle at first but I plan to keep trying. I love the progress I am making in the gym. It has helped me not only physically but the confidence boost I get from seeing my improvements.",
            "I am contemplating wether its worth continuing to pursue Software Engineering as a career. Or pursue Finanial Engineering instead.",
        ],
    },
    {
        "name": "score spread — AI-generated samples",
        "criterion": 2,
        # AI-generated examples for comparison with the five personal samples.
        "texts": [
            (
                "A consistent exercise routine can support both physical health "
                "and emotional well-being. Setting realistic goals makes it "
                "easier to build habits that last over time. Tracking progress "
                "can also help people recognize improvements that might "
                "otherwise go unnoticed."
            ),
            (
                "Effective trip planning begins with identifying the main "
                "requirements, including transportation, lodging, meals, and "
                "the activities you hope to enjoy. Creating a simple checklist "
                "can help keep these details organized. Reviewing the plan "
                "before departure can reduce avoidable stress."
            ),
            (
                "Learning a new skill often requires patience and consistent "
                "practice. Beginners may find the first attempts challenging, "
                "but gradual progress can build confidence. Setting aside "
                "regular time to practice is a practical way to improve."
            ),
            (
                "Communities benefit when residents have safe, welcoming "
                "places to spend time together. Shared spaces can encourage "
                "conversation and help people form stronger connections. "
                "Thoughtful design should consider accessibility, upkeep, "
                "and the needs of different age groups."
            ),
            (
                "Choosing a career path involves balancing personal interests "
                "with practical considerations. Researching the responsibilities "
                "and qualifications for each field can make the options clearer. "
                "Speaking with people who work in those careers may also "
                "provide useful perspective."
            ),
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": [
            "Went for a run. Legs hurt. Worth it.",
            (
                "We got to the campsite about four. The pitch was fine, a bit "
                "sloped, but there was a tap nearby and the toilets were clean "
                "enough. Putting the tent up took longer than it should have "
                "because I had forgotten how the poles went. The weather held "
                "until Saturday night. Then it rained hard and kept raining. "
                "We stayed in the tent and played cards and ate most of the "
                "food we had brought for Sunday. On Sunday we packed up wet "
                "and drove home early. It was not the weekend we planned but "
                "the kids enjoyed it and we would go back."
            ),
            (
                "The importance of effective communication in the workplace "
                "cannot be overstated. Teams that communicate clearly are "
                "better positioned to achieve their objectives and avoid "
                "costly m\n\nThe importance of effective communication in the "
                "workplace cannot be overstated. Teams that communicate "
                "clearly are better positioned to achieve their objectives "
                "and avoid costly m\n\nThe importance of effective "
                "communication in the workplace cannot be overstated. Teams "
                "that communicate clearly are better positioned to achieve "
                "their objectives and avoid costly m"
            ),
        ],
    },
    {
        "name": "malformed submissions",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_bad_missing"},
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": 12345, "creator_id": "eval_bad_non_string"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
