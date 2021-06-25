import os
from typing import List, Dict
import yaml


class Overview:
    FILENAME = "overview.yaml"

    def __init__(self):
        self.datasets: List[Dict] = []

    def add_dataset(self, config: Dict):
        self.datasets.append(config)

    def save_to_output_dir(self, path: os.PathLike):
        overview = dict()
        overview["generated-timeseries"] = []
        for i, dataset in enumerate(self.datasets):
            dataset["generation-id"] = dataset.get("base-oscillation", {}).get("title", i)
            overview["generated-timeseries"].append(dataset)
        with open(os.path.join(path, self.FILENAME), "w") as f:
            yaml.dump(overview, f)
