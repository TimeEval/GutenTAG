from typing import Optional, List, Sequence, Union

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
                        input_timeseries_path_test: str = None,
                        use_column_test: Union[str, int] = None,
                        length: Optional[int] = None,
                        input_timeseries_path_train: Optional[str] = None,
                        use_column_train: Optional[Union[str, int]] = None,
                        semi_supervised: Optional[bool] = None,
                        supervised: Optional[bool] = None,
                        *args, **kwargs) -> np.ndarray:
        
        """
             Generates a numpy array of time-series data from a CSV file based on the specified parameters.

             Precondition: if specifying column with an integer, the timestamp column is at column index 0

             Args:
                 ctx (BOGenerationContext): An instance of the BOGenerationContext class.
                 input_timeseries_path_test (str, optional): The path to the test data CSV file. Defaults to None.
                 use_column_test (Union[str, int], optional): The name or index of the column containing the test data. 
                     Defaults to None.
                 length (Optional[int], optional): The desired length of the output time-series data. Defaults to None.
                 input_timeseries_path_train (Optional[str], optional): The path to the training data CSV file. 
                     Defaults to None.
                 use_column_train (Optional[Union[str, int]], optional): The name or index of the column containing the training data. 
                     Defaults to None.
                 semi_supervised (Optional[bool], optional): A flag to indicate if the model is trained in semi-supervised mode.
                     Defaults to None.
                 supervised (Optional[bool], optional): A flag to indicate if the model is trained in supervised mode.
                     Defaults to None.
                 *args: Variable length argument list.
                 **kwargs: Arbitrary keyword arguments.
             
             Returns:
                 np.ndarray: A numpy array of the generated time-series data.
             
             Raises:
                 ValueError: If the number of rows in the input timeseries file is less than the desired length.
             
             
        """
        length = length or self.length
        input_timeseries_path_train = input_timeseries_path_train or self.input_timeseries_path_train
        input_timeseries_path_test = input_timeseries_path_test or self.input_timeseries_path_test
        use_column_train = use_column_train or self.use_column_train
        use_column_test = use_column_test or self.use_column_test
        
        
        if isinstance(use_column_test,str):
            test_columns: List[Union[str, int]] = [TIMESTAMP, use_column_test]
            index_column_test: Union[str, int] = TIMESTAMP
        else:
            test_columns = [0, int(use_column_test)]
            index_column_test = 0
    
        if isinstance(use_column_train,str):
            train_columns: List[Union[str, int]] = [TIMESTAMP, use_column_train]
            index_column_train: Union[str, int] = TIMESTAMP
        else:
            train_columns = [0, int(use_column_train)]
            index_column_train = 0


        if semi_supervised or supervised:
            df = pd.read_csv(input_timeseries_path_train, usecols=train_columns, index_col=index_column_test)
        else:
            df = pd.read_csv(input_timeseries_path_test, usecols=test_columns, index_col=index_column_train)
        if len(df) < length:
            raise ValueError("Number of rows in the input timeseries file is less than the desired length")
        return df.iloc[:length, 0]
    

BaseOscillation.register(CustomInput.KIND, CustomInput)
