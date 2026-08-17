import unittest
from typing import Any, Dict

from gutenTAG import GutenTAG


class TestTrendAnomalyLength(unittest.TestCase):
    """Regression tests for the trend-anomaly amplitude-envelope broadcast bug.

    The envelope used to be built as ``int(length * 0.2) + int(length * 0.8)``
    samples, which is one short of ``length`` whenever ``length`` is not a
    multiple of 5, raising a NumPy broadcasting ``ValueError``. These tests
    exercise window lengths covering every residue mod 5 (plus very small
    lengths) to make sure the trend anomaly generates without error.
    """

    seed = 42

    def _build_config(self, length: int) -> Dict[str, Any]:
        return {
            "timeseries": [
                {
                    "name": f"test-trend-{length}",
                    "length": 500,
                    "base-oscillations": [{"kind": "sine"}],
                    "anomalies": [
                        {
                            "position": "middle",
                            "length": length,
                            "channel": 0,
                            "kinds": [
                                {"kind": "trend", "oscillation": {"kind": "sine"}}
                            ],
                        }
                    ],
                }
            ]
        }

    def test_trend_anomaly_length(self) -> None:
        # Lengths cover every residue mod 5; non-multiples of 5 (e.g. 93, 94,
        # 96, 97) used to crash, very small lengths (2, 3) guard the secondary
        # transition_length == 0 edge case.
        for length in [2, 3, 5, 11, 90, 93, 94, 95, 96, 97, 100]:
            with self.subTest(length=length):
                gutentag = GutenTAG(seed=self.seed)
                gutentag.load_config_dict(self._build_config(length))
                ts = gutentag.generate(return_timeseries=True)
                self.assertIsNotNone(ts)
                self.assertEqual(len(ts), 1)  # type: ignore


if __name__ == "__main__":
    unittest.main()
