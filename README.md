# GutenTAG

<img src="logo_transparent.png" alt="GutenTAG logo" width="400px" align="middle"/>

A good **T**imeseries **A**nomaly **G**enerator.

GutenTAG is an extensible tool to generate time series datasets with and without anomalies.
A GutenTAG time series consists of a single (univariate) or multiple (multivariate) channels containing a base osciallation with different anomalies at different positions and of different kinds.

## tl;dr

The following call uses the [`example-config.yaml`](generation_configs/example-config.yaml) configuration file to generate a single time series with two anomalies in the middle and the end of the series.

```bash
python -m gutenTAG --config-yaml generation_configs/example-config.yaml --seed 11 --no-save --plot
```

![Example unsupervised time series with two anomalies](example-ts.png)

## Installation

```bash
# clone GutenTAG repository or extract the archive
git clone git@gitlab.hpi.de:akita/guten-tag.git #or unzip guten-tag.zip
cd guten-tag

# (optionally) create a new conda environment with Python 3
conda create -n gutentag python=3
conda activate gutentag

# install dependencies
pip install -r requirements.txt

# test installation
python -m gutenTAG
```

Test the installation with `python -m gutenTAG` and you should see the greeting and usage instructions:

```plain
$ python -m gutenTAG

                      Welcome to

       _____       _          _______       _____ _
      / ____|     | |        |__   __|/\   / ____| |
     | |  __ _   _| |_ ___ _ __ | |  /  \ | |  __| |
     | | |_ | | | | __/ _ \ '_ \| | / /\ \| | |_ | |
     | |__| | |_| | ||  __/ | | | |/ ____ \ |__| |_|
      \_____|\__,_|\__\___|_| |_|_/_/    \_\_____(_)

"Good day!" wishes your friendly Timeseries Anomaly Generator.



usage: __main__.py [-h] --config-yaml CONFIG_YAML [--output-dir OUTPUT_DIR] [--plot] [--no-save] [--seed SEED] [--addons [ADDONS ...]] [--n_jobs N_JOBS] [--only ONLY]
__main__.py: error: the following arguments are required: --config-yaml
```

## Usage

GutenTAG can be used as a python library and from the CLI.

### From CLI as program

Example call from CLI:

```bash
python -m gutenTAG --config-yaml generation_configs/example-config.yaml --plot --seed 42
# see help page with
python -m gutenTAG --help
```

See the [`example-config.yaml`-file](generation_configs/example-config.yaml) for an example of a configuration file.

### From within python as library

To generate GutenTAG time series from Python, you have multiple options. Either you write a `dict()` with the same schema as the configuration uses and call the following:

```python
from gutenTAG import GutenTAG

config = {
    "timeseries": [
        {
            "name": "test",
            "length": 100,
            "base-oscillations": [
               {"kind": "sinus"}
            ],
            "anomalies": [
                {"length": 5, "types": [{"kind": "mean"}]}
            ]
        }
    ]
}
gutentag = GutenTAG.from_dict(config, plot=True)

# call generate() to create the datasets (in-memory)
gutentag.generate()

# we only defined a single time series
assert len(gutentag.timeseries) == 1
ts = gutentag.timeseries[0]

# the data points are stored at
ts.timeseries
# the labels are stored at
ts.labels

# you can plot the results via
ts.plot()
```

Or you call the class and set its parameters yourself. However, this is not recommended!

## Structure

GutenTag generates time series based on two fundamental building blocks: base oscillations and anomalies.
Each time series has the following properties:

- optional name
- length
- number of channels
- a single base oscillation
- a list of anomalies (at different positions in the time series)

For a more detailled look at the structure of GutenTAG, please consider the [Wiki](https://gitlab.hpi.de/akita/guten-tag/-/wikis/home).

### Base Oscillations

The generator comes with the following base oscillations in [./gutenTAG/base_oscillations](./gutenTAG/base_oscillations):

- sine
- random-walk
- cylinder-bell-funnel
- ecg
- polynomial
- random-mode-jump
- formula

Base oscillations can have an underlying trend.
This trend can be any of the above base oscillations.

Using the `variance` property, you can add noise to the base oscillation.
The general kind of base oscillation is always the same for all channels of a time series.
However, noise and other random parameters differ between channels.

#### Using the `formula` Base Oscillation

The `formula` base oscillation is a simple math engine that can perform primitive math operations on multiple already generated channels.

##### Syntax

**Formula Object**

The `FormulaObj` is the base to every `formula`. It consists of three fields: `base`, `operation`, and `aggregation`.
The `base` defines the first operand. It can either be a channel id (`int`) or another `FormulaObj`. The `base` can be the only field in a `FormulaObj` and then simply copies the channel with the right id (`base:int`).
It can also have a field `operation` or `aggregation`. However, it cannot have both at the same time.

```yaml
# FormulaObj
base: Union[int, FormulaObj]
operation: Optional[Operation]
aggregation: Optional[Aggregation]
```

**Operation**

The `Operation` is the vectorized math operation that is performed on the `base`. It consists of two required fields: `kind`, and `operand`.
The `kind` field is an enum that defines which math operator to perform. The `operand` field is the operand that is calculated to the before-defined `base`. The `operand` can be a scalar value or another `FormulaObj`.

```yaml
# Operation
kind: Enum[+, -, *, /, **]
operand: Union[float, FormulaObj]
```

**Aggregation**

The alternative to the `Operation` is the `Aggregation` field. This field defines an aggregation operation on the `base`. Its result is either a scalar or an array. It consists of two fields: `kind`, and `axis`.
The `kind` field defines the kind of aggregation performed on a numpy array. The optional `axis` field defines the axis of the array the aggregation is performed on. If no `axis` is defined, the aggregation will return a scalar. 

```yaml
# Aggregation
kind: Enum[sum, min, max, median, std, var]
axis: Optional[int]
```

**Example**

The following formula:

```python
import numpy as np
a = np.arange(10)
b = np.ones(10)
channels = [a, b]

# formula
(channels[0] + channels[0]) * channels[1].sum()
```

can be defined as the following `FormulaObj`:

```yaml
formula:
  base:
    base: 0           # (channels[0]
    operation:
      kind: "+"       # +
      operand:
        base: 0       # channels[0])
  operation:
    kind: "*"         # *
    operand:
      base: 1         # channels[1]
      aggregation:
        kind: "sum"   # .sum()
```

### Anomalies

The generator comes with the following anomaly types in [./gutenTAG/anomalies/types](./gutenTAG/anomalies/types):

- amplitude
- extremum
- frequency
- mean
- pattern
- pattern-shift
- platform
- trend
- variance
- mode-correlation

## Adding a new Anomaly Type

1. create a new Enum type for [`AnomalyKind`](gutenTAG/anomalies/types/kind.py) and adapt the `generate` method
2. [RECOMMENDED] create a new anomaly type class under [gutenTAG/anomalies/types](gutenTAG/anomalies/types)
    1. the new class should inherit from [`gutenTAG.anomalies.BaseAnomaly`](gutenTAG/anomalies/types/__init__.py)

## Status

The following table shows which anomalies and base oscillations can be combined and
which combinations GutenTAG does not supported.

- `x` = Combination allowed
- `-` = Combination not allowed

|                  | sine | random-walk | cylinder-bell-funnel | ecg | polynomial | random-mode-jump | formula  |
|:-----------------|:----:|:-----------:|:--------------------:|:---:|:----------:|:----------------:|:--------:|
| amplitude        |  x   |      x      |          x           |  x  |      -     |        -         |    -     |
| extremum         |  x   |      x      |          x           |  x  |      x     |        -         |    x     |
| frequency        |  x   |      -      |          -           |  x  |      -     |        -         |    -     |
| mean             |  x   |      x      |          x           |  x  |      x     |        -         |    -     |
| pattern          |  x   |      -      |          x           |  x  |      -     |        -         |    -     |
| pattern_shift    |  x   |      -      |          -           |  x  |      -     |        -         |    -     |
| platform         |  x   |      x      |          x           |  x  |      x     |        -         |    x     |
| trend            |  x   |      x      |          x           |  x  |      x     |        -         |    x     |
| variance         |  x   |      x      |          x           |  x  |      x     |        -         |    x     |
| mode_correlation |  -   |      -      |          -           |  -  |      -     |        x         |    -     |
