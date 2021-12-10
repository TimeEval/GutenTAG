from __future__ import annotations
import os
import json
from pathlib import Path

import yaml
import pandas as pd
from typing import List, Dict, Optional

from joblib import Parallel, delayed
from tqdm import tqdm

from .overview import Overview
from .timeseries import TimeSeries, TrainingType
from .parser import ConfigParser
from ..utils.global_variables import UNSUPERVISED_FILENAME, SUPERVISED_FILENAME, SEMI_SUPERVISED_FILENAME
from ..utils.tqdm_joblib import tqdm_joblib


class GutenTAG:
    def __init__(self, n_jobs: int = 1):
        self.overview = Overview()
        self.timeseries: List[TimeSeries] = []
        self.n_jobs = n_jobs

    def add_timeseries(self, ts: TimeSeries):
        self.timeseries.append(ts)

    def add_configs_to_overview(self, configs: List[Dict]):
        self.overview.add_datasets(configs)

    def generate(self, return_dataframe: bool = False) -> Optional[List[pd.DataFrame]]:
        with tqdm_joblib(tqdm(desc="Generating datasets", total=len(self.timeseries))):
            func = lambda ts: ts.generate_with_dataframe if return_dataframe else ts.generate

            dfs = Parallel(n_jobs=self.n_jobs)(
                delayed(func(ts))() for ts in self.timeseries
            )

        if return_dataframe:
            return dfs
        return None

    def save_timeseries(self, output_dir: Path):
        output_dir.mkdir(exist_ok=True)
        self.overview.save_to_output_dir(output_dir)

        for i, ts in tqdm(enumerate(self.timeseries), desc="Saving datasets to disk", total=len(self.timeseries)):
            title = ts.dataset_name or str(i)
            save_dir = output_dir / title
            save_dir.mkdir(exist_ok=True)

            ts.to_csv(save_dir / UNSUPERVISED_FILENAME, TrainingType.TEST)

            if ts.supervised:
                ts.to_csv(save_dir / SUPERVISED_FILENAME, TrainingType.TRAIN_ANOMALIES)

            if ts.semi_supervised:
                ts.to_csv(save_dir / SEMI_SUPERVISED_FILENAME, TrainingType.TRAIN_NO_ANOMALIES)

    @staticmethod
    def from_json(path: os.PathLike, plot: bool = False) -> GutenTAG:
        with open(path, "r") as f:
            config = json.load(f)
        return GutenTAG.from_dict(config, plot)

    @staticmethod
    def from_yaml(path: os.PathLike, plot: bool = False, only: Optional[str] = None) -> GutenTAG:
        with open(path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return GutenTAG.from_dict(config, plot, only)

    @staticmethod
    def from_dict(config: Dict, plot: bool = False, only: Optional[str] = None) -> GutenTAG:
        gutentag = GutenTAG()
        config_parser = ConfigParser(plot, only)
        for base_oscillations, anomalies, options in config_parser.parse(config):
            ts = TimeSeries(base_oscillations, anomalies, **options.to_dict())
            gutentag.add_timeseries(ts)
        gutentag.add_configs_to_overview(config_parser.raw_ts)
        return gutentag
