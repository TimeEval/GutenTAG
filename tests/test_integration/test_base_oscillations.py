from . import TestIntegration


class TestIntegrationBaseOscillations(TestIntegration):

    def test_generates_single_channel(self):
        self._compare_expected_and_generated("tests/configs/example-config-single.yaml",
                                             "tests/generated/example-ts-single.csv",
                                             ["value-0", "is_anomaly"])

    def test_generates_single_channel_bo_list(self):
        self._compare_expected_and_generated("tests/configs/example-config-single-element.yaml",
                                             "tests/generated/example-ts-single.csv",
                                             ["value-0", "is_anomaly"])

    def test_generates_multi_channel(self):
        self._compare_expected_and_generated("tests/configs/example-config-multi.yaml",
                                             "tests/generated/example-ts-multi.csv",
                                             ["value-0", "value-1", "is_anomaly"])

    def test_generates_multi_channel_bo_list(self):
        self._compare_expected_and_generated("tests/configs/example-config-multi-element.yaml",
                                             "tests/generated/example-ts-multi.csv",
                                             ["value-0", "value-1", "is_anomaly"])

    def test_rmj_bo_list(self):
        self._compare_expected_and_generated("tests/configs/example-config-rmj.yaml",
                                             "tests/generated/example-ts-rmj.csv",
                                             ["value-0", "value-1", "is_anomaly"])

    def test_cbf_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-cbf.yaml",
                                             "tests/generated/example-ts-cbf.csv",
                                             ["value-0", "is_anomaly"])

    def test_rw_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-rw.yaml",
                                             "tests/generated/example-ts-rw.csv",
                                             ["value-0", "is_anomaly"])

    def test_ecg_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-ecg.yaml",
                                             "tests/generated/example-ts-ecg.csv",
                                             ["value-0", "is_anomaly"])

    def test_polynomial_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-polynomial.yaml",
                                             "tests/generated/example-ts-polynomial.csv",
                                             ["value-0", "is_anomaly"])

    def test_trend_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-trend.yaml",
                                             "tests/generated/example-ts-trend.csv",
                                             ["value-0", "is_anomaly"])

    def test_formula_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-formula.yaml",
                                             "tests/generated/example-ts-formula.csv",
                                             ["value-0", "is_anomaly"])

    def test_cosine_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-cosine.yaml",
                                             "tests/generated/example-ts-cosine.csv",
                                             ["value-0", "is_anomaly"])
