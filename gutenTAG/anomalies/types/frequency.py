from __future__ import annotations
from . import BaseAnomaly


class AnomalyFrequency(BaseAnomaly):
    def __init__(self, factor: float):
        self.factor = factor
