from . import TestIntegration


class TestIntegrationBenchmarkGeneration(TestIntegration):
    def test_generates_benchmark_files_without_errors(self):
        self._load_config_and_generate("generation_configs/benchmark-datasets.yaml")
        generated_without_errors = True
        self.assertTrue(generated_without_errors)
