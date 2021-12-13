SUPERVISED_FILENAME = "train_anomaly.csv"
SEMI_SUPERVISED_FILENAME = "train_no_anomaly.csv"
UNSUPERVISED_FILENAME = "test.csv"


BASE_OSCILLATION = "base-oscillation"
BASE_OSCILLATIONS = BASE_OSCILLATION + "s"
TIMESERIES = "timeseries"
ANOMALIES = "anomalies"


class BASE_OSCILLATION_NAMES:
    SINE = "sine"
    RANDOM_WALK = "random-walk"
    CYLINDER_BELL_FUNNEL = "cylinder-bell-funnel"
    ECG = "ecg"
    POLYNOMIAL = "polynomial"
    RANDOM_MODE_JUMP = "random-mode-jump"
    FORMULA = "formula"


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
    PARAMETERS = "parameters"
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
