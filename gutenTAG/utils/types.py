from enum import Enum


class BaseOscillationKind(Enum):
    Sinus = "sinus"
    RandomWalk = "random_walk"
    CylinderBellFunnel = "cylinder_bell_funnel"
    ECG = "ecg"
    CoMuT = "comut"
