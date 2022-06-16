import unittest
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from gutenTAG import GutenTAG


class TestIntegration(unittest.TestCase):
    def _load_config_and_generate(self, config_path: str) -> pd.DataFrame:
        gutenTAG = GutenTAG.from_yaml(Path(config_path), seed=42)
        df_generated = gutenTAG.generate(return_timeseries=True)
        assert df_generated is not None, "DataFrame should have been returned"
        return df_generated[0].timeseries

    def _compare_expected_and_generated(self, config_path: str, expected_path: str, columns: List[str]):
        expected_ts = pd.read_csv(expected_path, index_col="timestamp",
                                  dtype={'value-0': np.float64, 'is_anomaly': np.int8})

        df_generated = self._load_config_and_generate(config_path)
        for column in columns:
            assert_series_equal(df_generated[column], expected_ts[column])
