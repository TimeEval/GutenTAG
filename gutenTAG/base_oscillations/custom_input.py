from typing import Optional, List, Union

import numpy as np
import pandas as pd
import warnings

from . import BaseOscillation
from .interface import BaseOscillationInterface
from ..utils.global_variables import BASE_OSCILLATION_NAMES
from ..utils.types import BOGenerationContext


class CustomInput(BaseOscillationInterface):
    KIND = BASE_OSCILLATION_NAMES.CUSTOM_INPUT

    def get_base_oscillation_kind(self) -> str:
        return self.KIND

    def get_timeseries_periods(self) -> Optional[int]:
        return None

    def generate_only_base(
        self,
        ctx: BOGenerationContext,
        input_timeseries_path_test: str = None,
        use_column_test: Union[str, int] = None,
        length: Optional[int] = None,
        input_timeseries_path_train: Optional[str] = None,
        use_column_train: Optional[Union[str, int]] = None,
        semi_supervised: Optional[bool] = None,
        supervised: Optional[bool] = None,
        *args,
        **kwargs,
    ) -> np.ndarray:
        """Generates a numpy array of timeseries data from a CSV file based on the specified parameters.

        The following requirements must be met by the input file:

        - CSV file with the first line as the header.
        - The file should not contain any anomalies. Otherwise, the label information provided by GutenTAG will be
          wrong!
        - If the extracted channel is specified using an integer, the first column is column 0.
        - `custom-input` can extract only a single column/channel/dimension from the input file at a time. If multiple
          channels are required, you have to use the `custom-input` base oscillation multiple times.

        Arguments
        ---------
        ctx : BOGenerationContext
            An instance of the BOGenerationContext class.
        input_timeseries_path_test : str, optional
            The path to the test data CSV file. Defaults to None.
        use_column_test : Union[str, int], optional
            The name or index of the column containing the test data. Defaults to None.
        length : Optional[int], optional
            The desired length of the output time-series data. Defaults to None.
        input_timeseries_path_train : Optional[str], optional
            The path to the training data CSV file. Defaults to None.
        use_column_train : Optional[Union[str, int]], optional
            The name or index of the column containing the training data. Defaults to None.
        semi_supervised : Optional[bool], optional
            A flag to indicate if the model is trained in semi-supervised mode. Defaults to None.
        supervised : Optional[bool], optional
            A flag to indicate if the model is trained in supervised mode. Defaults to None.

        Returns
        -------
        np.ndarray
            A numpy array of the generated time-series data.

        Raises
        ------
        ValueError
            If the number of rows in the input timeseries file is less than the desired length.
        """
        length = length or self.length
        input_timeseries_path_train = (
            input_timeseries_path_train or self.input_timeseries_path_train
        )
        input_timeseries_path_test = (
            input_timeseries_path_test or self.input_timeseries_path_test
        )
        use_column_train = use_column_train or self.use_column_train
        use_column_test = use_column_test or self.use_column_test

        if semi_supervised or supervised:
            if input_timeseries_path_train is None:
                raise ValueError(
                    "No path to an input timeseries file for the training timeseries specified!"
                )

            df = pd.read_csv(input_timeseries_path_train, usecols=[use_column_train])

        else:
            if input_timeseries_path_test is None:
                raise ValueError("No path to an input timeseries file specified!")

            df = pd.read_csv(input_timeseries_path_test, usecols=[use_column_test])

        if len(df) < length:
            raise ValueError(
                "Number of rows in the input timeseries file is less than the desired length"
            )
        col_type = df.dtypes[0]
        if col_type != np.float_:
            df = df.astype(float)
            warnings.warn(
                f"Input data was of {col_type} type and has been automatically converted to float."
            )
        return df.iloc[:length, 0]


BaseOscillation.register(CustomInput.KIND, CustomInput)
