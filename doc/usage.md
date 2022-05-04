# Usage

## From CLI

To generate time series from CLI, the user must create a config YAML file that defines all base-oscillations and their contained anomalies. The YAML file must have the following schema (optional keys are shown in brackets):

```yaml
timeseries:
  - [name: Str]
    length: Int
    [semi-supervised: Bool]
    [supervised: Bool]
    base-oscillations:
      - kind: Enum[cylinder-bell-funnel,ecg,random-walk,sine,polynomial,random-mode-jump,formula]
        [trend: object]
        # parameters from [Introduction -> Base Oscillations](introduction#base-oscillations)
    anomalies:
      - length: Int
        [channel: Int]
        [position: Enum[beginning,middle,end]]
        [exact-position: Int]
        [creep-length: Int]
        kinds:
          - kind: Enum[extremum,frequency,mean,pattern,pattern-shift,platform,variance,amplitude,trend,mode-correlation]
            parameters:
              # corresponding parameters from [Introduction -> Anomaly Types](introduction#anomaly-types)
```

As seen in the YAML schema, in one config file multiple time series with multiple anomalies can be defined.
Each anomaly can furthermore be a combination of multiple anomaly types (e.g., platform and variance).

We also provide a [JSON schema definition](config-schema.md) that also works with YAML files.

### Commands

Once `GutenTAG` is installed and a desired config file is written, the user can call the following command to generate time series:

```shell
python -m gutenTAG [-h] [--version] --config-yaml CONFIG_YAML \
                  [--output-dir OUTPUT_DIR] \
                  [--plot] \
                  [--no-save] \
                  [--seed SEED] \
                  [--addons [ADDONS [ADDONS ...]]] \
                  [--n_jobs N_JOBS] \
                  [--only ONLY]

```

See `python -m gutenTAG --help` for the CLI usage and the explanation of the CLI arguments (further details also below).


### Parameters

|Name|Type| Desription                                                                                         |Default|
|----|----|----------------------------------------------------------------------------------------------------|-------|
|config-yaml|String| Path to config.yaml                                                                                |-|
|output-dir|String| Path to output director                                                                            |`generated-timeseries`|
|plot|Bool| Whether a plot should be displayed                                                                 |`False`|
|no-save|Bool| Whether the saving should be skipped                                                               |`False`|
|seed|Int| Random seed number for reproducibility                                                             |`None`|
|addons|String| Python import paths (explained in [Advanced Features](advanced-features.md))                       |`[]`|
|n_jobs|Integer| Number of parallelism to generate multiple time series in parallel                                 |`1`|
|only|String| Name of a time series defined in the config.yaml that is considered while all others are excluded. |`None`|

### Outputs

The generator will then create a directory with the desired timeseries and an `overview.yaml` file that has the same structure as the `config.yaml` with the extension of the `generation-id` parameter for time series without a name. This ID or the configured name tells the user which of the subfolders contains which time series. Inside of the subfolders is a `test.csv` file that represents the defined time series; if the time series is configured semi-supervised, there will be an additional file `train_no_anomaly.csv` containing a similar time series without anomalies; if the time series is configured supervised, there will be an additional file `train_anomaly.csv` containing a similar time series with anomalies. Each file has the following structure

```csv
timestamp,value-0,value-1,is_anomaly
0,0.1,0.3,0
1,0.3,0.3,0
2,0.1,0.3,1
3,0.2,0.3,0
```

The last column is the label, `0` if no anomaly else `1`. The preceding columns represent the channels. The file has a header and an index column called `timestamp`.

## From Python

To generate GutenTAG time series from Python, you have multiple options. Either you write a `dict()` with the same schema as in [From CLI](#from-cli) and call the following:

```python
from gutenTAG import GutenTAG

config = {
    "timeseries": [
        {
            "name": "test",
            "length": 100,
            "base-oscillations": [
               {"kind": "sine"}
            ],
            "anomalies": [
                {"length": 5, "channel": 0, "types": [{"kind": "mean", "parameters": {"offset": .5}}]}
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
