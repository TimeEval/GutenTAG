from pathlib import Path


SUPERVISED_FILENAME = "train_anomaly.csv"
SEMI_SUPERVISED_FILENAME = "train_no_anomaly.csv"
UNSUPERVISED_FILENAME = "test.csv"


BASE_OSCILLATION = "base-oscillation"
BASE_OSCILLATIONS = BASE_OSCILLATION + "s"
TIMESERIES = "timeseries"
ANOMALIES = "anomalies"


class BASE_OSCILLATION_NAMES:
    MLS = "mls"
    SINE = "sine"
    COSINE = "cosine"
    RANDOM_WALK = "random-walk"
    CYLINDER_BELL_FUNNEL = "cylinder-bell-funnel"
    ECG = "ecg"
    POLYNOMIAL = "polynomial"
    RANDOM_MODE_JUMP = "random-mode-jump"
    FORMULA = "formula"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    DIRICHLET = "dirichlet"
    CUSTOM_INPUT = "custom-input"


class ANOMALY_TYPE_NAMES:
    AMPLITUDE = "amplitude"
    EXTREMUM = "extremum"
    FREQUENCY = "frequency"
    MEAN = "mean"
    PATTERN = "pattern"
    PATTERN_SHIFT = "pattern-shift"
    PLATFORM = "platform"
    TREND = "trend"
    VARIANCE = "variance"
    MODE_CORRELATION = "mode-correlation"


class PARAMETERS:
    OSCILLATION = "oscillation"
    LENGTH = "length"
    FREQUENCY = "frequency"
    AMPLITUDE = "amplitude"
    VARIANCE = "variance"
    AVG_PATTERN_LENGTH = "avg-pattern-length"
    VARIANCE_PATTERN_LENGTH = "variance-pattern-length"
    VARIANCE_AMPLITUDE = "variance-amplitude"
    FREQ_MOD = "freq-mod"
    POLYNOMIAL = "polynomial"
    TREND = "trend"
    OFFSET = "offset"
    SMOOTHING = "smoothing"
    CHANNEL_DIFF = "channel-diff"
    CHANNEL_OFFSET = "channel-offset"
    RANDOM_SEED = "random-seed"
    FORMULA = "formula"
    KIND = "kind"
    KINDS = "kinds"
    NAME = "name"
    CHANNELS = "channels"
    CHANNEL = "channel"
    POSITION = "position"
    EXACT_POSITION = "exact-position"
    CREEPING_LENGTH = "creeping-length"
    ECG_SIM_METHOD = "ecg-sim-method"
    DUTY = "duty"
    WIDTH = "width"
    PERIODICITY = "periodicity"
    COMPLEXITY = "complexity"
    INPUT_TIMESERIES_PATH_TRAIN = "input-timeseries-path-train"
    INPUT_TIMESERIES_PATH_TEST = "input-timeseries-path-test"
    USE_COLUMN_TRAIN = "use-column-train"
    USE_COLUMN_TEST = "use-column-test"


class CONFIG_SCHEMA:
    BASE_ID = "guten-tag-generation-config.schema.yaml"
    SCHEMA_DOMAIN = "https://example.com"
    SCHEMA_FOLDER_PATH = Path("generation-config-schema")

    SCHEMA_PART_IDS = [
        "anomaly.guten-tag-generation-config.schema.yaml",
        "anomaly-kind.guten-tag-generation-config.schema.yaml",
        "formula.guten-tag-generation-config.schema.yaml",
        "oscillation.guten-tag-generation-config.schema.yaml"
    ]

    @staticmethod
    def schema_path(schema_id: str, path: Path = SCHEMA_FOLDER_PATH) -> Path:
        return path / schema_id

    @staticmethod
    def schema_name(schema_id: str, domain: str = SCHEMA_DOMAIN) -> str:
        return f"{domain}/{schema_id}"
