from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Union, Callable, Sequence, Tuple, Any

import yaml
from joblib import Parallel, delayed
from tqdm import tqdm

from .addons import import_addons, AddOnProcessContext, AddOnFinalizeContext, BaseAddOn
from .config import ConfigParser, ConfigValidator
from .generator import Overview, TimeSeries
from .timeseries import TrainingType, TimeSeries as ExtTimeSeries
from .utils.global_variables import UNSUPERVISED_FILENAME, SUPERVISED_FILENAME, SEMI_SUPERVISED_FILENAME
from .utils.tqdm_joblib import tqdm_joblib


@dataclass
class _GenerationContext:
    plot: bool = False
    return_timeseries: bool = False
    output_folder: Optional[os.PathLike] = None
    seed: Optional[int] = None
    addons: Sequence[BaseAddOn] = ()

    def to_addon_process_ctx(self, timeseries: TimeSeries, config: Dict) -> AddOnProcessContext:
        return AddOnProcessContext(
            timeseries=timeseries,
            config=config,
            plot=self.plot,
            output_folder=self.output_folder,
        )


class GutenTAG:
    def __init__(self,
                 n_jobs: int = 1,
                 seed: Optional[int] = None,
                 addons: Sequence[str] = ()):
        self._overview = Overview()
        self._timeseries: List[TimeSeries] = []
        self._n_jobs = n_jobs
        # remove duplicate addons
        self._registered_addons: List[str] = []
        for addon in addons:
            self.use_addon(addon)
        self._overview.add_seed(seed)
        self.seed = seed
        self.addons: Dict[str, BaseAddOn] = {}

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
        if addon not in self._registered_addons:
            if insert_location == "last":
                self._registered_addons.append(addon)
            elif insert_location == "first":
                self._registered_addons = [addon] + self._registered_addons
            elif isinstance(insert_location, int):
                self._registered_addons.insert(insert_location, addon)
            else:
                ValueError(f"insert_position={insert_location} unknown!")
        else:
            ValueError(f"'{addon}' already loaded at position {self._registered_addons.index(addon)}")
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

        # prepare
        folder: Optional[Path] = None
        if output_folder is not None:
            folder = Path(output_folder)
            folder.mkdir(exist_ok=True)

        addon_types = import_addons(list(self._registered_addons))
        addons = [addon() for addon in tqdm(addon_types, desc="Initializing addons", total=len(addon_types))]
        for name, addon in zip(self._registered_addons, addons):
            self.addons[name] = addon

        # process time series
        ctx = _GenerationContext(
            plot=plot,
            output_folder=output_folder,
            seed=self.seed,
            addons=addons,
            return_timeseries=return_timeseries,
        )
        with tqdm_joblib(tqdm(desc="Generating datasets", total=len(self._timeseries))):
            results: List[Tuple[Dict, Dict[str, Any], Optional[List[ExtTimeSeries]]]] = Parallel(n_jobs=n_jobs)(
                delayed(self.internal_generate)(ctx, ts, config)
                for ts, config in zip(self._timeseries, self._overview.datasets)
            )
        configs, data_dicts, timeseries_datasets = tuple(zip(*results))
        self._overview.datasets = configs

        # finalize
        if folder is not None:
            self._overview.save_to_output_dir(folder)
        finalize_ctx = AddOnFinalizeContext(
            overview=self._overview,
            plot=plot,
            output_folder=output_folder
        )
        finalize_ctx.fill_store(data_dicts)
        for addon in tqdm(addons, desc="Finalizing addons", total=len(addons)):
            addon.finalize(finalize_ctx)

        if return_timeseries and timeseries_datasets is not None:
            return [d for dataset in timeseries_datasets for d in dataset]
        return None

    @staticmethod
    def internal_generate(ctx: _GenerationContext, ts: TimeSeries, config: Dict) -> Tuple[Dict, Dict[str, Any], Optional[List[ExtTimeSeries]]]:
        ts.generate(ctx.seed)
        addon_ctx = ctx.to_addon_process_ctx(ts, config)
        for addon in ctx.addons:
            addon_ctx = addon.process(addon_ctx)
        ts = addon_ctx.timeseries
        config = addon_ctx.config
        data = addon_ctx._data_store

        if ctx.plot:
           ts.plot()


        if ctx.output_folder is not None:
            GutenTAG.save_timeseries(ts, ctx.output_folder)

        if ctx.return_timeseries:
            return config, data, ts.to_datasets()
        return config, data, None

    @staticmethod
    def save_timeseries(ts: TimeSeries, output_dir: os.PathLike) -> None:
        name = ts.dataset_name
        dataset_folder = Path(output_dir) / name
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
