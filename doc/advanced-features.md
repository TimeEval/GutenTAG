# Advanced Features

## Add-Ons

GutenTAG has a simple add-on feature which can be activated by using the [CLI](usage#from-cli). 

### Definition

An add-on can be written and defined with the help of the [`BaseAddOn`](../gutenTAG/addons/__init__.py) class. This class defines two methods, that are called after the CLI tool has already saved the time series to disk:

```python
import argparse

from typing import Tuple
from gutenTAG import GutenTAG
from gutenTAG.generator import Overview


class BaseAddOn:
    def process(self, overview: Overview, gutenTAG: GutenTAG, args: argparse.Namespace) -> Tuple[Overview, GutenTAG]:
        """Gets called before `process_generators`"""
        return overview, gutenTAG
```

### Implemented Add-Ons

GutenTAG already comes with an add-on for the TimeEval [^1] [^2] tool. This add-on creates a `datasets.csv` meta-file in the output directory. This file is necessary to import the generated datasets into the TimeEval tool. Use it as follows:

```shell
python -m gutenTAG --config-yaml config.yaml --addons gutenTAG.addons.timeeval.TimeEvalAddOn
```

[^1]: HPI Gitlab: https://gitlab.hpi.de/akita/bp2020fn1/timeeval/

[^2]: HPI Github: https://github.com/HPI-Information-Systems/timeeval
