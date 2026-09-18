from collections.abc import Mapping
from typing import Any

RECOMMENDATION_WEIGHTS: dict[str, float] = {
    "semantic_similarity": 0.35,
    "knowledge_graph_relation": 0.30,
    "sequence_transition": 0.20,
    "historical_feedback": 0.10,
    "content_freshness": 0.05,
}

CASE_SIMILARITY_WEIGHTS: dict[str, float] = {
    "chart_structure_similarity": 0.35,
    "hexagram_path_similarity": 0.30,
    "topic_symbol_similarity": 0.20,
    "session_sequence_similarity": 0.15,
}

RECOMMENDATION_MODEL_VERSION = "weighted-rules-v1.0"
CASE_ALGORITHM_VERSION = "multi-feature-similarity-v1.0"


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def weighted_score(
    features: Mapping[str, float | None],
    weights: Mapping[str, float],
) -> tuple[float, dict[str, float], float]:
    available_weight = 0.0
    weighted_total = 0.0
    effective_weights: dict[str, float] = {}

    for feature_name, weight in weights.items():
        value = features.get(feature_name)
        if value is None:
            continue
        normalized_value = clamp(float(value))
        weighted_total += normalized_value * weight
        available_weight += weight
        effective_weights[feature_name] = weight

    if available_weight == 0:
        return 0.0, {}, 0.0

    effective_weights = {
        feature_name: round(weight / available_weight, 4)
        for feature_name, weight in effective_weights.items()
    }
    return round(weighted_total / available_weight, 6), effective_weights, available_weight


def scalar_similarity(left: Any, right: Any) -> float | None:
    if left is None or right is None:
        return None
    if isinstance(left, bool) or isinstance(right, bool):
        return 1.0 if left == right else 0.0
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        denominator = max(abs(float(left)), abs(float(right)), 1.0)
        return clamp(1.0 - abs(float(left) - float(right)) / denominator)
    if isinstance(left, str) and isinstance(right, str):
        normalized_left = " ".join(left.lower().split())
        normalized_right = " ".join(right.lower().split())
        if not normalized_left or not normalized_right:
            return None
        if normalized_left == normalized_right:
            return 1.0
        left_grams = _character_ngrams(normalized_left)
        right_grams = _character_ngrams(normalized_right)
        if not left_grams or not right_grams:
            return 0.0
        return len(left_grams & right_grams) / len(left_grams | right_grams)
    if isinstance(left, list) and isinstance(right, list):
        left_values = {_stable_key(item) for item in left}
        right_values = {_stable_key(item) for item in right}
        if not left_values or not right_values:
            return None
        return len(left_values & right_values) / len(left_values | right_values)
    return 1.0 if left == right else 0.0


def structured_similarity(left: Any, right: Any) -> float | None:
    left_flat = _flatten(left)
    right_flat = _flatten(right)
    shared_keys = sorted(set(left_flat) & set(right_flat))
    values: list[float] = []
    for key in shared_keys:
        similarity = scalar_similarity(left_flat[key], right_flat[key])
        if similarity is not None:
            values.append(similarity)
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        flat: dict[str, Any] = {}
        for key, item in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            flat.update(_flatten(item, child_prefix))
        return flat
    return {prefix or "value": value}


def _character_ngrams(value: str) -> set[str]:
    compact = "".join(value.split())
    if len(compact) < 2:
        return {compact} if compact else set()
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def _stable_key(value: Any) -> str:
    if isinstance(value, dict):
        return repr(sorted(value.items()))
    return repr(value)
