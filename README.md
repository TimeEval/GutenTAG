<img src="logo_transparent.png" alt="GutenTAG logo" width="400px" align="middle"/>

A good **T**imeseries **A**nomaly **G**enerator.

## Usage


### From within python as library

Example API usage using Python 3:

```python
from gutenTAG.base_oscillations import BaseOscillation
from gutenTAG.anomalies import Anomaly, Position, AnomalyKind


options = {
   # ...
}

osci = BaseOscillation.from_key("sinus", **options)
# to generate a sinus oscillation without anomalies
timeseries, labels = osci.generate(with_anomalies=False)

# inject anomalies
anomaly = Anomaly(
   position=Position.Middle,
   exact_position=None,
   anomaly_length=100,
   channel=0
)
params = {"frequency_factor": 2.0}
anomaly.set_anomaly(AnomalyKind("frequency").create(**params))
# to generate a sinus oscillation with a frequency anomaly in the middle
timeseries, labels = osci.generate(with_anomalies=True)
```

### From CLI as program

Example call from CLI:

```bash
python -m gutenTAG --config-yaml gutenTAG/generator/generation_config.yaml --plot --seed 42
# see help page with
python -m gutenTAG --help
```

See the [`generation_config.yaml`-file](./gutenTAG/generator/generation_config.yaml) for an example of a configuration file.

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

- sinus
- random_walk
- cylinder_bell_funnel
- ecg
- polynomial

Base oscillations can have an underlying trend.
This trend can be any of the above base oscillations.

Using the `variance` property, you can add noise to the base oscillation.
The general kind of base oscillation is always the same for all channels of a time series.
However, noise and other random parameters differ between channels.

### Anomalies

The generator comes with the following anomaly types in [./gutenTAG/anomalies/types](./gutenTAG/anomalies/types):

- amplitude
- extremum
- frequency
- mean
- pattern
- pattern_shift
- platform
- trend
- variance

## Adding a new Anomaly Type

1. create a new Enum type for [`AnomalyKind`](gutenTAG/anomalies/types/kind.py) and adapt the `generate` method
2. [RECOMMENDED] create a new anomaly type class under [gutenTAG/anomalies/types](gutenTAG/anomalies/types)
    1. the new class should inherit from [`gutenTAG.anomalies.BaseAnomaly`](gutenTAG/anomalies/types/__init__.py)


## Status

The following table shows which anomalies and base oscillations can be combined and
which combinations GutenTAG does not supported.

`x` = Combination allowed
`-` = Combination not allowed

|               | Sinus | Random Walk | CBF | ECG | Polynomial |
|:--------------|:-----:|:-----------:|:---:|:---:|:----------:|
| amplitude     |   x   |      x      |  x  |  x  |      -     |
| extremum      |   x   |      x      |  x  |  x  |      x     |
| frequency     |   x   |      -      |  -  |  x  |      -     |
| mean          |   x   |      x      |  x  |  x  |      x     |
| pattern       |   x   |      -      |  x  |  x  |      -     |
| pattern_shift |   x   |      -      |  -  |  x  |      -     |
| platform      |   x   |      x      |  x  |  x  |      x     |
| trend         |   x   |      x      |  x  |  x  |      x     |
| variance      |   x   |      x      |  x  |  x  |      x     |


## TODO

### Features

- [ ] trend anomaly bug
- [ ] generate YAML from docs

### Future (nice to have)

- [ ] noise as variance Union[float, List[float]] for each channel
- [ ] nicer plot for multivariate time series
