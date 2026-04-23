"""Entropy scoring for potential secrets."""

from __future__ import annotations

import math
from collections import Counter


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    total = len(value)
    entropy = 0.0
    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    return round(entropy, 6)


def is_high_entropy(value: str, *, threshold: float = 3.5, min_length: int = 20) -> bool:
    if len(value) < min_length:
        return False
    return shannon_entropy(value) >= threshold

