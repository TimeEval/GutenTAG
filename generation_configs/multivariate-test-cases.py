import random
from itertools import combinations
from pathlib import Path

import numpy as np

from gutenTAG import GutenTAG


GENERATE_SUPERVISED = False
GENERATE_SEMI_SUPERVISED = False
SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def random_bo(kind: str):
    noise = np.random.rand() / 10
    mapping = {
        "sine": {
            "kind": "sine",
            "frequency": np.random.randint(1, 50),
            "variance": noise,
            "offset": np.random.rand() * 20 - 10,
            "amplitude": np.random.rand() * 10
        },
        "complex-sine": {
            "kind": "sine",
            "frequency": np.random.randint(1, 10),
            "variance": noise,
            "offset": np.random.rand() * 20 - 10,
            "amplitude": np.random.rand() * 10,
            "freq-mod": 0.01,
            "trend": {
                "kind": "polynomial",
                "polynomial": [1, 1]
            }
        },
        "ecg": {
            "kind": "ecg",
            "frequency": np.random.randint(10, 50),
            "variance": 0.001,
            "offset": np.random.rand() * 20 - 10
        },
        "cbf": {
            "kind": "cylinder-bell-funnel",
            "variance": noise,
            "offset": np.random.rand() * 20 - 10,
            "amplitude": np.random.rand() * 10 + 0.1,
            "avg-pattern-length": np.random.randint(10, 200),
            "variance-pattern-length": 0.2,
            "variance-amplitude": 0.5
        },
        "rw": {
            "kind": "random-walk",
            "variance": noise,
            "offset": np.random.rand() * 20 - 10,
            "amplitude": 1,
            "smoothing": 0.01
        },
        "poly": {
            "kind": "polynomial",
            "variance": noise,
            "offset": np.random.rand() * 20 - 10,
            "polynomial": [0, 2, 1, -2],
        },
        "rmj": {
            "kind": "random-mode-jump",
            "variance": noise,
            "offset": np.random.rand() * 20 - 10,
            "frequency": np.random.randint(10, 1000),
            "channel_diff": np.random.rand() * 10,
            "channel_offset": 1,
        }
    }
    return mapping[kind]


def random_anomaly(kind: str):
    trend_bos = [
        {
            "kind": "polynomial",
            "polynomial": [2, 2]
        },
        {
            "kind": "polynomial",
            "polynomial": [0.2, 0.2]
        },
        {
            "kind": "sine",
            "frequency": 0.725,
            "amplitude": 0.25,
            "variance": 0.0
        },
        {
            "kind": "sine",
            "frequency": 1,
            "amplitude": .5,
            "variance": 0.0
        }
    ]
    mapping = {
        "amplitude": {
            "kind": "amplitude",
            "amplitude_factor": np.random.choice([0.1, 0.25, 0.5, 2, 3, 10])
        },
        "extremum": {
            "kind": "extremum",
            "min": False,
            "local": bool(np.random.choice([True, False])),
            "context_window": 100
        },
        "frequency": {
            "kind": "frequency",
            "frequency_factor": np.random.choice([0.1, 0.25, 0.3, 0.5, 2, 3, 10])
        },
        "mean": {
            "kind": "mean",
            "offset": np.random.rand() * 20 - 10
        },
        "pattern": {
            "kind": "pattern",
            "sinusoid_k": np.random.rand(),
            "cbf_pattern_factor": np.random.rand()
        },
        "pattern-shift": {
            "kind": "pattern-shift",
            "shift_by": np.random.randint(-50, 50),
            "transition_window": 50
        },
        "platform": {
            "kind": "platform",
            "value": np.random.randint(10)
        },
        "trend": {
            "kind": "trend",
            "oscillation": np.random.choice(trend_bos)
        },
        "variance": {
            "kind": "variance",
            "variance": np.random.rand() / 2
        },
        "mode-correlation": {
            "kind": "mode-correlation"
        }
    }
    return mapping[kind]


def create_ts_def(name: str, bo_defs, anom_defs):
    return {
        "name": name,
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": bo_defs,
        "anomalies": anom_defs
    }


def gen_channel_series():
    bos = ["ecg", "rw", "poly"]
    anomalies = {
        "ecg": ["frequency", "variance", "extremum"],
        "rw": ["platform", "variance", "extremum"],
        "poly": ["platform", "variance", "extremum"]
    }
    anomaly_lengths = [100, 200, 500, 1000]
    n_channels = [2, 5, 10, 50, 100, 500]

    timeseries = []
    for bo in bos:
        for d in n_channels:
            bo_defs = [random_bo(bo) for _ in range(d)]
            for anom in anomalies[bo]:
                for l in anomaly_lengths:
                    if anom == "extremum":
                        l = 1
                    timeseries.append(create_ts_def(
                        f"channels-{d}-{bo}-{anom}-{l}",
                        bo_defs,
                        [{
                            "position": "middle",
                            "length": l,
                            "channel": np.random.randint(d),
                            "kinds": [random_anomaly(anom)]
                        }]
                    ))
                    if anom == "extremum":
                        break

    return timeseries


def gen_bo_diversity_series():
    timeseries = []
    bos = ["sine", "ecg", "rw", "cbf", "poly"]
    # all same
    n_bos = 10
    for bo in bos:
        timeseries.append(create_ts_def(
            f"bo-diversity-all-same-{bo}",
            [random_bo(bo) for _ in range(n_bos)],
            [{
                "position": "middle",
                "length": 100,
                "channel": np.random.randint(n_bos),
                "kinds": [random_anomaly("mean")]
            }]
        ))
    # same diff
    base_bo = "sine"
    n_bos = 10
    for i in [1, 2, 5]:
        for bo in set(bos) - set(base_bo):
            bo_defs = np.array([random_bo(base_bo) for _ in range(n_bos)])
            idxs = np.random.choice(n_bos, size=i, replace=False)
            bo_defs[idxs] = [random_bo(bo) for _ in range(i)]
            timeseries.append(create_ts_def(
                f"bo-diversity-{i}-same-diff-{bo}",
                bo_defs.tolist(),
                [{
                    "position": "middle",
                    "length": 100,
                    "channel": np.random.randint(n_bos),
                    "kinds": [random_anomaly("mean")]
                }]
            ))
    # multiple diff
    n_bos = 10
    times_mapping = {
        2: [5, 5],
        3: [3, 3, 4],
        4: [2, 2, 3, 3],
        5: [2, 2, 2, 2, 2]
    }
    for i in [2, 3, 4, 5]:
        bo_combs = list(combinations(bos, i))
        for bo_tuple in bo_combs:
            bo_tuple = list(bo_tuple)
            np.random.shuffle(bo_tuple)
            bo_defs = []
            for bo, times in zip(bo_tuple, times_mapping[i]):
                bo_defs.extend(random_bo(bo) for _ in range(times))
            for anom_pos in range(i):
                pos_begin = np.sum(times_mapping[i][:anom_pos], dtype=np.int_)
                pos_end = pos_begin + times_mapping[i][anom_pos]
                pos = np.random.randint(pos_begin, pos_end)
                timeseries.append(create_ts_def(
                    f"bo-diversity-{i}-multi-diff-BOS={'_'.join(sorted(bo_tuple))}-ANOM={sorted(bo_tuple).index(bo_tuple[anom_pos])}",
                    bo_defs,
                    [{
                        "position": "middle",
                        "length": 100,
                        "channel": pos,
                        "kinds": [random_anomaly("mean")]
                    }]
                ))
    return timeseries


def gen_anomaly_appearance_series():
    timeseries = []
    anomalies = ["amplitude", "extremum", "frequency", "mean", "pattern",
                 "pattern-shift", "platform", "trend", "variance"]
    n_bos = 20
    bo_kind = "sine"
    # same
    for anom in anomalies:
        for n in [1, 2, 5, 10, n_bos]:
            anom_channels = np.random.choice(n_bos, size=n, replace=False)
            position = np.random.randint(2500, 7500)
            timeseries.append(create_ts_def(
                f"anom-appearance-same-{n}-{anom}",
                [random_bo(bo_kind) for _ in range(n_bos)],
                [{
                    "exact-position": position + 50 if anom == "extremum" else position,
                    "length": 1 if anom == "extremum" else 100,
                    "channel": int(c),
                    "kinds": [random_anomaly(anom)]
                } for c in anom_channels]
            ))
    # diff
    for n_kinds in [2, 3, 5]:
        anom_combs = list(combinations(anomalies, n_kinds))
        for anom_tuple in anom_combs:
            anom_tuple = list(anom_tuple)
            np.random.shuffle(anom_tuple)
            for n in [2, 3, 5, 10, n_bos]:
                if n_kinds > n:
                    continue
                n_times = n // n_kinds
                times = [n_times] * n_kinds
                remainder = n - (n_times * n_kinds)
                i = 0
                while remainder > 0:
                    times[i % n_kinds] += 1
                    remainder -= 1
                    i += 1

                anomaly_defs = []
                position = np.random.randint(2500, 7500)
                for anom, anom_times in zip(anom_tuple, times):
                    anom_channels = np.random.choice(n_bos, size=anom_times, replace=False)
                    for c in anom_channels:
                        anomaly_defs.append({
                            "exact-position": position + 50 if anom == "extremum" else position,
                            "length": 1 if anom == "extremum" else 100,
                            "channel": int(c),
                            "kinds": [random_anomaly(anom)]
                        })

                timeseries.append(create_ts_def(
                    f"anom-appearance-{n_kinds}-diff-{n}-ANOMS={'_'.join(sorted(anom_tuple))}",
                    [random_bo(bo_kind) for _ in range(n_bos)],
                    anomaly_defs
                ))

    return timeseries


def gen_special_series():
    return [{
        "name": "sum-cancels-out-anomaly",
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [{
            "kind": "sine",
            "frequency": 0.5,
            "offset": 2
        }, {
            "kind": "formula",
            "formula": {
                "base": 0,
                "operation": {
                    "kind": "*",
                    "operand": -1.
                }
            }
        }],
        "anomalies": [{
            "exact-position": 5000,
            "length": 100,
            "channel": 0,
            "kinds": [{"kind": "mean", "offset": 2}]
        }, {
            "exact-position": 5000,
            "length": 100,
            "channel": 1,
            "kinds": [{"kind": "mean", "offset": -2}]
        }]
    }, {
        "name": "3-is-sum-of-2",
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [{
            "kind": "sine",
            "frequency": 0.5,
            "offset": 2
        }, {
            "kind": "polynomial",
            "polynomial": [0, -2],
        }, {
            "kind": "formula",
            "formula": {
                "base": 0,
                "operation": {
                    "kind": "+",
                    "operand": {
                        "base": 1
                    }
                }
            }
        }],
        "anomalies": [{
            "exact-position": 5000,
            "length": 100,
            "channel": 0,
            "kinds": [{"kind": "mean", "offset": 2}]
        }, {
            "exact-position": 5000,
            "length": 100,
            "channel": 1,
            "kinds": [{"kind": "mean", "offset": -2}]
        }, {
            "position": "end",
            "length": 1,
            "channel": 2,
            "kinds": [{"kind": "extremum", "local": True, "min": False, "context_window": 200}]
        }]
    }, {
        "name": "creeping-anomalies",
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [{
            "kind": "sine",
            "frequency": 0.5,
            "offset": 2
        }, {
            "kind": "polynomial",
            "polynomial": [0, -2],
        }, {
            "kind": "ecg",
            "frequency": 2,
            "variance": 0.005
        }],
        "anomalies": [{
            "position": "middle",
            "length": 300,
            "creeping-length": 200,
            "channel": 1,
            "kinds": [{"kind": "mean", "offset": 2}]
        }, {
            "position": "middle",
            "length": 300,
            "creeping-length": 250,
            "channel": 0,
            "kinds": [{"kind": "variance", "variance": .5}]
        }, {
            "position": "end",
            "length": 200,
            "creeping-length": 100,
            "channel": 2,
            "kinds": [{"kind": "amplitude", "amplitude_factor": 2}]
        }]
    }, {
        "name": "shifted-anomalies",
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [{
            "kind": "sine",
            "frequency": 0.5,
            "offset": 2
        }, {
            "kind": "polynomial",
            "polynomial": [0, -2],
        }, {
            "kind": "ecg",
            "frequency": 2,
            "variance": 0.005
        }],
        "anomalies": [{
            "exact-position": 5200,
            "length": 200,
            "channel": 0,
            "kinds": [{"kind": "frequency", "frequency_factor": 2}]
        }, {
            "exact-position": 5300,
            "length": 200,
            "channel": 2,
            "kinds": [{"kind": "frequency", "frequency_factor": .5}]
        }]
    }, {
        "name": "missing-pattern-1",
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [{
            "kind": "ecg",
            "frequency": 1,
            "offset": 0,
            "variance": 0.001
        }],
        "anomalies": [{
            "exact-position": 1715,
            "length": 8,
            "channel": 0,
            "kinds": [
                {"kind": "platform", "value": 0.5},
                {"kind": "variance", "variance": 0.05},
            ]
        }]
    }, {
        "name": "missing-pattern-2",
        "length": 10000,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [{
            "kind": "sine",
            "frequency": .25,
            "offset": 0,
            "variance": 0
        }, {
            "kind": "ecg",
            "frequency": 1,
            "offset": 0,
            "variance": 0
        }, {
            "kind": "formula",
            "formula": {
                "base": 0,
                "operation": {
                    "kind": "*",
                    "operand": {
                        "base": 1
                    }
                }
            }
        }],
        "anomalies": [{
            "exact-position": 4316,
            "length": 7,
            "channel": 2,
            "kinds": [{"kind": "platform", "value": 0.3}]
        }]
    }]


if __name__ == '__main__':
    path = Path("multivariate-test-cases")
    print("Generating config ...")
    config = {
        "timeseries": gen_channel_series() + gen_bo_diversity_series() + gen_anomaly_appearance_series() + gen_special_series()
    }
    gutentag = GutenTAG(n_jobs=-1, seed=SEED, addons=["gutenTAG.addons.timeeval.TimeEvalAddOn"])
    gutentag.load_config_dict(config)
    # gutentag.load_config_dict({"timeseries": gen_special_series()}, only="sum-cancels-out-anomaly")
    gutentag.generate(output_folder=path)
    # dfs = gutentag.generate(return_timeseries=True)

    # df = dfs[4]
    # # df["sum"] = df["value-0"] + df["value-1"] + df["value-2"]
    # print(df)
    # import matplotlib.pyplot as plt
    # fig, axs = plt.subplots(2, 1, sharex="col")
    # df[set(df.columns) - {"is_anomaly"}].plot(ax=axs[0])
    # axs[0].legend()
    # df["is_anomaly"].plot(ax=axs[1])
    # axs[1].legend()
    # plt.show()
