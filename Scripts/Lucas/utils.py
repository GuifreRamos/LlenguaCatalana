import pandas as pd
import numpy as np

def select_and_rename_columns(df, cols_dict):
    df = df[cols_dict.keys()]
    df = df.rename(columns=cols_dict)
    return df

def make_cols_numeric(df, cols):
    """This method takes in a Dataframe and a column name present
    in the Dataframe and makes the values of the columns numerical.
    All the while supposing that the column's values are
    of the form '1,5' for example."""
    for col in cols:
        df[col] = df[col].apply(lambda x: x.replace(',', '.'))
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def rescale_percentages(df, cols):
    """This method will take a column and rescale the
    values to percentages in a logarithmic way."""
    for col in cols:
        min_val = np.log(df[col].min())
        max_val = np.log(df[col].max())
        df[f"{col}_prct"] = 100 * (np.log(df[col]) - min_val) / (
                max_val - min_val)
    return df

def filter_df_by_column_value(df, columns, value):
    """
    Filters a Pandas DataFrame to include only rows
    where any of the specified columns has the given value.
    """
    if isinstance(columns, str):
        columns = [columns]

    filter_condition = df[columns].isin([value]).any(axis=1)
    return df[filter_condition]