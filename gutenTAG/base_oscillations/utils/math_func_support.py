from typing import Optional, Callable

import numpy as np


SAMPLING_F = 100  # in Hz


def calc_period_length(f: float) -> int:
    """Calculate the period length based on the frequency ``f`` and our default sampling frequency (in points)."""
    return int(SAMPLING_F / f)


def calc_n_periods(n: int, f: float) -> int:
    """Calculate the number of periods of frequency ``f`` that fit wholly into the signal of length ``n``."""
    return int(n / SAMPLING_F * f)


def prepare_base_signal(n: int, f: float) -> np.ndarray:
    """Creates the index base signal for mathematical functions using np.linspace and the factor 2*PI.

    Parameters
    ----------
    n : int
        length in number of points
    f : float
        base frequency in Hz (cycles/periods per second (per default: per 100 points))
    Returns
    -------
    base : np.ndarray
        base signal for mathematical functions (linear increasing index)
    """
    duration = n / SAMPLING_F  # in seconds

    # print(f"duration={duration} seconds")
    # print(f"frequency={f} Hz")
    # print(f"sampling frequency={SAMPLING_F} Hz")
    # print(f"periods={calc_n_periods(n, f)}")
    # print(f"period length={calc_period_length(f)} points")
    # print(f"length={n} points")

    t = np.linspace(0, duration, n)  # in seconds
    base = 2 * np.pi * f * t
    return base


def generate_periodic_signal(base: np.ndarray, func: Callable[[np.ndarray], np.ndarray], a: float, freq_mod: Optional[float] = None):
    """Generates a periodic signal based on the base signal (should already contain the frequency) and applying the
    supplied mathematical function. ``freq_mod`` can be used to modulate the signal amplitude with another frequency.

    Parameters
    ----------
    base : np.ndarray
        base signal (linear increasing index)
    func : array function
        signal creating mathematical function
    a : float
        amplitude of the desired signal
    freq_mod : Optional[float]
        optional frequency modulation as a factor of the base frequency
    Returns
    -------
    time series : np.ndarray
        Time series containing the signal (applying func on base) with amplitude ``a``.
    """
    ts: np.ndarray = np.array(a)
    if freq_mod:
        ts = func(base * freq_mod) * ts

    return func(base) * ts
