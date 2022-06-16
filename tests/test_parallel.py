import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from pandas._testing import assert_series_equal

from gutenTAG import GutenTAG


class TestParallel(unittest.TestCase):
    def test_seeded_parallel(self):
        expected_ts = pd.read_csv("tests/generated/example-ts-multi.csv",
                                  index_col="timestamp",
                                  dtype={'value-0': np.float64, 'is_anomaly': np.int8})
        gutenTAG = GutenTAG.from_yaml(Path("tests/configs/example-config-multi.yaml"), seed=42, n_jobs=-1)
        df_generated = gutenTAG.generate(return_timeseries=True)
        assert df_generated is not None, "DataFrame should have been returned"
        df = df_generated[0].timeseries
        for column in ["value-0", "value-1", "is_anomaly"]:
            assert_series_equal(df[column], expected_ts[column])
