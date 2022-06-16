import importlib
import os
from dataclasses import dataclass
from typing import List, Type, Optional

from ..generator import Overview, TimeSeries


@dataclass
class AddOnProcessContext:
    overview: Overview
    datasets: List[TimeSeries]
    plot: bool = False
    output_folder: Optional[os.PathLike] = None
    n_jobs: int = 1

    @property
    def should_save(self) -> bool:
        return self.output_folder is not None


class BaseAddOn:
    def process(self,
                ctx: AddOnProcessContext,
                gutenTAG: 'GutenTAG') -> AddOnProcessContext:  # type: ignore  # to prevent circular import
        """Gets called after time series are generated but before they are plotted or written to disk."""
        return ctx


def import_addons(addons: List[str]) -> List[Type[BaseAddOn]]:
    module_classes = [addon.rsplit(".", 1) for addon in addons]

    classes = [importlib.import_module(package).__dict__[cls] for package, cls in module_classes]
    return [cls for cls in classes if issubclass(cls, BaseAddOn)]
