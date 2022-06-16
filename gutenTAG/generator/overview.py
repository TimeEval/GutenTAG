import os
from typing import List, Dict, Optional, Any, Callable, Union

import git
import yaml


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

    def add_seed(self, seed: Optional[int]) -> None:
        self.seed = seed

    def add_dataset(self, config: Dict) -> None:
        self.datasets.append(config)

    def add_datasets(self, configs: List[Dict]) -> None:
        self.datasets.extend(configs)

    def remove_dataset_by_name(self, name: Union[str, Callable[[str], bool]]) -> None:
        if isinstance(name, str):
            self.datasets = [d for d in self.datasets if d["name"] != name]
        else:
            self.datasets = [d for d in self.datasets if not name(d["name"])]

    def save_to_output_dir(self, path: os.PathLike) -> None:
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
