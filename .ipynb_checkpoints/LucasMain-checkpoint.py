import pandas as pd
import matplotlib.pyplot as plt

import tkinter
root = tkinter.Tk()
print(root.tk.exprstring('$tcl_library'))
print(root.tk.exprstring('$tk_library'))


def filter_df_by_column_value(df, columns, value):
    """
    Filters a Pandas DataFrame to include only rows where any of the specified columns has the given value.

    Parameters:
    df (pandas.DataFrame): The input DataFrame to filter.
    columns (str or list of str): The column(s) to filter by. Can be a single column name or a list of column names.
    value (any): The value to filter the DataFrame by. Defaults to 2015.

    Returns:
    pandas.DataFrame: The filtered DataFrame.
    """
    if isinstance(columns, str):
        columns = [columns]

    filter_condition = df[columns].isin([value]).any(axis=1)
    return df[filter_condition]


df = pd.read_csv("dades/ist-14074-15022-com.csv", delimiter=';')

print("Data Overview:")
print(df.head())

df = df.dropna(subset=['comarca o Aran'])
df = df.astype({
    'any': int,
    'comarca o Aran': str,
    'concepte': str,
    'estat': str,
    'valor': str,
})

print(df.dtypes)
df['valor'] = df['valor'].apply(lambda x: x.replace(',', '.'))
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
for i in df['valor']:
    print(i)

print("Columns : ")
for col in df.columns:
    print(f" - {col}")

# Exploratory Data Analysis
print("Data Overview:")
print(df.head())
print("\nData Types:")
print(df.dtypes)
print("\nDescriptive Statistics:")
print(df.describe())

df_2015 = filter_df_by_column_value(df, ["any"], 2020)
df_2015_estudis_baixos = filter_df_by_column_value(df_2015,['concepte'], 'població amb estudis baixos (%)')

print(df_2015_estudis_baixos)

plt.bar(df_2015_estudis_baixos['comarca o Aran'], df_2015_estudis_baixos['valor'])
plt.xticks(rotation='vertical')
plt.show()