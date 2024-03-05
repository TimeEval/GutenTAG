import unittest
from typing import Dict, Any

from gutenTAG import GutenTAG


class TestLengths(unittest.TestCase):
    def setUp(self) -> None:
        self.seed = 42
        self.config = {
            "timeseries": [
                {
                    "name": "test-amp",
                    "length": 500,
                    "base-oscillations": [{"kind": "sine"}],
                    "anomalies": [
                        {
                            "position": "end",
                            "length": 47,
                            "channel": 0,
                            "kinds": [{"kind": "amplitude", "amplitude_factor": 2.0}],
                        }
                    ],
                }
            ]
        }
        self.creeping_factor = 0.3

    def _update_config(
        self, length: int, include_creeping: bool = False
    ) -> Dict[str, Any]:
        config = self.config.copy()
        config["timeseries"][0]["anomalies"][0]["length"] = length
        cl = int(round(length * self.creeping_factor)) if include_creeping else 0
        config["timeseries"][0]["anomalies"][0]["creeping-length"] = cl
        return config

    def _run_and_validate(self, config: Dict[str, Any]) -> None:
        gutentag = GutenTAG(seed=self.seed)
        gutentag.load_config_dict(config)
        ts = gutentag.generate(return_timeseries=True)
        self.assertIsNotNone(ts)
        self.assertEqual(len(ts), 1)

    def test_lengths(self) -> None:
        for i in range(25, 50):
            # Check case anomaly_protocol.creeping_length == 0
            config = self._update_config(i, include_creeping=False)
            self._run_and_validate(config)
            # Check case anomaly_protocol.creeping_length > 0
            config = self._update_config(i, include_creeping=True)
            self._run_and_validate(config)
