import unittest

from gutenTAG import GutenTAG


class TestLengths(unittest.TestCase):
    def setUp(self) -> None:
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
                            # "creeping-length": 12,  # remove to test the default 20% option
                            "channel": 0,
                            "kinds": [{"kind": "amplitude", "amplitude_factor": 2.0}],
                        }
                    ],
                }
            ]
        }
        self.creeping_factor = 0.3

    def update_config(self, length: int, include_creeping: bool = False):
        self.config["timeseries"][0]["anomalies"][0]["length"] = length
        cl = int(round(length * self.creeping_factor)) if include_creeping else 0
        self.config["timeseries"][0]["anomalies"][0]["creeping-length"] = cl

    def __run(self):
        res = False
        gutentag = GutenTAG(seed=42)
        gutentag.load_config_dict(self.config)
        try:
            gutentag.generate(return_timeseries=True)
            res = True
        except ValueError:
            # For details see: https://github.com/TimeEval/GutenTAG/issues/49
            # Catches ValueError:
            #  'operands could not be broadcast together with shapes (n,) (n-1,)'
            ...
        return res

    def test_lengths(self):
        results = []
        for i in range(25, 50):
            self.update_config(i, include_creeping=False)
            results.append(self.__run())
        assert all(results)

    def test_lengths_with_creeping(self):
        results = []
        for i in range(25, 50):
            self.update_config(i, include_creeping=True)
            results.append(self.__run())
        assert all(results)
