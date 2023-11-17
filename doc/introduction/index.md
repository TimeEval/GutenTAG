# Introduction

The GutenTAG is a good timeseries anomaly generator.
As a user, you can choose between several [Base Oscillations](base-oscillations.md) and [Anomaly Types](anomaly-types.md) which are applied on the base oscillations.
However, not all anomalies can be applied on all base oscillations.
An overview can be found [here](#combinations).

## Installation

You can install GutenTAG from the official Python Package Index or from source.

- Installation from PyPI:

  ```bash
  pip install timeeval-gutenTAG
  ```

- Installation from source:

  ```bash
  git clone git@github.com:TimeEval/GutenTAG.git

  cd GutenTAG

  # (optionally) create a new conda environment with Python 3
  conda create -n gutentag python=3.8
  conda activate gutentag

  # install dependencies
  pip install -r requirements.txt
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

                     Version 1.2.0

"Good day!" wishes your friendly Timeseries Anomaly Generator.



usage: __main__.py [-h] [--version] --config-yaml CONFIG_YAML
                   [--output-dir OUTPUT_DIR] [--plot] [--no-save]
                   [--seed SEED] [--addons [ADDONS [ADDONS ...]]]
                   [--n_jobs N_JOBS] [--only ONLY]
__main__.py: error: the following arguments are required: --config-yaml
```
Go to the [usage-page](../usage.md) for further instructions on how to call GutenTAG.

## Structure

GutenTag generates time series based on two fundamental building blocks: [base oscillations](base-oscillations.md) and [anomalies](anomaly-types.md).
Each time series has the following properties:

- optional name
- length
- a list of base oscillations defining the different channels
- a list of anomalies (at different positions in the time series)
- (some additional optional configuration options)

### Internal Process

1. We first generate the base oscillation.
2. Then, we inject the anomalies at the specific locations.
    1. The location of an anomaly is defined by the given position (in time)
        1. A position can be an exact time stamp or index in the time series
        2. or an approximate region like _beginning_, _middle_, or _end_. Here, GutenTAG will randomly choose a cycle in the corresponding region and will use its start as position.
    2. and the channel defined by the channel ID.
3. Afterwards, the variations like _noise_, _trend_, and _offset_ are applied to the time series.

## Combinations

The following table shows which anomalies and base oscillations can be combined and
which combinations GutenTAG does not support.

- `x` = Combination allowed
- `-` = Combination not allowed

|                  | Sine  | Cosine | Square | Random Walk | CBF | ECG | Polynomial | Random Mode Jump | Formula | Sawtooth | Dirichlet | MLS | Custom Input |
|:-----------------|:-----:|:------:|:------:|:-----------:|:---:|:---:|:----------:|:----------------:|:-------:|:--------:|:---------:|:---:|:------------:|
| amplitude        |   x   |   x    |   x    |      x      |  x  |  x  |     -      |        -         |    -    |    x     |     x     |  x  |       x      |
| extremum         |   x   |   x    |   x    |      x      |  x  |  x  |     x      |        -         |    x    |    x     |     x     |  x  |       x      |
| frequency        |   x   |   x    |   x    |      -      |  -  |  x  |     -      |        -         |    -    |    x     |     x     |  -  |       -      |
| mean             |   x   |   x    |   x    |      x      |  x  |  x  |     x      |        -         |    x    |    x     |     x     |  x  |       x      |
| pattern          |   x   |   x    |   x    |      -      |  x  |  x  |     -      |        -         |    -    |    x     |     x     |  x  |       -      |
| pattern_shift    |   x   |   x    |   x    |      -      |  -  |  x  |     -      |        -         |    -    |    x     |     x     |  -  |       -      |
| platform         |   x   |   x    |   x    |      x      |  x  |  x  |     x      |        -         |    x    |    x     |     x     |  x  |       x      |
| trend            |   x   |   x    |   x    |      x      |  x  |  x  |     x      |        -         |    x    |    x     |     x     |  x  |       x      |
| variance         |   x   |   x    |   x    |      x      |  x  |  x  |     x      |        -         |    x    |    x     |     x     |  x  |       x      |
| mode_correlation |   -   |   -    |   -    |      -      |  -  |  -  |     -      |        x         |    -    |    -     |     -     |  -  |       -      |
