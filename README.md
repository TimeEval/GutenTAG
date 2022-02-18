<div align="center">
    <img width="400px" src="./logo_transparent.png" alt="TimeEval logo"/>
    <p>
    A good <strong>T</strong>imeseries <strong>A</strong>nomaly <strong>G</strong>enerator.
    </p>

[![pipeline status](https://gitlab.hpi.de/akita/guten-tag/badges/main/pipeline.svg)](https://gitlab.hpi.de/akita/guten-tag/-/commits/main)
[![coverage report](https://gitlab.hpi.de/akita/guten-tag/badges/main/coverage.svg)](https://gitlab.hpi.de/akita/guten-tag/-/commits/main)

[![Git tag](https://img.shields.io/badge/tag-0.1.0-blue)](setup.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python version 3.8](https://img.shields.io/badge/python-3.8-blue)](setup.py)

</div>

GutenTAG is an extensible tool to generate time series datasets with and without anomalies.
A GutenTAG time series consists of a single (univariate) or multiple (multivariate) channels containing a base osciallation with different anomalies at different positions and of different kinds.

## tl;dr

[![base-oscillations](https://img.shields.io/badge/base_oscillations-8-3a4750?style=for-the-badge)](./doc/introduction/base-oscillations.md)
[![base-oscillations](https://img.shields.io/badge/anomaly_types-11-f6c90b?style=for-the-badge)](./doc/introduction/anomaly-types.md)
[![base-oscillations](https://img.shields.io/badge/add--ons-1-f64e8b?style=for-the-badge)](./doc/advanced-features.md)

[![base-oscillations](https://img.shields.io/badge/easy_config-YAML-3a4750?style=for-the-badge)](./doc/usage.md)

The following call uses the [`example-config.yaml`](generation_configs/example-config.yaml) configuration file to generate a single time series with two anomalies in the middle and the end of the series.

```bash
python -m gutenTAG --config-yaml generation_configs/example-config.yaml --seed 11 --no-save --plot
```

![Example unsupervised time series with two anomalies](example-ts.png)

## Documentation

GutenTAG's documentation can be found [here](doc/index.md).


# TODO

- [ ] negation anomaly (does a pattern not appear)
