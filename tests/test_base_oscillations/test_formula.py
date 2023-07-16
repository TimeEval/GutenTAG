import unittest

import numpy as np
from numpy.testing import assert_array_equal

from gutenTAG.base_oscillations.formula import FormulaParser  # type: ignore


class TestFormula(unittest.TestCase):
    def test_formula_parser(self):
        prev_channels = [np.arange(10), np.ones(10)]
        d = {
            "base": {"base": 0, "operation": {"kind": "+", "operand": {"base": 0}}},
            "operation": {
                "kind": "*",
                "operand": {"base": 1, "aggregation": {"kind": "sum"}},
            },
        }
        expected = (np.arange(10) + np.arange(10)) * np.ones(10).sum()
        parsed = FormulaParser(d).parse(prev_channels=prev_channels).execute()

        assert_array_equal(expected, parsed)
