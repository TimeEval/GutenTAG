from typing import Optional

import numpy as np
import pandas as pd

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.global_variables import BASE_OSCILLATION_NAMES, TIMESTAMP
from ..utils.types import BOGenerationContext
from ..utils.default_values import default_values


class CustomInput(BaseOscillationInterface):
    "currently works for univariate data"
    KIND = BASE_OSCILLATION_NAMES.CUSTOM_INPUT

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None
    
    def generate_only_base(self,
                        ctx: BOGenerationContext,
                        length: Optional[int] = None,
                        input_timeseries_path: Optional[str] = None,
                        *args, **kwargs) -> np.ndarray:
        
        """
        Generate a 1-dimensional numpy array of length 'length' using the data from the input timeseries file.
        If 'length' or 'input_timeseries_path' is not provided, use the default values set in the 'self' object.

        Args:
            ctx (BOGenerationContext): Context object for base object generation.
            length (Optional[int]): Desired length of the generated array. (default is self.length)
            input_timeseries_path (Optional[str]): Path to the input timeseries file. (default is self.input_timeseries_path)

        Returns:
            np.ndarray: 1-dimensional array of the given length.
        """
        length = length or self.length
        input_timeseries_path = input_timeseries_path or self.input_timeseries_path
        df = pd.read_csv(input_timeseries_path, index_col=TIMESTAMP)
        data = df.values
        data = [_list[0] for _list in data]
        data = np.array(data)
        try:
            len(np.shape(data)) == 1
        except Exception:
            print("timeseries must be 1-d")
        length = len(data)
        return data
    

BaseOscillation.register(CustomInput.KIND, CustomInput)