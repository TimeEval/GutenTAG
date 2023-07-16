import unittest
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
from numpy.random import SeedSequence
from numpy.testing import assert_array_equal

from gutenTAG.base_oscillations.custom_input import CustomInput
from gutenTAG.utils.types import GenerationContext


class TestCustomInput(unittest.TestCase):
    def setUp(self) -> None:
        self.ctx = GenerationContext(SeedSequence(42)).to_bo()
        self.input_path1 = Path("tests/custom_input_ts/dummy_timeseries.csv")
        self.input_path2 = Path("tests/custom_input_ts/dummy_timeseries_2.csv")
        self.input_path_datatypes = Path(
            "tests/custom_input_ts/data_types_timeseries.csv"
        )
        self.column_idx = 1
        self.length = 100
        self.expected_test = (
            pd.read_csv(self.input_path1, usecols=[self.column_idx])
            .iloc[: self.length, 0]
            .values
        )
        self.expected_train = (
            pd.read_csv(self.input_path2, usecols=[self.column_idx])
            .iloc[: self.length, 0]
            .values
        )

    def test_all_args_specified_just_unsupervised(self):
        timeseries = CustomInput(
            supervised=False, semi_supervised=False
        ).generate_only_base(
            ctx=self.ctx,
            length=self.length,
            input_timeseries_path_test=str(self.input_path1),
            use_column_test=self.column_idx,
            input_timeseries_path_train=str(self.input_path2),
            use_column_train=self.column_idx,
        )

        self.assertEqual(len(timeseries), 100)
        assert_array_equal(timeseries, self.expected_test)

    def test_all_args_specified_supervised(self):
        timeseries = CustomInput().generate_only_base(
            ctx=self.ctx,
            length=self.length,
            input_timeseries_path_test=str(self.input_path1),
            use_column_test=self.column_idx,
            input_timeseries_path_train=str(self.input_path2),
            use_column_train=self.column_idx,
            supervised=True,
        )

        self.assertEqual(len(timeseries), 100)
        assert_array_equal(timeseries, self.expected_train)

    def test_all_args_specified_semi_supervised(self):
        timeseries = CustomInput().generate_only_base(
            ctx=self.ctx,
            length=self.length,
            input_timeseries_path_test=str(self.input_path1),
            use_column_test=self.column_idx,
            input_timeseries_path_train=str(self.input_path2),
            use_column_train=self.column_idx,
            semi_supervised=True,
        )

        self.assertEqual(len(timeseries), 100)
        assert_array_equal(timeseries, self.expected_train)

    def test_just_testargs(self):
        timeseries = CustomInput().generate_only_base(
            ctx=self.ctx,
            length=self.length,
            input_timeseries_path_test=str(self.input_path1),
            use_column_test=self.column_idx,
        )

        self.assertEqual(len(timeseries), 100)
        assert_array_equal(timeseries, self.expected_test)

    def test_testfile_none(self):
        with self.assertRaises(ValueError) as e:
            CustomInput().generate_only_base(
                ctx=self.ctx,
                length=self.length,
                use_column_test=1,
            )
        self.assertRegex(str(e.exception).lower(), "no path")

    def test_missing_testfile(self):
        with self.assertRaises(FileNotFoundError):
            CustomInput().generate_only_base(
                ctx=self.ctx,
                length=self.length,
                input_timeseries_path_test="wrong-folder/missing-file.csv",
                use_column_test=1,
            )

    def test_trainfile_none(self):
        with self.assertRaises(ValueError) as e:
            CustomInput().generate_only_base(
                ctx=self.ctx,
                length=self.length,
                input_timeseries_path_test="wrong-folder/missing-file.csv",
                use_column_test=1,
                use_column_train=1,
                supervised=True,
            )
        self.assertRegex(str(e.exception).lower(), "no path.*training timeseries")

    def test_column_names(self):
        kwargs = {
            "input-timeseries-path-test": str(self.input_path1),
            "use-column-test": "value1",
            "input-timeseries-path-train": str(self.input_path2),
            "use-column-train": "value1",
        }
        gen = CustomInput(length=self.length, **kwargs)

        timeseries = gen.generate_only_base(self.ctx)
        self.assertEqual(len(timeseries), 100)
        assert_array_equal(timeseries, self.expected_test)

        timeseries = gen.generate_only_base(self.ctx, supervised=True)
        self.assertEqual(len(timeseries), 100)
        assert_array_equal(timeseries, self.expected_train)

    def test_input_too_short(self):
        with self.assertRaises(ValueError) as e:
            CustomInput().generate_only_base(
                ctx=self.ctx,
                length=10_000,
                input_timeseries_path_test=str(self.input_path1),
                use_column_test=1,
            )
        self.assertRegex(str(e.exception).lower(), "less than the desired length")

    def test_read_floats(self):
        for tpe in ["floats", "nulls"]:
            # a warning will raise an error!
            with warnings.catch_warnings():
                timeseries = CustomInput().generate_only_base(
                    ctx=self.ctx,
                    length=5,
                    input_timeseries_path_test=self.input_path_datatypes,
                    use_column_test=tpe,
                )
            #  data is properly converted
            self.assertEqual(timeseries.dtype, np.float_)

    def test_convert_to_float_with_warning(self):
        for tpe in ["ints", "bools"]:
            with self.assertWarns(UserWarning) as w:
                timeseries = CustomInput().generate_only_base(
                    ctx=self.ctx,
                    length=5,
                    input_timeseries_path_test=self.input_path_datatypes,
                    use_column_test=tpe,
                )
            # warning is raised
            self.assertRegex(str(w.warning), "automatically converted to float")
            #  data is properly converted
            self.assertEqual(timeseries.dtype, np.float_)

    def test_error_on_string_type(self):
        with self.assertRaises(ValueError) as e:
            CustomInput().generate_only_base(
                ctx=self.ctx,
                length=5,
                input_timeseries_path_test=self.input_path_datatypes,
                use_column_test="strings",
            )
        self.assertRegex(str(e.exception), "could not convert string to float")
