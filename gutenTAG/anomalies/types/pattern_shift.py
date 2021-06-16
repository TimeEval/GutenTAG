from . import BaseAnomaly


class AnomalyPatternShift(BaseAnomaly):
    def __init__(self, shift_factor: float):
        self.shift_factor = shift_factor
