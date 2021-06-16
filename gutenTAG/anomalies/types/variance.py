from . import BaseAnomaly


class AnomalyVariance(BaseAnomaly):
    def __init__(self, factor: float):
        self.factor = factor
