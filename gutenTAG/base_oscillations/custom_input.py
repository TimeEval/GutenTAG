from typing import Optional, List

import numpy as np
import pandas as pd

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.global_variables import BASE_OSCILLATION_NAMES, TIMESTAMP
from ..utils.types import BOGenerationContext
from ..utils.default_values import default_values


class CustomInput(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.CUSTOM_INPUT

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None
    
    def generate_only_base(self,
                        ctx: BOGenerationContext,
                        length: Optional[int] = None,
                        input_timeseries_path_train: Optional[str] = None,
                        input_timeseries_path_test: Optional[str] = None,
                        usecols: Optional[List[str]] = None,
                        semi_supervised: Optional[bool] = None,
                        supervised: Optional[bool] = None,
                        *args, **kwargs) -> np.ndarray:
        
        """
             Generate a numpy array using the data from the input timeseries file.

             Args:
                 ctx (BOGenerationContext): The context object for base object generation.
                 length (Optional[int]): The desired length of the generated array. If not specified, default is self.length.
                 input_timeseries_path_train (Optional[str]): The path to the input timeseries file for training data. If not specified, default is self.input_timeseries_path_train.
                 input_timeseries_path_test (Optional[str]): The path to the input timeseries file for test data. If not specified, default is self.input_timeseries_path_test.
                 usecols (Optional[List[str]]): The list of column names to be returned from the CSV file. If not specified, default is None, which returns all columns.
                 semi_supervised (Optional[bool]): A flag indicating whether the generation is for semi-supervised learning. If not specified, default is None.
                 supervised (Optional[bool]): A flag indicating whether the generation is for supervised learning. If not specified, default is None.

             Returns:
                 np.ndarray: A 1-dimensional or multi-dimensional numpy array, depending on the selected columns.

             If `usecols` is not provided, or if it is `None`, the function will return all columns in the input CSV file. In this case, the dimensionality of the returned array will be the same as the original dataframe, which could be 1-dimensional or multi-dimensional, depending on the structure of the CSV file.

             If `usecols` is provided with a list of column names that selects only one column, the returned array will be 1-dimensional.

             If `usecols` is provided with a list of column names that selects multiple columns, the returned array will be multi-dimensional, with one dimension for each selected column.

             Raises:
                 ValueError: If the number of rows in the input timeseries file is less than the desired length.

        """
        length = length or self.length
        input_timeseries_path_train = input_timeseries_path_train or self.input_timeseries_path_train
        input_timeseries_path_test = input_timeseries_path_test or self.input_timeseries_path_test
        usecols = usecols or self.usecols
        usecols.append(TIMESTAMP)   


        if semi_supervised or supervised:
            df = pd.read_csv(input_timeseries_path_train, usecols=usecols, index_col=TIMESTAMP)
        else:
            df = pd.read_csv(input_timeseries_path_test, usecols=usecols, index_col=TIMESTAMP)
        if len(df) < length:
            raise ValueError("Number of rows in the input timeseries file is less than the desired length")
        return df.values[:,0]
    

BaseOscillation.register(CustomInput.KIND, CustomInput)
