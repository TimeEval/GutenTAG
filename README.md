# GutenTAG
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
|frequency|x|||||
|mean|x|x|x|x|x|
|pattern|x|||||
|pattern_shift|x|||||
|platform|x|x|x|x|x|
|variance|x|x|x|x|x|
