import unittest
from typing import List

import numpy as np
import pandas as pd
import yaml
from pandas.testing import assert_series_equal

from gutenTAG import GutenTAG


class TestIntegration(unittest.TestCase):
    def _load_config_and_generate(self, config_path: str) -> pd.DataFrame:
        with open(config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        gutenTAG = GutenTAG.from_dict(config)
        gutenTAG.seed = 42
        df_generated = gutenTAG.generate(True)
        assert df_generated is not None, "DataFrame should have been returned"
        return df_generated[0]

    def _compare_expected_and_generated(self, config_path: str, expected_path: str, columns: List[str]):
        expected_ts = pd.read_csv(expected_path, index_col="timestamp",
                                  dtype={'value-0': np.float64, 'is_anomaly': np.int8})

        df_generated = self._load_config_and_generate(config_path)
        for column in columns:
            assert_series_equal(df_generated[column], expected_ts[column])
