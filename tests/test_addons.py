import unittest
import numpy as np
import yaml
import random

from gutenTAG import GutenTAG
from gutenTAG.addons.timeeval import TimeEvalAddOn
from gutenTAG.__main__ import parse_args


class TestAddons(unittest.TestCase):
    def setUp(self) -> None:
        seed = 42
        np.random.seed(seed)
        random.seed(seed)

    def test_timeeval_addon_rmj(self):
        with open("tests/configs/example-config-rmj.yaml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        args = parse_args(["--config-yaml", "", "--no-save"])
        gutentag = GutenTAG.from_dict(config)
        gutentag.generate()
        addon = TimeEvalAddOn()
        addon.process(overview=gutentag.overview, gutenTAG=gutentag, args=args)
        df = addon.df
        self.assertEqual(df["dataset_name"][0], "rmj.unsupervised")
        self.assertEqual(df["test_path"][0], "rmj/test.csv")
        self.assertEqual(df["input_type"][0], "multivariate")
        self.assertEqual(df["length"][0], 1000)
        self.assertEqual(df["dimensions"][0], 2)
        self.assertEqual(df["contamination"][0], 0.02)
        self.assertEqual(df["num_anomalies"][0], 1)
        self.assertEqual(df["min_anomaly_length"][0], 20)
        self.assertEqual(df["median_anomaly_length"][0], 20)
        self.assertEqual(df["max_anomaly_length"][0], 20, 2)
        self.assertEqual(df["train_type"][0], "unsupervised")
        self.assertAlmostEqual(df["mean"][0], 0, 1)
        self.assertAlmostEqual(df["stddev"][0], 0, 1)
        self.assertTrue(np.isnan(df["trend"][0]))
        self.assertEqual(df["period_size"][0], 20)

    def test_timeeval_addon_sine(self):
        with open("tests/configs/example-config-ecg.yaml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        args = parse_args(["--config-yaml", "", "--no-save"])
        gutentag = GutenTAG.from_dict(config)
        gutentag.generate()
        addon = TimeEvalAddOn()
        addon.process(overview=gutentag.overview, gutenTAG=gutentag, args=args)
        df = addon.df
        self.assertEqual(df["dataset_name"][0], "ecg.unsupervised")
        self.assertEqual(df["test_path"][0], "ecg/test.csv")
        self.assertEqual(df["input_type"][0], "univariate")
        self.assertEqual(df["length"][0], 1000)
        self.assertEqual(df["dimensions"][0], 1)
        self.assertEqual(df["contamination"][0], 0.04)
        self.assertEqual(df["num_anomalies"][0], 1)
        self.assertEqual(df["min_anomaly_length"][0], 40)
        self.assertEqual(df["median_anomaly_length"][0], 40)
        self.assertEqual(df["max_anomaly_length"][0], 40, 2)
        self.assertEqual(df["train_type"][0], "unsupervised")
        self.assertAlmostEqual(df["mean"][0], 0.5, 2)
        self.assertAlmostEqual(df["stddev"][0], 0, 1)
        self.assertTrue(np.isnan(df["trend"][0]))
        self.assertEqual(df["period_size"][0], 10)
