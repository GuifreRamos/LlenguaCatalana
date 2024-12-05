import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def make_percentages(df, col_names, total_col_name):
    for col_name in col_names:
        df[col_names[col_name]] = 100 * df[col_name] / df[total_col_name]
    return df


def do_PCA(df, num_dims):
    # Standardize the dataset
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(df)

    # Apply PCA
    pca = PCA(n_components=num_dims)
    pca_result = pca.fit_transform(standardized_data)

    # Store PCA results in a DataFrame
    col_names = [f"PC{i}" for i in range(num_dims)]
    pca_df = pd.DataFrame(data=pca_result, columns=col_names, index=df.index)

    # Get the loadings
    loadings = pca.components_
    loading_df = pd.DataFrame(loadings, columns=df.columns, index=col_names)

    return loading_df, pca_df


def rescale_principal_components(df, cols):
    for col in cols:
        df[col] = df[col] - df[col].min()
        print(df[col])
        max_val = df[col].max()
        df[f"{col}_prct"] = 100 * df[col] / max_val
        print(df[f"{col}_prct"])
    return df


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
        if pd.api.types.is_string_dtype(df[col].dtype):
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