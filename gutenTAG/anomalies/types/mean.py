from . import BaseAnomaly


class AnomalyMean(BaseAnomaly):
    def __init__(self, offset: float):
        self.offset = offset
