from dataclasses import dataclass
from enum import Enum

import pandas as pd


class TrainingType(Enum):
    TEST = "test"
    TRAIN_NO_ANOMALIES = "train-no-anomaly"
    TRAIN_ANOMALIES = "train-anomaly"


@dataclass
class TimeSeries:
    name: str
    training_type: TrainingType
    timeseries: pd.DataFrame


INDEX_COLUMN_NAME = "timestamp"
LABEL_COLUMN_NAME = "is_anomaly"
