![GutenTAG](./logo_transparent.png)


A good **T**imeseries **A**nomaly **G**enerator.

## Usage

```python
from gutenTAG.generator import GutenTAG
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
- [x] clean sinus
- [ ] linear base oscillation
- [ ] nested trends (as base oscillation)
- [ ] check if anomalies collide with same position (shift)
- [ ] offset to base oscillation
- [ ] smoothing for random walk
- [ ] amplitude anomaly (steep gaussian transition `scipy.stats.norm.pdf(np.linspace(0, 3, 100), scale=1.05)`)
- [ ] frequency -> sampling_rate
- [ ] give name to timeseries
- [ ] generate YAML from docs

### Anomaly

- [ ] Trend anomaly

### Future (nice to have)

- [ ] noise as variance Union[float, List[float]] for each channel
- [ ] plot with subplot
- [ ] plot multivariate with subplot
- [ ] create YAML schema
