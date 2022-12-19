import random
from pathlib import Path
import numpy as np
from gutenTAG import GutenTAG


GENERATE_SUPERVISED = False
GENERATE_SEMI_SUPERVISED = False
SEED = 42
NR_CHANNELS = 1
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

def random_anomaly(kind: str, length: int, position: str):
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
        # "trend": {
        #     "kind": "trend",
        #     "oscillation": np.random.choice(trend_bos)
        # },
        "variance": {
            "kind": "variance",
            "variance": np.random.rand() / 2
        },
        "mode-correlation": {
                "kind": "mode-correlation"
            }
    }
    return mapping[kind]


def generate_timeseries(dataset_name, nr_datapoints, base_oscillation, share_anomaly_points):
    anomaly_datapoints = 0
    anomalies_definitions = []
    anomalies = ["amplitude", "extremum", "frequency", "mean", "pattern",
                 "pattern-shift", "platform", "variance"] #"trend",
    anomaly_lengths = [10, 20, 30, 40, 50]
    anomaly_position = ["beginning", "middle", "end"]
    while anomaly_datapoints/nr_datapoints < share_anomaly_points:
        for anom in anomalies:
            for n in anomaly_lengths:
                for position in anomaly_position:
                    if anom == "extremum":
                        n = 1
                    new_anomaly = {
                        "position": position,
                        "length": n,
                        "kinds": [random_anomaly(kind = anom, length = n, position = position)]
                    }
                    anomalies_definitions.append(new_anomaly)
                    anomaly_datapoints = anomaly_datapoints + n


        
    return [{
        "name": dataset_name,
        "length": nr_datapoints,
        "channels": NR_CHANNELS,
        "semi-supervised": GENERATE_SEMI_SUPERVISED,
        "supervised": GENERATE_SUPERVISED,
        "base-oscillations": [random_bo(base_oscillation)],
        "anomalies": anomalies_definitions
    }]

if __name__ == "__main__":
    path = Path("generated_test_datasets")
    print("Generating config ...")
    config = {"timeseries": generate_timeseries("test_dataset", 1000, "ecg", 0.1)}
    print(config)
    gutentag = GutenTAG(n_jobs=-1, seed=SEED, addons=["gutenTAG.addons.timeeval.TimeEvalAddOn"])
    gutentag.load_config_dict(config)
    gutentag.generate(output_folder=path)

    