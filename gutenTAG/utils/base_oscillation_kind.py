from enum import Enum


class BaseOscillationKind(Enum):
    Sine = "sine"
    Cosine = "cosine"
    RandomWalk = "random_walk"
    CylinderBellFunnel = "cylinder_bell_funnel"
    ECG = "ecg"
    Polynomial = "polynomial"
    RandomModeJump = "random_mode_jump"
    Formula = "formula"
