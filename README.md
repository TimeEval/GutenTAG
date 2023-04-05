<div align="center">
    <img width="400px" src="https://github.com/HPI-Information-Systems/gutentag/raw/main/logo_transparent.png" alt="TimeEval logo"/>
    <p>
    A good <strong>T</strong>imeseries <strong>A</strong>nomaly <strong>G</strong>enerator.
    </p>

[![CI](https://github.com/HPI-Information-Systems/gutentag/actions/workflows/build.yml/badge.svg)](https://github.com/HPI-Information-Systems/gutentag/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/HPI-Information-Systems/gutentag/branch/main/graph/badge.svg?token=6QXOCY4TS2)](https://codecov.io/gh/HPI-Information-Systems/gutentag)
[![PyPI package](https://badge.fury.io/py/timeeval-gutenTAG.svg)](https://badge.fury.io/py/timeeval-gutenTAG)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![python version 3.7|3.8|3.9|3.10|3.11](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
[![Downloads](https://pepy.tech/badge/timeeval-gutentag)](https://pepy.tech/project/timeeval-gutentag)

</div>

GutenTAG is an extensible tool to generate time series datasets with and without anomalies.
A GutenTAG time series consists of a single (univariate) or multiple (multivariate) channels containing a base oscillation with different anomalies at different positions and of different kinds.

[![base-oscillations](https://img.shields.io/badge/base_oscillations-11-3a4750?style=for-the-badge)](./doc/introduction/base-oscillations.md)
[![base-oscillations](https://img.shields.io/badge/anomaly_types-10-f6c90b?style=for-the-badge)](./doc/introduction/anomaly-types.md)
[![base-oscillations](https://img.shields.io/badge/add--ons-1-f64e8b?style=for-the-badge)](./doc/advanced-features.md)

[![base-oscillations](https://img.shields.io/badge/easy_config-YAML-3a4750?style=for-the-badge)](./doc/usage.md)

## tl;dr

1. Install GutenTAG from [PyPI](https://pypi.org/project/timeeval-gutenTAG/):

   ```sh
   pip install timeeval-gutenTAG
   ```

   GutenTAG supports Python 3.7, 3.8, 3.9, 3.10, and 3.11; all other [requirements](./requirements.txt) are installed with the pip-call above.

2. Create a generation configuration file [`example-config.yaml`](./generation_configs/example-config.yaml) with the instructions to generate a single time series with two anomalies:
   A _pattern_ anomaly in the middle and an _amplitude_ anomaly at the end of the series.
   You can use the following content:

   ```yaml
   timeseries:
   - name: demo
     length: 1000
     base-oscillations:
     - kind: sine
       frequency: 4.0
       amplitude: 1.0
       variance: 0.05
     anomalies:
     - position: middle
       length: 50
       kinds:
       - kind: pattern
         sinusoid_k: 10.0
     - position: end
       length: 10
       kinds:
       - kind: amplitude
         amplitude_factor: 1.5
   ```

3. Execute GutenTAG with a seed and let it plot the time series:

   ```bash
   gutenTAG --config-yaml example-config.yaml --seed 11 --no-save --plot
   ```

   You should see the following time series:

   ![Example unsupervised time series with two anomalies](https://github.com/HPI-Information-Systems/gutentag/raw/main/example-ts.png)

## Documentation

GutenTAG's documentation can be found [here](doc/index.md).

## Citation

If you use GutenTAG in your project or research, please cite our demonstration paper:

> Phillip Wenig, Sebastian Schmidl, and Thorsten Papenbrock.
> TimeEval: A Benchmarking Toolkit for Time Series Anomaly Detection Algorithms. PVLDB, 15(12): 3678 - 3681, 2022.
> doi:[10.14778/3554821.3554873](https://doi.org/10.14778/3554821.3554873)

```bibtex
@article{WenigEtAl2022TimeEval,
  title = {TimeEval: {{A}} Benchmarking Toolkit for Time Series Anomaly Detection Algorithms},
  author = {Wenig, Phillip and Schmidl, Sebastian and Papenbrock, Thorsten},
  date = {2022},
  journaltitle = {Proceedings of the {{VLDB Endowment}} ({{PVLDB}})},
  volume = {15},
  number = {12},
  pages = {3678 -- 3681},
  doi = {10.14778/3554821.3554873}
}
```

## To-Do

- [ ] negation anomaly (does a pattern not appear)
