"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics
import unicodedata


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    The sample standard deviation of sentence word counts divided by their mean.

    Returns:
        A nonnegative coefficient of variation. Higher means sentence lengths
        vary more; fewer than two sentences returns 0.0.
    """
    sentence_word_counts = [len(words(sentence)) for sentence in sentences(text)]
    if len(sentence_word_counts) < 2:
        return 0.0

    mean_length = statistics.mean(sentence_word_counts)
    if mean_length == 0:
        return 0.0
    return statistics.stdev(sentence_word_counts) / mean_length


def type_token_ratio(text: str) -> float:
    """
    Unique normalized words divided by total normalized words.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    Unicode punctuation characters divided by the total number of characters.

    Returns:
        A float from 0.0 to 1.0; empty text returns 0.0.
    """
    if not text:
        return 0.0

    punctuation_count = sum(
        1 for character in text
        if unicodedata.category(character).startswith("P")
    )
    return punctuation_count / len(text)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    Combine the style measures into a 0–1 score; higher means more likely AI.

    The three normalized features are equally averaged: inverse coefficient
    of variation for sentence lengths, inverse type-token ratio, and
    punctuation density. Missing evidence contributes a neutral 0.5 for that
    feature. This is a simple heuristic, not a calibrated authorship test.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.
    """
    tokens = words(text)
    if not tokens:
        return 0.5

    sentence_count = len(sentences(text))
    spread = sentence_length_spread(text)
    sentence_regularity = (
        1.0 / (1.0 + spread) if sentence_count >= 2 else 0.5
    )
    vocabulary_repetition = 1.0 - type_token_ratio(text)
    punctuation = punctuation_density(text)

    return (sentence_regularity + vocabulary_repetition + punctuation) / 3.0


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nThese simple style measures are heuristics, not authorship proof.")
