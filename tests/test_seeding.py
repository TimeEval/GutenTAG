import unittest
from copy import deepcopy
from typing import List, Optional

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from gutenTAG import GutenTAG, TimeSeries


class TestSeeding(unittest.TestCase):
    def setUp(self) -> None:
        config_sine = {
            "name": "sine-ts",
            "length": 500,
            "base-oscillations": [{"kind": "sine", "frequency": 1.5}],
            "anomalies": [
                {
                    "position": "beginning",
                    "length": 5,
                    "kinds": [{"kind": "frequency", "frequency_factor": 2}],
                }
            ],
        }
        config_ecg = {
            "name": "ecg-ts",
            "length": 1000,
            "base-oscillations": [{"kind": "ecg", "frequency": 10}],
            "anomalies": [
                {
                    "position": "middle",
                    "length": 100,
                    "kinds": [{"kind": "platform", "value": -1}],
                }
            ],
        }
        self.config_single_sine = {"timeseries": [config_sine]}
        self.config_single_ecg = {"timeseries": [config_ecg]}
        self.config_multiple = {"timeseries": [config_sine, config_ecg]}

    def _create_and_generate(self, config: dict, seed: int) -> List[TimeSeries]:
        gutentag = GutenTAG.from_dict(config, seed=seed)
        return gutentag.generate(return_timeseries=True)  # type: ignore  # shouldn't be None and if so raise the error later on

    def _assert_df_equal(
        self, df1: pd.DataFrame, df2: pd.DataFrame, columns: Optional[List[str]] = None
    ) -> None:
        if columns is None:
            columns = np.union1d(df1.columns, df2.columns).tolist()
        for column in columns:
            assert_series_equal(df1[column], df2[column])

    def test_reproducible(self):
        df1 = self._create_and_generate(self.config_single_sine, seed=42)[0].timeseries
        df2 = self._create_and_generate(self.config_single_sine, seed=42)[0].timeseries
        self._assert_df_equal(df1, df2)

    def test_reproducible_diff_config(self):
        df1 = self._create_and_generate(self.config_single_ecg, seed=42)[0].timeseries
        df2 = self._create_and_generate(self.config_multiple, seed=42)[1].timeseries
        self._assert_df_equal(df1, df2)

    def test_independent_of_order(self):
        dfs1 = self._create_and_generate(self.config_multiple, seed=42)
        config2 = deepcopy(self.config_multiple)
        config2["timeseries"] = config2["timeseries"][::-1]
        dfs2 = self._create_and_generate(self.config_multiple, seed=42)
        for df1, df2 in zip(dfs1, dfs2):
            self._assert_df_equal(df1.timeseries, df2.timeseries)

    def test_diff_when_diff_seed(self):
        df1 = self._create_and_generate(self.config_single_ecg, seed=42)[0].timeseries
        df2 = self._create_and_generate(self.config_single_ecg, seed=1)[0].timeseries

        with self.assertRaises(AssertionError):
            self._assert_df_equal(df1, df2)
