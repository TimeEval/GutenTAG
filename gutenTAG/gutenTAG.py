from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import List, Dict, Optional, Union, Callable, Sequence

import yaml
from joblib import Parallel, delayed
from tqdm import tqdm

from .addons import import_addons, AddOnProcessContext
from .config.parser import ConfigParser
from .config.validator import ConfigValidator
from .generator.overview import Overview
from .generator.timeseries import TimeSeries
from .timeseries import TrainingType, TimeSeries as ExtTimeSeries
from .utils.global_variables import UNSUPERVISED_FILENAME, SUPERVISED_FILENAME, SEMI_SUPERVISED_FILENAME
from .utils.tqdm_joblib import tqdm_joblib


class GutenTAG:
    def __init__(self,
                 n_jobs: int = 1,
                 seed: Optional[int] = None,
                 addons: Sequence[str] = ()):
        self._overview = Overview()
        self._timeseries: List[TimeSeries] = []
        self._n_jobs = n_jobs
        # remove duplicate addons
        self._addons: List[str] = []
        for addon in addons:
            self.use_addon(addon)
        self._overview.add_seed(seed)
        self.seed = seed

    def load_config_json(self, json_config_path: os.PathLike, only: Optional[str] = None) -> GutenTAG:
        with open(json_config_path, "r") as f:
            config = json.load(f)
        return self.load_config_dict(config, only)

    def load_config_yaml(self, yaml_config_path: os.PathLike, only: Optional[str] = None) -> GutenTAG:
        with open(yaml_config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return self.load_config_dict(config, only)

    def load_config_dict(self, config: Dict, only: Optional[str] = None) -> GutenTAG:
        # First parse, then validate config, because our own error messages are more precise than
        # the validator's ones.
        config_parser = ConfigParser(only=only)
        timeseries = []
        for base_oscillations, anomalies, options, ts_config in config_parser.parse(config):
            ts = TimeSeries(base_oscillations, anomalies, **options.to_dict())
            timeseries.append(ts)
        ConfigValidator().validate(config)

        self._timeseries.extend(timeseries)
        self._overview.add_datasets(config_parser.raw_ts_configs)
        return self

    def remove_by_name(self, name: Union[str, Callable[[str], bool]]) -> GutenTAG:
        if isinstance(name, str):
            self._timeseries = [ts for ts in self._timeseries if ts.dataset_name != name]
        else:
            self._timeseries = [ts for ts in self._timeseries if not name(ts.dataset_name)]
        self._overview.remove_dataset_by_name(name)
        return self

    def use_addon(self, addon: str, insert_location: Union[str, int] = "last") -> GutenTAG:
        if addon not in self._addons:
            if insert_location == "last":
                self._addons.append(addon)
            elif insert_location == "first":
                self._addons = [addon] + self._addons
            elif isinstance(insert_location, int):
                self._addons.insert(insert_location, addon)
            else:
                ValueError(f"insert_position={insert_location} unknown!")
        else:
            ValueError(f"'{addon}' already loaded at position {self._addons.index(addon)}")
        return self

    def generate(self,
                 return_timeseries: bool = False,
                 output_folder: Optional[os.PathLike] = None,
                 plot: bool = False) -> Optional[List[ExtTimeSeries]]:
        n_jobs = self._n_jobs
        if n_jobs != 1 and plot:
            warnings.warn(
                f"Cannot generate time series in parallel while plotting ('n_jobs' was set to {n_jobs})! Falling "
                f"back to serial generation.")
            n_jobs = 1
        with tqdm_joblib(tqdm(desc="Generating datasets", total=len(self._timeseries))):
            self._timeseries = Parallel(n_jobs=n_jobs)(
                delayed(ts.generate)(self.seed) for ts in self._timeseries
            )

        addons = import_addons(list(self._addons))
        ctx = AddOnProcessContext(
            overview=self._overview,
            datasets=self._timeseries,
            output_folder=output_folder,
            plot=plot,
            n_jobs=n_jobs
        )
        for addon in tqdm(addons, desc="Executing addons", total=len(self._addons)):
            ctx = addon().process(ctx, gutenTAG=self)
        self._overview = ctx.overview
        self._timeseries = ctx.datasets
        plot = ctx.plot

        if plot:
            for ts in tqdm(self._timeseries, desc="Plotting datasets", total=len(self._timeseries)):
                ts.plot()

        if output_folder is not None:
            self.save_timeseries(output_folder)

        if return_timeseries:
            return [d for ts in self._timeseries for d in ts.to_datasets()]
        return None

    def save_timeseries(self, output_dir: os.PathLike):
        folder = Path(output_dir)
        folder.mkdir(exist_ok=True)
        self._overview.save_to_output_dir(folder)

        for i, ts in tqdm(enumerate(self._timeseries), desc="Saving datasets to disk", total=len(self._timeseries)):
            name = ts.dataset_name or str(i)
            dataset_folder = folder / name
            dataset_folder.mkdir(exist_ok=True)

            ts.to_csv(dataset_folder / UNSUPERVISED_FILENAME, TrainingType.TEST)

            if ts.supervised:
                ts.to_csv(dataset_folder / SUPERVISED_FILENAME, TrainingType.TRAIN_ANOMALIES)

            if ts.semi_supervised:
                ts.to_csv(dataset_folder / SEMI_SUPERVISED_FILENAME, TrainingType.TRAIN_NO_ANOMALIES)

    @staticmethod
    def from_json(path: os.PathLike,
                  n_jobs: int = 1,
                  seed: Optional[int] = None,
                  addons: Sequence[str] = (),
                  only: Optional[str] = None) -> GutenTAG:
        gt = GutenTAG(n_jobs=n_jobs, seed=seed, addons=addons)
        return gt.load_config_json(path, only=only)

    @staticmethod
    def from_yaml(path: os.PathLike,
                  n_jobs: int = 1,
                  seed: Optional[int] = None,
                  addons: Sequence[str] = (),
                  only: Optional[str] = None) -> GutenTAG:
        gt = GutenTAG(n_jobs=n_jobs, seed=seed, addons=addons)
        return gt.load_config_yaml(path, only=only)

    @staticmethod
    def from_dict(config: Dict,
                  n_jobs: int = 1,
                  seed: Optional[int] = None,
                  addons: Sequence[str] = (),
                  only: Optional[str] = None) -> GutenTAG:
        gt = GutenTAG(n_jobs=n_jobs, seed=seed, addons=addons)
        return gt.load_config_dict(config, only=only)
