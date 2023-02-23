from ast import List
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
                        usecols: Optional[List[str]] = None,
                        *args, **kwargs) -> np.ndarray:
        
        """
        Generate a numpy array using the data from the input timeseries file.

        Args:
            ctx (BOGenerationContext): Context object for base object generation.
            length (Optional[int]): Desired length of the generated array. (default is self.length)
            input_timeseries_path (Optional[str]): Path to the input timeseries file. (default is self.input_timeseries_path)
            usecols (Optional[List[str]]): List of column names to be returned from the CSV file. (default is None, which returns all columns)

        Returns:
            np.ndarray: A 1-dimensional or multi-dimensional numpy array, depending on the selected columns.

        If `usecols` is not provided, or if it is `None`, the function will return all columns in the input CSV file. In this case, the dimensionality of the returned array will be the same as the original dataframe, which could be 1-dimensional or multi-dimensional, depending on the structure of the CSV file.

        If `usecols` is provided with a list of column names that selects only one column, the returned array will be 1-dimensional.

        If `usecols` is provided with a list of column names that selects multiple columns, the returned array will be multi-dimensional, with one dimension for each selected column.
        """
        length = length or self.length
        input_timeseries_path = input_timeseries_path or self.input_timeseries_path
        df = pd.read_csv(input_timeseries_path, usecols=usecols, index_col=TIMESTAMP)
        if len(df) < length:
            raise ValueError("Number of rows in the input timeseries file is less than the desired length")
        return df.values[:,0]
    

BaseOscillation.register(CustomInput.KIND, CustomInput)
