from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler

from gutenTAG.base_oscillations.utils.math_func_support import calc_n_periods

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.global_variables import BASE_OSCILLATION_NAMES, TIMESTAMP
from ..utils.types import BOGenerationContext
from ..utils.default_values import default_values


class CustomProcess(BaseOscillationInterface):
    "currently works for univariate data"
    KIND = BASE_OSCILLATION_NAMES.CUSTOM_PROCESS

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None
    
    def generate_only_base(self,
                        ctx: BOGenerationContext,
                        length: Optional[int] = None,
                        input_timeseries_path: Optional[str] = None,
                        *args, **kwargs) -> np.ndarray:
        length = length or self.length
        input_timeseries_path = input_timeseries_path or self.input_timeseries_path
        df = pd.read_csv(input_timeseries_path, index_col=TIMESTAMP)
        data = df.values
        data = [_list[0] for _list in data]
        data = np.array(data)
        assert len(np.shape(data)) == 1, "timeseries must be 1-d"
        length = len(data)
        return data
    

    # def custom_process(source_ts_path: str,
    #                     length: int = default_values[BASE_OSCILLATIONS][PARAMETERS]
    #                     ) -> np.ndarray:
    #     ts_df = pd.read_csv(source_ts_path, parse_dates=True, index_col="timestamp")
    #     synthesizer: Syntesizer = Syntesizer()
    #     synthesizer.fit(ts_df)

    #     return None

BaseOscillation.register(CustomProcess.KIND, CustomProcess)