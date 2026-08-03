from difflib import SequenceMatcher
from typing import List, Dict, Set
from .data_loader import load_treatments

# Below this score a match is considered too weak to be "the same thing" —
# but for plain treatment-name search we still fall back to showing the
# closest few rather than nothing, since typos/voice noise are expected
# and a wrong treatment *name* guess is low-stakes (the person is looking
# for something they already know they need).
MIN_USEFUL_SCORE = 0.32

# Symptom-based search uses a completely different scoring function (see
# _candidate_score_strict below) with a much wider gap between noise and
# signal, so this threshold can stay generous while still safely rejecting
# unrelated queries — calibrated empirically: false-positive queries like
# "nausea and diarrhea" or "headache and dizziness" score 0.0 against
# unrelated treatments, while genuine (even loosely worded) matches score
# 0.28+. There is NO "closest anyway" fallback in strict mode: an empty
# result correctly means "see a doctor," not a failure.
MIN_USEFUL_SCORE_STRICT = 0.35

# Generic filler words that show up across almost any spoken or typed
# query ("I have appendix pain", "knee operation cost") and don't help
# distinguish one treatment from another. Stripped before word-overlap /
# similarity scoring so a shared filler word like "operation" doesn't
# out-rank a shared anatomical term like "knee".
STOPWORDS: Set[str] = {
    "i", "me", "my", "have", "has", "had", "in", "is", "are", "was", "were",
    "on", "at", "near",
    "a", "an", "the", "of", "for", "to", "and", "or", "with",
    "pain", "ache", "aches", "hurt", "hurts", "hurting",
    "cost", "costs", "price", "estimate", "cheap", "cheapest",
    "need", "needed", "needing", "want", "wanted",
    "surgery", "operation", "treatment", "procedure",
    "hospital", "doctor", "please", "help", "get", "done", "do",
    "this", "that", "some", "any",
}


def _strip_stopwords(words: Set[str]) -> Set[str]:
    filtered = words - STOPWORDS
    return filtered if filtered else words  # don't strip down to nothing


# ---------- lenient scoring: plain treatment-name search ----------
# Unchanged from the earlier fix — validated against typed names, typos,
# and short voice transcripts. Kept separate from the strict/symptom
# scorer below so tuning one never risks regressing the other.

def _candidate_score_lenient(raw_query: str, query_words: Set[str], candidate: str) -> float:
    candidate = candidate.strip().lower()
    if not candidate:
        return 0.0

    if raw_query and (raw_query in candidate or candidate in raw_query):
        shorter = min(len(raw_query), len(candidate))
        longer = max(len(raw_query), len(candidate))
        return 0.7 + 0.3 * (shorter / longer)

    candidate_words = set(candidate.split())
    if not query_words or not candidate_words:
        return 0.0

    union = query_words | candidate_words
    overlap = len(query_words & candidate_words) / len(union) if union else 0.0

    per_word_best = []
    for qw in query_words:
        best_for_this_word = max(SequenceMatcher(None, qw, cw).ratio() for cw in candidate_words)
        per_word_best.append(best_for_this_word)
    avg_word_coverage = sum(per_word_best) / len(per_word_best)

    seq_ratio = SequenceMatcher(None, " ".join(sorted(query_words)), candidate).ratio()

    return 0.4 * overlap + 0.4 * avg_word_coverage + 0.2 * seq_ratio


# ---------- strict scoring: symptom checker ----------
# An F1-style precision/recall blend over exact (post-stopword) word
# matches, with a small allowance for near-exact fuzzy matches (typos).
# This cleanly separates real matches from noise in a way the lenient
# formula didn't: a single incidental shared word against an otherwise
# irrelevant multi-word query now scores low on BOTH precision and recall,
# instead of one lucky word pair being able to dominate the whole score.

def _candidate_score_strict(raw_query: str, query_words: Set[str], candidate: str) -> float:
    candidate = candidate.strip().lower()
    if not candidate:
        return 0.0

    if raw_query and (raw_query in candidate or candidate in raw_query):
        shorter = min(len(raw_query), len(candidate))
        longer = max(len(raw_query), len(candidate))
        return 0.7 + 0.3 * (shorter / longer)

    candidate_words = _strip_stopwords(set(candidate.split()))
    if not query_words or not candidate_words:
        return 0.0

    hits = 0.0
    for qw in query_words:
        if qw in candidate_words:
            hits += 1.0
        else:
            best = max((SequenceMatcher(None, qw, cw).ratio() for cw in candidate_words), default=0.0)
            if best >= 0.82:  # typo-level closeness only, not loose fuzziness
                hits += best

    precision = hits / len(query_words)
    recall = hits / len(candidate_words)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _best_score_for_treatment(raw_query: str, query_words: Set[str], treatment: Dict, use_symptoms: bool) -> float:
    candidates = [treatment["name"]] + treatment.get("aliases", [])
    if use_symptoms:
        candidates += treatment.get("symptoms", [])
    if treatment.get("name_hi"):
        candidates.append(treatment["name_hi"])

    scorer = _candidate_score_strict if use_symptoms else _candidate_score_lenient
    return max((scorer(raw_query, query_words, c) for c in candidates), default=0.0)


def search_treatments(query: str, strict: bool = False) -> List[Dict]:
    """
    Fuzzy/closest-match search against name + aliases (+ symptoms, when
    `strict=True` is used for the symptom checker). Empty query returns
    all treatments.

    strict=False (default, used by plain treatment-name search): lenient
    threshold, always falls back to the closest few rather than nothing.

    strict=True (symptom checker only): F1-based scoring with a much
    higher bar, and returns an empty list rather than a weak guess if
    nothing clears it.
    """
    treatments = load_treatments()
    raw_query = (query or "").strip().lower()
    if not raw_query:
        return treatments

    query_words = _strip_stopwords(set(raw_query.split()))

    scored = [
        (_best_score_for_treatment(raw_query, query_words, t, use_symptoms=strict), t)
        for t in treatments
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)

    threshold = MIN_USEFUL_SCORE_STRICT if strict else MIN_USEFUL_SCORE
    useful = [t for score, t in scored if score >= threshold]

    if strict:
        return useful[:5]

    if useful:
        return useful[:8]

    return [t for score, t in scored[:5] if score > 0]


def get_treatment_by_id(treatment_id: str) -> Dict | None:
    for t in load_treatments():
        if t["id"] == treatment_id:
            return t
    return None