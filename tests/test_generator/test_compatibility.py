from unittest import TestCase

from gutenTAG.config.parser import ConfigParser


class TestCompatibility(TestCase):
    def setUp(self) -> None:
        self.config = {
            "timeseries": [
                {
                    "name": "ecg",
                    "length": 100,
                    "base-oscillations": [
                        {
                            "kind": "ecg"
                        }
                    ],
                    "anomalies": [
                        {
                            "position": "middle",
                            "length": 40,
                            "channel": 0,
                            "kinds": [
                                {
                                    "kind": "pattern-shift",
                                    "parameters": {
                                        "shift_by": 5,
                                        "transition_window": 10
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        self.breaking_config = {
            "timeseries": [
                {
                    "name": "ecg",
                    "length": 100,
                    "base-oscillations": [
                        {
                            "kind": "ecg"
                        }
                    ],
                    "anomalies": [
                        {
                            "position": "middle",
                            "length": 40,
                            "channel": 0,
                            "kinds": [
                                {
                                    "kind": "pattern-shift",
                                    "parameters": {
                                        "shift_by": 5,
                                        "transition_window": 10
                                    }
                                },
                                {
                                    "kind": "mode-correlation",
                                    "parameters": {}
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def test_compatibility(self):
        ConfigParser().parse(self.config)

    def test_compatibility_breaks(self):
        with self.assertRaises(ValueError):
            ConfigParser().parse(self.breaking_config)

    def test_compatibility_breaks_and_ignores(self):
        ConfigParser(skip_errors=True).parse(self.breaking_config)
