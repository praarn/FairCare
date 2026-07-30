from difflib import SequenceMatcher
from typing import List, Dict, Set
from .data_loader import load_treatments

# Below this score a match is considered too weak to be "the same thing" —
# but for plain treatment-name search we still fall back to showing the
# closest few rather than nothing, since typos/voice noise are expected
# and a wrong treatment *name* guess is low-stakes (the person is looking
# for something they already know they need).
MIN_USEFUL_SCORE = 0.32

# Symptom-based search is a different risk profile: suggesting a specific
# surgery off a weak, partial word match on vague symptoms is actively
# misleading. This threshold is intentionally much stricter, and — unlike
# the lenient path above — there is NO "closest anyway" fallback: an empty
# result (leading the person to "see a doctor") is the safe outcome here,
# not a failure.
MIN_USEFUL_SCORE_STRICT = 0.55

# Generic filler words that show up across almost any spoken or typed
# query ("I have appendix pain", "knee operation cost") and don't help
# distinguish one treatment from another. Stripped before word-overlap /
# similarity scoring so a shared filler word like "operation" doesn't
# out-rank a shared anatomical term like "knee".
STOPWORDS: Set[str] = {
    "i", "me", "my", "have", "has", "had", "in", "is", "are", "was", "were",
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


def _candidate_score(raw_query: str, query_words: Set[str], candidate: str) -> float:
    """
    Fuzzy-match one candidate string (a treatment name, alias, or symptom
    phrase) against the search input. Combines:

    1. Substring containment on the raw, unfiltered query — the strongest
       signal for typed partial input ("appendix" inside "appendix surgery").
    2. Word-overlap ratio on the *filler-stripped* query.
    3. Per-query-word coverage: for EACH remaining query word, how well
       does it match something in the candidate — then averaged across
       all of them. This is the key fix over an earlier version that took
       the single best word pair and let one incidental match (e.g. just
       "nausea" inside "nausea and vomiting with belly pain") drown out
       the fact that the rest of the query didn't match anything. Now a
       query needs most of its words to genuinely correspond, not just one.
    4. Whole-string character similarity as a smaller tiebreaker signal.
    """
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


def _best_score_for_treatment(raw_query: str, query_words: Set[str], treatment: Dict, use_symptoms: bool) -> float:
    candidates = [treatment["name"]] + treatment.get("aliases", [])
    if use_symptoms:
        candidates += treatment.get("symptoms", [])
    if treatment.get("name_hi"):
        candidates.append(treatment["name_hi"])
    return max((_candidate_score(raw_query, query_words, c) for c in candidates), default=0.0)


def search_treatments(query: str, strict: bool = False) -> List[Dict]:
    """
    Fuzzy/closest-match search against name + aliases (+ symptoms, when
    `strict=True` is used for the symptom checker). Empty query returns
    all treatments.

    strict=False (default, used by plain treatment-name search): lenient
    threshold, always falls back to the closest few rather than nothing.

    strict=True (symptom checker only): much higher bar, and returns an
    empty list rather than a weak guess if nothing clears it — matches
    against symptom phrases are also only considered in this mode, since
    they're the noisiest/most safety-sensitive signal.
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
        # No "closest anyway" fallback here — an empty result correctly
        # signals "we can't relate this to anything listed, see a doctor".
        return useful[:5]

    if useful:
        return useful[:8]

    return [t for score, t in scored[:5] if score > 0]


def get_treatment_by_id(treatment_id: str) -> Dict | None:
    for t in load_treatments():
        if t["id"] == treatment_id:
            return t
    return None