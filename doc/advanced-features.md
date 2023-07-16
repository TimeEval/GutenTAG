# Advanced Features

## Add-Ons

GutenTAG has a simple add-on feature which can be activated by using the [CLI](usage#from-cli).

### Definition

An add-on can be written and defined with the help of the [`BaseAddOn`](../gutenTAG/addons/__init__.py) class.
This class defines two methods, that are called after the CLI tool has already saved the time series to disk:

```python
import os
from typing import List, Optional
from dataclasses import dataclass
from gutenTAG import GutenTAG
from gutenTAG.generator import Overview, TimeSeries


@dataclass
class AddOnProcessContext:
    overview: Overview
    datasets: List[TimeSeries]
    plot: bool = False
    output_folder: Optional[os.PathLike] = None
    n_jobs: int = 1

class BaseAddOn:
    def process(self, ctx: AddOnProcessContext, gutenTAG: GutenTAG) -> AddOnProcessContext:
        """Gets called after time series are generated but before they are plotted or written to disk."""
        return ctx
```

### Implemented Add-Ons

GutenTAG already comes with an add-on for the TimeEval [^1] [^2] tool. This add-on creates a `datasets.csv` meta-file in the output directory. This file is necessary to import the generated datasets into the TimeEval tool. Use it as follows:

```shell
python -m gutenTAG --config-yaml config.yaml --addons gutenTAG.addons.timeeval.TimeEvalAddOn
```

[^1]: HPI Gitlab: https://gitlab.hpi.de/akita/bp2020fn1/timeeval/

[^2]: HPI Github: https://github.com/HPI-Information-Systems/timeeval
