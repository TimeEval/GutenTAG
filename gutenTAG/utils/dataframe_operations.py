import pandas as pd


def columns_to_separate_csvs(d: pd.DataFrame, output_folder_path: str) -> None:
    """Store all dataframe columns in separate csv files
    where the file name equals the column name"""
    for column in d.columns:
        d[column].to_csv(output_folder_path.joinpath(f'{column}.csv'))