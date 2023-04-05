from . import TestIntegration


class TestIntegrationAnomalyTypes(TestIntegration):
    def test_pattern_sinusoid_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-pattern.yaml",
                                             "tests/generated/example-ts-pattern.csv",
                                             ["value-0", "is_anomaly"])

    def test_extremum_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-extremum.yaml",
                                             "tests/generated/example-ts-extremum.csv",
                                             ["value-0", "is_anomaly"])

    def test_amplitude_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-amplitude.yaml",
                                             "tests/generated/example-ts-amplitude.csv",
                                             ["value-0", "is_anomaly"])

    def test_trend_anomaly_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-trend-anomaly.yaml",
                                             "tests/generated/example-ts-trend-anomaly.csv",
                                             ["value-0", "is_anomaly"])

    def test_creeping_amplitude_anomaly_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-creeping-amplitude.yaml",
                                             "tests/generated/example-ts-creeping-amplitude.csv",
                                             ["value-0", "is_anomaly"])

    def test_creeping_mean_anomaly_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-creeping-mean.yaml",
                                             "tests/generated/example-ts-creeping-mean.csv",
                                             ["value-0", "is_anomaly"])

    def test_creeping_variance_anomaly_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-creeping-variance.yaml",
                                             "tests/generated/example-ts-creeping-variance.csv",
                                             ["value-0", "is_anomaly"])

    def test_creeping_variance_transition_anomaly_from_config(self):
        self._compare_expected_and_generated("tests/configs/example-config-creeping-variance-transition.yaml",
                                             "tests/generated/example-ts-creeping-variance-transition.csv",
                                             ["value-0", "is_anomaly"])
