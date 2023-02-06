from .base_oscillation import BaseOscillation
from .cosine import Cosine
from .custom_process import CustomProcess
from .cylinder_bell_funnel import CylinderBellFunnel
from .dirichlet import Dirichlet
from .ecg import ECG
from .formula import Formula  # type: ignore  # mypy ends up in recursion
from .interface import BaseOscillationInterface
from .mls import MLS
from .polynomial import Polynomial
from .random_mode_jump import RandomModeJump
from .random_walk import RandomWalk
from .sawtooth import Sawtooth
from .sine import Sine
from .square import Square
