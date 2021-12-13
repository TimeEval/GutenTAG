import os
from typing import List, Dict, Optional, Any
import yaml
import git


class Overview:
    FILENAME = "overview.yaml"
    GUTENTAG_LINK = "https://gitlab.hpi.de/akita/guten-tag"

    def __init__(self):
        self.datasets: List[Dict] = []
        self.seed: Optional[int] = None

        try:
            self.git_commit_sha = git.Repo(search_parent_directories=True).head.object.hexsha
        except git.InvalidGitRepositoryError:
            self.git_commit_sha = None

    def add_seed(self, seed: int):
        self.seed = seed

    def add_dataset(self, config: Dict):
        self.datasets.append(config)

    def add_datasets(self, configs: List[Dict]):
        self.datasets.extend(configs)

    def save_to_output_dir(self, path: os.PathLike):
        overview: Dict[str, Any] = dict()
        overview["generated-timeseries"] = []
        for i, dataset in enumerate(self.datasets):
            dataset["generation-id"] = dataset.get("base_oscillation", {}).get("title", i)
            overview["generated-timeseries"].append(dataset)

        overview["meta"] = {}
        overview["meta"]["seed"] = self.seed
        overview["meta"]["git_commit_sha"] = self.git_commit_sha
        overview["meta"]["download_link"] = self.GUTENTAG_LINK

        with open(os.path.join(path, self.FILENAME), "w") as f:
            yaml.dump(overview, f)
