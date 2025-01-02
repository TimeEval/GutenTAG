from unittest import TestCase

import numpy as np
import yaml

from gutenTAG.generator.overview import DictSanitizer


class TestOverviewSanitizer(TestCase):
    def setUp(self) -> None:
        self.numpy_config = {
            "timeseries": [
                {
                    "name": "ecg",
                    "length": np.int32(100),
                    "base-oscillations": [{"kind": "ecg", "frequency": np.float64(2)}],
                    "anomalies": [
                        {
                            "position": "middle",
                            "length": np.int32(40),
                            "channel": np.int32(0),
                            "kinds": [
                                {
                                    "kind": "pattern-shift",
                                    "shift_by": np.int32(5),
                                    "transition_window": np.int32(10),
                                    "some_array": np.array([1.2, 2.3]),
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        self.clean_config = {
            "timeseries": [
                {
                    "name": "ecg",
                    "length": 100,
                    "base-oscillations": [{"kind": "ecg", "frequency": 2.0}],
                    "anomalies": [
                        {
                            "position": "middle",
                            "length": 40,
                            "channel": 0,
                            "kinds": [
                                {
                                    "kind": "pattern-shift",
                                    "shift_by": 5,
                                    "transition_window": 10,
                                    "some_array": [1.2, 2.3],
                                }
                            ],
                        }
                    ],
                }
            ]
        }

    def test_all_numpy_types_gone(self):
        correct_yaml = yaml.dump(self.clean_config)

        sanitizer = DictSanitizer()
        cleaned_config = sanitizer.sanitize(self.numpy_config)
        cleaned_yaml = yaml.dump(cleaned_config)

        self.assertEqual(correct_yaml, cleaned_yaml)
