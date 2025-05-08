import unittest
from pathlib import Path

import numpy as np

from gutenTAG import GutenTAG
from gutenTAG.addons import (
    AddOnProcessContext,
    AddOnFinalizeContext,
    BaseAddOn,
    import_addons,
)
from gutenTAG.addons.timeeval import TimeEvalAddOn


class TestAddons(unittest.TestCase):
    @staticmethod
    def _execute_addon(gutentag: GutenTAG, addon: BaseAddOn):
        states = []
        for ts, config in zip(gutentag._timeseries, gutentag._overview.datasets):
            ctx = addon.process(AddOnProcessContext(timeseries=ts, config=config))
            states.append(ctx._data_store)
        finalize_ctx = AddOnFinalizeContext(overview=gutentag._overview)
        finalize_ctx.fill_store(states)
        addon.finalize(finalize_ctx)

    def test_import_builtin_addon(self):
        addons = import_addons(["TimeEvalAddOn"])
        self.assertEqual(len(addons), 1)

    def test_import_absolute_path_addon(self):
        addons = import_addons(["gutenTAG.addons.timeeval.TimeEvalAddOn"])
        self.assertEqual(len(addons), 1)

    def test_import_unknown_package(self):
        with self.assertRaises(ValueError) as ex:
            import_addons(["gutenTAG.unknownpackage.TimeEvalAddOn"])
        self.assertRegex(str(ex.exception), r"Package .* could not be loaded")

    def test_import_unknown_class(self):
        with self.assertRaises(ValueError) as ex:
            import_addons(["gutenTAG.addons.timeeval.TimeEvalAddOn2"])
        self.assertRegex(str(ex.exception), r"AddOn .* not found")

    def test_import_wrong_inheritance(self):
        with self.assertRaises(ValueError) as ex:
            import_addons(["gutenTAG.addons.AddOnFinalizeContext"])
        self.assertRegex(str(ex.exception), r"is not a compatible AddOn")

    def test_timeeval_addon_rmj(self):
        gutentag = GutenTAG.from_yaml(
            Path("tests/configs/example-config-rmj.yaml"), seed=42
        )
        gutentag.generate()
        addon = TimeEvalAddOn()
        self._execute_addon(gutentag, addon)
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
        self.assertAlmostEqual(df["mean"][0], -0.06, 2)
        self.assertAlmostEqual(df["stddev"][0], 0.02, 2)
        self.assertTrue(np.isnan(df["trend"][0]))
        self.assertEqual(df["period_size"][0], 20)

    def test_timeeval_addon_sine(self):
        gutentag = GutenTAG.from_yaml(
            Path("tests/configs/example-config-ecg.yaml"), seed=42
        )
        gutentag.generate()
        addon = TimeEvalAddOn()
        self._execute_addon(gutentag, addon)
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
        self.assertAlmostEqual(df["mean"][0], 0.50, 2)
        self.assertAlmostEqual(df["stddev"][0], 0.00, 2)
        self.assertTrue(np.isnan(df["trend"][0]))
        self.assertEqual(df["period_size"][0], 10)

    def test_timeeval_addon_complex(self):
        gutentag = GutenTAG.from_yaml(
            Path("tests/configs/example-config-complex.yaml"), seed=42
        )
        gutentag.generate()
        addon = TimeEvalAddOn()
        self._execute_addon(gutentag, addon)
        df = addon.df
        self.assertEqual(len(df), 3)
        self.assertEqual(df["dataset_name"][0], "bo-dict.unsupervised")
        self.assertEqual(df["test_path"][0], "bo-dict/test.csv")
        self.assertTrue(np.isnan(df["train_path"][0]))
        self.assertEqual(df["input_type"][0], "univariate")
        self.assertEqual(df["length"][0], 1000)
        self.assertEqual(df["dimensions"][0], 1)
        self.assertEqual(df["contamination"][0], 0.02)
        self.assertEqual(df["num_anomalies"][0], 1)
        self.assertEqual(df["min_anomaly_length"][0], 20)
        self.assertEqual(df["median_anomaly_length"][0], 20)
        self.assertEqual(df["max_anomaly_length"][0], 20, 2)
        self.assertEqual(df["train_type"][0], "unsupervised")
        self.assertTrue(np.isnan(df["trend"][0]))
        self.assertEqual(df["period_size"][0], 50)

        self.assertEqual(df["dataset_name"][1], "bo-dict.semi-supervised")
        self.assertEqual(df["test_path"][1], "bo-dict/test.csv")
        self.assertEqual(df["train_path"][1], "bo-dict/train_no_anomaly.csv")
        self.assertEqual(df["input_type"][1], "univariate")
        self.assertEqual(df["length"][1], 1000)
        self.assertEqual(df["dimensions"][1], 1)
        self.assertEqual(df["contamination"][1], 0.02)
        self.assertEqual(df["num_anomalies"][1], 1)
        self.assertEqual(df["min_anomaly_length"][1], 20)
        self.assertEqual(df["median_anomaly_length"][1], 20)
        self.assertEqual(df["max_anomaly_length"][1], 20, 2)
        self.assertEqual(df["train_type"][1], "semi-supervised")
        self.assertTrue(np.isnan(df["trend"][1]))
        self.assertEqual(df["period_size"][1], 50)

        self.assertEqual(df["dataset_name"][2], "bo-list.unsupervised")
        self.assertEqual(df["test_path"][2], "bo-list/test.csv")
        self.assertTrue(np.isnan(df["train_path"][2]))
        self.assertEqual(df["input_type"][2], "multivariate")
        self.assertEqual(df["length"][2], 1000)
        self.assertEqual(df["dimensions"][2], 2)
        self.assertEqual(df["contamination"][2], 0.02)
        self.assertEqual(df["num_anomalies"][2], 1)
        self.assertEqual(df["min_anomaly_length"][2], 20)
        self.assertEqual(df["median_anomaly_length"][2], 20)
        self.assertEqual(df["max_anomaly_length"][2], 20, 2)
        self.assertEqual(df["train_type"][2], "unsupervised")
        self.assertTrue(np.isnan(df["trend"][2]))
        self.assertEqual(df["period_size"][2], 50)

    def test_timeeval_addon_without_period(self):
        gutentag = GutenTAG.from_yaml(Path("tests/configs/example-config-rw.yaml"))
        gutentag.generate()
        addon = TimeEvalAddOn()
        self._execute_addon(gutentag, addon)
        df = addon.df
        self.assertTrue(np.isnan(df["period_size"][0]))
