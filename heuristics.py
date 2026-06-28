import re
import string


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"[.!?]+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def calculate_stylometric_score(text: str) -> dict:
    sentences = split_sentences(text)
    words = tokenize_words(text)

    if not sentences or not words:
        return {
            "score": 0.5,
            "metrics": {
                "avg_sentence_length": 0,
                "sentence_length_variance": 0,
                "type_token_ratio": 0,
                "punctuation_density": 0
            }
        }

    sentence_lengths = [
        len(tokenize_words(sentence))
        for sentence in sentences
    ]

    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

    sentence_length_variance = sum(
        (length - avg_sentence_length) ** 2
        for length in sentence_lengths
    ) / len(sentence_lengths)

    unique_words = set(words)
    type_token_ratio = len(unique_words) / len(words)

    punctuation_count = sum(1 for char in text if char in string.punctuation)
    punctuation_density = punctuation_count / max(len(text), 1)

    # Score components:
    # Higher score means more AI-like.
    # AI writing often has moderate sentence length, lower variance,
    # controlled punctuation, and smooth vocabulary patterns.

    length_score = 1.0 if 14 <= avg_sentence_length <= 26 else 0.4

    variance_score = 1.0 if sentence_length_variance < 20 else 0.3

    ttr_score = 0.8 if 0.35 <= type_token_ratio <= 0.75 else 0.4

    punctuation_score = 0.8 if punctuation_density < 0.08 else 0.3

    final_score = (
        0.30 * length_score
        + 0.30 * variance_score
        + 0.25 * ttr_score
        + 0.15 * punctuation_score
    )

    return {
        "score": round(final_score, 3),
        "metrics": {
            "avg_sentence_length": round(avg_sentence_length, 3),
            "sentence_length_variance": round(sentence_length_variance, 3),
            "type_token_ratio": round(type_token_ratio, 3),
            "punctuation_density": round(punctuation_density, 3)
        }
    }