from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from typing import List, Type, Optional, Any, Dict

from ..generator import Overview, TimeSeries


@dataclass
class AddOnProcessContext:
    timeseries: TimeSeries
    config: Dict
    plot: bool = False
    output_folder: Optional[os.PathLike] = None

    _data_store: Dict[str, Any] = field(default_factory=lambda: {})

    @property
    def should_save(self) -> bool:
        return self.output_folder is not None

    def copy(self, timeseries: Optional[TimeSeries] = None, config: Optional[Dict] = None) -> AddOnProcessContext:
        return AddOnProcessContext(
            timeseries=timeseries or self.timeseries,
            config=config or self.config,
            plot=self.plot,
            output_folder=self.output_folder,
        )

    def store_data(self, key: str, data: Any) -> AddOnProcessContext:
        ctx = self.copy()
        ctx._data_store[key] = data
        return ctx


@dataclass
class AddOnFinalizeContext:
    overview: Overview
    plot: bool = False
    output_folder: Optional[os.PathLike] = None

    _data_store: Dict[str, List[Any]] = field(default_factory=lambda: {})

    @property
    def should_save(self) -> bool:
        return self.output_folder is not None

    def get_data(self, key: str) -> List[Any]:
        return self._data_store[key]

    def fill_store(self, stores: List[Dict[str, Any]]) -> None:
        """**Don't use!** Internal API."""
        for dd in stores:
            for key in dd:
                if key not in self._data_store:
                    self._data_store[key] = []
                self._data_store[key].append(dd[key])


class BaseAddOn:
    def process(self, ctx: AddOnProcessContext) -> AddOnProcessContext:
        """Gets called after a time series is generated but before they are plotted or written to disk."""
        return ctx

    def finalize(self, ctx: AddOnFinalizeContext) -> None:
        pass


def import_addons(addons: List[str]) -> List[Type[BaseAddOn]]:
    module_classes = [addon.rsplit(".", 1) for addon in addons]

    classes = [importlib.import_module(package).__dict__[cls] for package, cls in module_classes]
    return [cls for cls in classes if issubclass(cls, BaseAddOn)]
