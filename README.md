<img src="logo_transparent.png" alt="GutenTAG logo" width="400px" align="middle"/>

A good **T**imeseries **A**nomaly **G**enerator.

## Usage


### From python

```python
from gutenTAG.generator import GutenTAG
```

### From CLI

Example call from CLI:

```bash
python -m gutenTAG --config-yaml gutenTAG/generator/generation_config.yaml --plot --seed 42
# see help page with
python -m gutenTAG --help
```

## Structure

### Base Oscillations
The generator comes with the following base oscillations in [./gutenTAG/base_oscillations](./gutenTAG/base_oscillations):

- sinus
- random walk
- cylinder bell funnel
- synthetic ecg
- CoMuT

#### Usage

```python
from gutenTAG.base_oscillations import BaseOscillation

options = {
    # ...
}

# to generate a sinus oscillation without anomalies
BaseOscillation.Sinus(**options).generate()
```

### Anomalies
Also, the generator comes with the following anomaly types in [./gutenTAG/anomalies/types](./gutenTAG/anomalies/types):

- extremum
- frequency
- mean
- pattern
- pattern_shift
- platform
- variance

#### Usage

```python
from gutenTAG.base_oscillations import BaseOscillation
from gutenTAG.anomalies import Anomaly, Position
from gutenTAG.anomalies.types.platform import AnomalyPlatform

options = {
    # ...
}

anomalies = [
    Anomaly(Position.Beginning, anomaly_length=200).set_platform(AnomalyPlatform(0.0))
]

# to generate a sinus oscillation with a platform anomaly
BaseOscillation.Sinus(**options).inject_anomalies(anomalies).generate()
```

## Adding a new Anomaly Type

1. create a new Enum type for [`AnomalyKind`](gutenTAG/anomalies/types/kind.py) and adapt the `generate` method
2. [RECOMMENDED] create a new anomaly type class under [gutenTAG/anomalies/types](gutenTAG/anomalies/types)
    2. the new class should inherit from [`gutenTAG.anomalies.BaseAnomaly`](gutenTAG/anomalies/types/__init__.py)


## Status

|   | Sinus | Random Walk | CBF | ECG | CoMuT |
|---|-------|-------------|-----|-----|-------|
|extremum |x|x|x|x|x|
|frequency|x|-|x|x||
|mean|x|x|x|x|x|
|pattern|x|-|x|x||
|pattern_shift|x|-|-|x||
|platform|x|x|x|x|x|
|variance|x|x|x|x|x|


## TODO

### Base-Oscillation

- [x] timeeval format
- [x] train-with-label
- [x] sinus add amplitude+frequency modification over time
- [x] clean sinus (`freq-mod: false` turns on clean mode)
- [x] linear base oscillation
- [x] nested trends (as base oscillation)
- [x] check if anomalies collide with same position (shift)
- [x] offset to base oscillation
- [x] smoothing for random walk
- [x] amplitude anomaly (steep gaussian transition `scipy.stats.norm.pdf(np.linspace(0, 3, 100), scale=1.05)`)
- [x] frequency -> sampling_rate
- [x] give name to timeseries
- [x] train with&without anomalies
- [x] 3 entries for datasets.csv ^
- [x] dataset name/path for datasets.csv 
- [ ] trend anomaly bug
- [x] pull lengths
- [ ] generate YAML from docs

### Anomaly

- [x] Trend anomaly

### Future (nice to have)

- [ ] datasets.csv trend
- [ ] noise as variance Union[float, List[float]] for each channel
- [ ] plot with subplot
- [ ] plot multivariate with subplot
- [ ] create YAML schema (very nice to have, almost important)
