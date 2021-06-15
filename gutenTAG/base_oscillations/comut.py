import numpy as np
import pandas as pd
from typing import Tuple
from collections import defaultdict


class CorrelatedMultivarGenerator:
    def __init__(self,
                 length: int,
                 dimensions: int,
                 n_anomalies: int,
                 step_length: int,
                 value_diff: int,
                 value_offset: int,
                 dimensions_involved: int,
                 std: float = 1):
        self.length = length
        self.dimensions = dimensions
        self.n_anomalies = n_anomalies
        self.step_length = step_length
        self.value_diff = value_diff
        self.value_offset = value_offset
        self.dimensions_involved = dimensions_involved
        self.std = std

    def _generate_random_values(self, dim: int) -> np.ndarray:
        high_val = (self.value_diff * (dim + 1) - self.value_diff / 2) + self.value_offset
        return np.abs(np.random.normal(high_val, self.std, size=self.length))

    def _generate_random_steps(self) -> np.ndarray:
        n_steps = int(np.ceil(self.length / self.step_length).item())
        energy = np.random.choice([-1, 1], size=n_steps)
        base = np.repeat(energy, self.step_length)[:self.length].astype(np.float64)
        values = self._generate_random_values(0)
        base *= values
        return base

    def _generate_partner_steps(self, partner: np.ndarray, dim: int, n_anomalies: int) -> Tuple[np.ndarray, np.ndarray]:
        anomalies = np.random.choice(self.length // self.step_length, size=n_anomalies, replace=False) * self.step_length
        energy = np.sign(partner)
        anomalies = (np.repeat(anomalies.reshape(-1, 1), axis=1, repeats=self.step_length) + np.arange(self.step_length)).flatten()
        energy[anomalies] *= -1
        values = self._generate_random_values(dim)
        array = energy * values
        return array, anomalies

    def _distribute_anomalies(self) -> dict:
        results = defaultdict(int)
        unique, counts = np.unique(np.random.choice(np.arange(1, self.dimensions_involved), size=self.n_anomalies), return_counts=True)
        results.update(dict(zip(unique, counts)))
        return results

    def generate(self) -> pd.DataFrame:
        assert 1 < self.dimensions_involved <= self.dimensions
        anomaly_distribution = self._distribute_anomalies()
        base = self._generate_random_steps()
        other_dims, anomalies = zip(*[self._generate_partner_steps(base, dim, anomaly_distribution[dim])
                                      for dim in range(1, self.dimensions)])
        labels = np.zeros(len(base))
        labels[np.concatenate(anomalies)] = 1
        results = np.stack([base]+[o for o in other_dims]+[labels], axis=1)

        df = pd.DataFrame(results, columns=[f"value_{i}" for i in range(self.dimensions)]+["is_anomaly"])
        df.index.set_names("timestamp", inplace=True)
        df["is_anomaly"] = df.is_anomaly.astype(int)
        return df
