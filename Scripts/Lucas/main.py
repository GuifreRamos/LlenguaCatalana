import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from pandas import merge
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.gridspec as gridspec

from utils import select_and_rename_columns, make_cols_numeric, rescale_percentages, rescale_principal_components
from imaging import create_bivariate_plot_matplotlib, biplot, create_bivariate_plot_matplotlib_final
import os

def first_intent():
    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"

    # In the following we will consider data from 2011
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    # Load population data
    pop_df = pd.read_csv(data_dir + "pop_gen_1_comarques.csv", delimiter=';')
    # Select relevant population data columns and rename
    cols_dict = {
        'Unnamed: 0': "nom_comar",
        "2011": "pop_2011",
    }
    pop_df = select_and_rename_columns(pop_df, cols_dict)
    pop_df = make_cols_numeric(pop_df, ['pop_2011'])
    pop_df.loc[pop_df['nom_comar'] == "Aran", 'nom_comar'] = "Val d'Aran"
    # Merge Dataframes obtained up until now
    df = pd.merge(com_df, pop_df)
    # Rescale
    df = rescale_percentages(df, cols=['pop_2011'])
    # Load catalan knowledge data
    cat_knowledge_df = pd.read_csv(data_dir + "cat2011.csv", delimiter=';')
    # Make Dataframe compatible
    cols_dict = {
        "Unnamed: 0": "nom_comar",
        "% sap parlar": "talks",
    }
    cat_knowledge_df = select_and_rename_columns(cat_knowledge_df, cols_dict)
    # Merge again
    df = pd.merge(df, cat_knowledge_df)
    # Make Numeric and rescale
    df = make_cols_numeric(df, ["talks"])
    df = rescale_percentages(df, cols=['talks'])
    print(df["pop_2011_prct"])
    print(df["talks_prct"])
    # Create Bivariate
    create_bivariate_plot_matplotlib(df, "pop_2011_prct", "talks_prct", file_name="PopvsTalk2011",
                                     x_axis_name="Population", y_axis_name="Talking Ability",
                                     title="Population vs Talking Ability 2011")


def second_intent():
    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"
    # In the following we will consider data from 2011
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    # Load population data
    niv_df = pd.read_csv(data_dir + "nivell_formacio_assolit.csv", delimiter=';')
    df = pd.merge(com_df, niv_df)
    cat_knowledge_df = pd.read_csv(data_dir + "cat2011.csv", delimiter=';')
    cols_dict = {
        "Unnamed: 0": "nom_comar",
    }
    cat_knowledge_df = cat_knowledge_df.rename(columns=cols_dict)
    df = pd.merge(df, cat_knowledge_df)

    # Make Columns Numeric
    cols_list = [
        "Població de 2 anys i més", "L'entén", "El sap parlar",
        "El sap llegir", "El sap escriure", "No l'entén", "No sap llegir o escriure",
        "Total", "No sap llegir o escriure", "Sense estudis", "Educació primària",
        "ESO", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
        "Diplomatura", "Grau universitari", "Llicenciatura i doctorat"
    ]
    df = make_cols_numeric(df, cols_list)

    # Make Language Proficiency Percentage Columns
    df["understands_prct"] = 100 * df["L'entén"] / df["Població de 2 anys i més"]
    df["speaks_prct"] = 100 * df["El sap parlar"] / df["Població de 2 anys i més"]
    df["reads_prct"] = 100 * df["El sap llegir"] / df["Població de 2 anys i més"]
    df["writes_prct"] = 100 * df["El sap escriure"] / df["Població de 2 anys i més"]

    # Make Education Level Percentages
    df["no_diploma_prct"] = 100 * df["Sense estudis"] / df["Total"]
    df["primary_diploma_prct"] =100 * df["Educació primària"] / df["Total"]
    df["ESO_diploma_prct"] = 100 * df["ESO"] / df["Total"]
    df["batxi_diploma_prct"] = 100 * df["Batxillerat superior"] / df["Total"]
    df["professional_middle_degree_diploma_prct"] = 100 * df["FP grau mitjà"] / df["Total"]
    df["professional_degree_diploma_prct"] = 100 * df["FP grau superior"] / df["Total"]
    df["old_university_degree_diploma_prct"] = 100 * df["Diplomatura"] / df["Total"]
    df["university_degree_diploma_prct"] = 100 * df["Grau universitari"] / df["Total"]
    df["master_and_doctor_diploma_prct"] = 100 * df["Llicenciatura i doctorat"] / df["Total"]

    # Filter important columns
    col_list = [
        "understands_prct", "speaks_prct", "reads_prct",
        "writes_prct", "no_diploma_prct", "primary_diploma_prct", "ESO_diploma_prct",
        "batxi_diploma_prct", "professional_middle_degree_diploma_prct",
        "professional_degree_diploma_prct", "old_university_degree_diploma_prct",
        "university_degree_diploma_prct", "master_and_doctor_diploma_prct",
        "nom_comar",
    ]
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    print(df.isnull().any())

    # Standardize the dataset
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(df)

    # Apply PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(standardized_data)

    # Store PCA results in a DataFrame
    pca_df = pd.DataFrame(data=pca_result, columns=['PC1', 'PC2'], index=df.index)

    # Get the loadings
    loadings = pca.components_
    loading_df = pd.DataFrame(loadings, columns=df.columns, index=['PC1', 'PC2'])
    biplot(pca_df, loading_df.T, labels=df.index)

    # Add geometry etc.
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, pca_df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC1", "PC2"])
    create_bivariate_plot_matplotlib(df, 'PC2_prct', 'PC1_prct', file_name="MatplotlibBivariatePlotPCA",
                                     x_axis_name="Advanced education and Catalan",
                                     y_axis_name="Basic education and Catalan", )

def third_intent():
    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"
    # Load population data
    df = pd.read_csv(data_dir + "nivell_formacio_assolit.csv", delimiter=';')
    # Make Columns Numeric
    cols_list = [
        "Total", "No sap llegir o escriure", "Sense estudis", "Educació primària",
        "ESO", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
        "Diplomatura", "Grau universitari", "Llicenciatura i doctorat"
    ]
    df = make_cols_numeric(df, cols_list)
    # Make Education Level Percentages
    df["no_diploma_prct"] = 100 * df["Sense estudis"] / df["Total"]
    df["primary_diploma_prct"] = 100 * df["Educació primària"] / df["Total"]
    df["ESO_diploma_prct"] = 100 * df["ESO"] / df["Total"]
    df["batxi_diploma_prct"] = 100 * df["Batxillerat superior"] / df["Total"]
    df["professional_middle_degree_diploma_prct"] = 100 * df["FP grau mitjà"] / df["Total"]
    df["professional_degree_diploma_prct"] = 100 * df["FP grau superior"] / df["Total"]
    df["old_university_degree_diploma_prct"] = 100 * df["Diplomatura"] / df["Total"]
    df["university_degree_diploma_prct"] = 100 * df["Grau universitari"] / df["Total"]
    df["master_and_doctor_diploma_prct"] = 100 * df["Llicenciatura i doctorat"] / df["Total"]

    # Filter important columns
    col_list = [
        "no_diploma_prct", "primary_diploma_prct", "ESO_diploma_prct",
        "batxi_diploma_prct", "professional_middle_degree_diploma_prct",
        "professional_degree_diploma_prct", "old_university_degree_diploma_prct",
        "university_degree_diploma_prct", "master_and_doctor_diploma_prct",
        "nom_comar",
    ]
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    print(df.isnull().any())

    # Standardize the dataset
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(standardized_data)

    # Store PCA results in a DataFrame
    pca_df = pd.DataFrame(data=pca_result, columns=['PC_Educational'], index=df.index)
    print(pca_df)

    # Get the loadings
    loadings = pca.components_
    loading_df = pd.DataFrame(loadings, columns=df.columns, index=['PC_Educational'])
    print(loading_df.T)

    # Catalan Knowledge
    cat_knowledge_df = pd.read_csv(data_dir + "cat2011.csv", delimiter=';')
    cols_dict = {
        "Unnamed: 0": "nom_comar",
    }
    cat_knowledge_df = cat_knowledge_df.rename(columns=cols_dict)
    print(cat_knowledge_df.columns)

    # Make Columns Numeric
    cols_list = [
        "Població de 2 anys i més", "L'entén", "El sap parlar",
        "El sap llegir", "El sap escriure"
    ]
    cat_knowledge_df = make_cols_numeric(cat_knowledge_df, cols_list)

    # Make Language Proficiency Percentage Columns
    cat_knowledge_df["understands_prct"] = 100 * cat_knowledge_df["L'entén"] / cat_knowledge_df["Població de 2 anys i més"]
    cat_knowledge_df["speaks_prct"] = 100 * cat_knowledge_df["El sap parlar"] / cat_knowledge_df["Població de 2 anys i més"]
    cat_knowledge_df["reads_prct"] = 100 * cat_knowledge_df["El sap llegir"] / cat_knowledge_df["Població de 2 anys i més"]
    cat_knowledge_df["writes_prct"] = 100 * cat_knowledge_df["El sap escriure"] / cat_knowledge_df["Població de 2 anys i més"]

    # Filter important columns
    col_list = [
        "nom_comar", "understands_prct", "speaks_prct",
        "reads_prct", "writes_prct"
    ]
    cat_knowledge_df = cat_knowledge_df[col_list]
    cat_knowledge_df.set_index('nom_comar', inplace=True)

    # Standardize the dataset
    scaler = StandardScaler()
    cat_knowledge_standardized_data = scaler.fit_transform(cat_knowledge_df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(cat_knowledge_standardized_data)

    # Store PCA results in a DataFrame
    cat_knowledge_pca_df = pd.DataFrame(data=pca_result, columns=['PC_Catalan'], index=df.index)
    print(cat_knowledge_pca_df)

    # Get the loadings
    loadings = pca.components_
    cat_knowledge_loading_df = pd.DataFrame(loadings, columns=cat_knowledge_df.columns, index=['PC_Catalan'])
    print(cat_knowledge_loading_df.T)

    df = merge(cat_knowledge_pca_df, pca_df, left_index=True, right_index=True)
    print(df)

    # Add geometry etc.
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC_Educational", "PC_Catalan"])
    print(df)
    create_bivariate_plot_matplotlib(df, 'PC_Educational_prct', 'PC_Catalan_prct',
                                     file_name="EduvsCat_2011", x_axis_name="Educational Level",
                                     y_axis_name="Catalan Level", title="Education vs Catalan Level")


def fourth_intent():
    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"

    # In the following we will consider data from 2011
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    # Load population data
    pop_df = pd.read_csv(data_dir + "pop_gen_1_comarques.csv", delimiter=';')
    # Select relevant population data columns and rename
    cols_dict = {
        'Unnamed: 0': "nom_comar",
        "2001": "pop",
    }
    pop_df = select_and_rename_columns(pop_df, cols_dict)
    pop_df = make_cols_numeric(pop_df, ['pop'])
    pop_df.loc[pop_df['nom_comar'] == "Aran", 'nom_comar'] = "Val d'Aran"
    # Merge Dataframes obtained up until now
    df = pd.merge(com_df, pop_df)
    # Rescale
    df = rescale_percentages(df, cols=['pop'])
    # Load catalan knowledge data
    cat_knowledge_df = pd.read_csv(data_dir + "cat2001.csv", delimiter=';')
    # Make Dataframe compatible
    cols_dict = {
        "Unnamed: 0": "nom_comar",
        "% sap parlar": "talks",
    }
    cat_knowledge_df = select_and_rename_columns(cat_knowledge_df, cols_dict)
    # Merge again
    df = pd.merge(df, cat_knowledge_df)
    # Make Numeric and rescale
    df = make_cols_numeric(df, ["talks"])
    df = rescale_percentages(df, cols=['talks'])
    print(df["pop_prct"])
    print(df["talks_prct"])
    # Create Bivariate
    create_bivariate_plot_matplotlib(df, "pop_prct", "talks_prct", file_name="PopvsTalk2001",
                                     x_axis_name="Population", y_axis_name="Talking Ability",
                                     title="Population vs Talking Ability 2001")


def fifth_intent():
    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"
    # Load population data
    df = pd.read_csv(data_dir + "t15743200100.csv", delimiter=';')
    print(df.columns)
    # Make Columns Numeric
    cols_list = [
        "Total", "No sap llegir o escriure", "Sense estudis", "Primer grau",
        "ESO, EGB, Batx. elem.", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
        "Diplomatura", "Llicenciatura i doctorat"
    ]
    df = make_cols_numeric(df, cols_list)
    # Make Education Level Percentages
    df["analfabetic_prct"] = 100 * df["No sap llegir o escriure"] / df["Total"]
    df["no_diploma_prct"] = 100 * df["Sense estudis"] / df["Total"]
    df["primary_diploma_prct"] = 100 * df["Primer grau"] / df["Total"]
    df["ESO_diploma_prct"] = 100 * df["ESO, EGB, Batx. elem."] / df["Total"]
    df["batxi_diploma_prct"] = 100 * df["Batxillerat superior"] / df["Total"]
    df["professional_middle_degree_diploma_prct"] = 100 * df["FP grau mitjà"] / df["Total"]
    df["professional_degree_diploma_prct"] = 100 * df["FP grau superior"] / df["Total"]
    df["old_university_degree_diploma_prct"] = 100 * df["Diplomatura"] / df["Total"]
    df["master_and_doctor_diploma_prct"] = 100 * df["Llicenciatura i doctorat"] / df["Total"]

    # Filter important columns
    col_list = [
        "no_diploma_prct", "primary_diploma_prct", "ESO_diploma_prct",
        "batxi_diploma_prct", "professional_middle_degree_diploma_prct",
        "professional_degree_diploma_prct", "old_university_degree_diploma_prct",
        "master_and_doctor_diploma_prct", "nom_comar", "analfabetic_prct"
    ]
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    print(df.isnull().any())

    # Standardize the dataset
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(standardized_data)

    # Store PCA results in a DataFrame
    pca_df = pd.DataFrame(data=pca_result, columns=['PC_Educational'], index=df.index)
    print(pca_df)

    # Get the loadings
    loadings = pca.components_
    loading_df = pd.DataFrame(loadings, columns=df.columns, index=['PC_Educational'])
    print(loading_df.T)

    # Catalan Knowledge
    cat_knowledge_df = pd.read_csv(data_dir + "cat2001.csv", delimiter=';')
    cols_dict = {
        "Unnamed: 0": "nom_comar",
    }
    cat_knowledge_df = cat_knowledge_df.rename(columns=cols_dict)
    print(cat_knowledge_df.columns)

    # Make Columns Numeric
    cols_list = [
        "Població de 2 anys i més", "L'entén", "El sap parlar",
        "El sap llegir", "El sap escriure"
    ]
    cat_knowledge_df = make_cols_numeric(cat_knowledge_df, cols_list)

    # Make Language Proficiency Percentage Columns
    cat_knowledge_df["understands_prct"] = 100 * cat_knowledge_df["L'entén"] / cat_knowledge_df["Població de 2 anys i més"]
    cat_knowledge_df["speaks_prct"] = 100 * cat_knowledge_df["El sap parlar"] / cat_knowledge_df["Població de 2 anys i més"]
    cat_knowledge_df["reads_prct"] = 100 * cat_knowledge_df["El sap llegir"] / cat_knowledge_df["Població de 2 anys i més"]
    cat_knowledge_df["writes_prct"] = 100 * cat_knowledge_df["El sap escriure"] / cat_knowledge_df["Població de 2 anys i més"]

    # Filter important columns
    col_list = [
        "nom_comar", "understands_prct", "speaks_prct",
        "reads_prct", "writes_prct"
    ]
    cat_knowledge_df = cat_knowledge_df[col_list]
    cat_knowledge_df.set_index('nom_comar', inplace=True)

    # Standardize the dataset
    scaler = StandardScaler()
    cat_knowledge_standardized_data = scaler.fit_transform(cat_knowledge_df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(cat_knowledge_standardized_data)

    # Store PCA results in a DataFrame
    cat_knowledge_pca_df = pd.DataFrame(data=pca_result, columns=['PC_Catalan'], index=df.index)
    print(cat_knowledge_pca_df)

    # Get the loadings
    loadings = pca.components_
    cat_knowledge_loading_df = pd.DataFrame(loadings, columns=cat_knowledge_df.columns, index=['PC_Catalan'])
    print(cat_knowledge_loading_df.T)

    df = merge(cat_knowledge_pca_df, pca_df, left_index=True, right_index=True)
    print(df)

    # Add geometry etc.
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC_Educational", "PC_Catalan"])
    print(df)
    create_bivariate_plot_matplotlib(df, 'PC_Educational_prct', 'PC_Catalan_prct',
                                     file_name="EduvsCat_2001", x_axis_name="Educational Level",
                                     y_axis_name="Catalan Level", title="Education vs Catalan Level")


def final_piece():
    fig = plt.figure(constrained_layout=True, figsize=(10, 10))
    subplots = fig.subfigures(2, 2)

    fig1 = subplots[0][0]
    fig2 = subplots[0][1]
    fig3 = subplots[1][0]
    fig4 = subplots[1][1]

    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"

    # In the following we will consider data from 2011
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    # Load population data
    pop_df = pd.read_csv(data_dir + "pop_gen_1_comarques.csv", delimiter=';')
    # Select relevant population data columns and rename
    cols_dict = {
        'Unnamed: 0': "nom_comar",
        "2011": "pop_2011",
    }
    pop_df = select_and_rename_columns(pop_df, cols_dict)
    pop_df = make_cols_numeric(pop_df, ['pop_2011'])
    pop_df.loc[pop_df['nom_comar'] == "Aran", 'nom_comar'] = "Val d'Aran"
    # Merge Dataframes obtained up until now
    df = pd.merge(com_df, pop_df)
    # Rescale
    df = rescale_percentages(df, cols=['pop_2011'])
    # Load catalan knowledge data
    cat_knowledge_df = pd.read_csv(data_dir + "cat2011.csv", delimiter=';')
    # Make Dataframe compatible
    cols_dict = {
        "Unnamed: 0": "nom_comar",
        "% sap parlar": "talks",
    }
    cat_knowledge_df = select_and_rename_columns(cat_knowledge_df, cols_dict)
    # Merge again
    df = pd.merge(df, cat_knowledge_df)
    # Make Numeric and rescale
    df = make_cols_numeric(df, ["talks"])
    df = rescale_percentages(df, cols=['talks'])
    print(df["pop_2011_prct"])
    print(df["talks_prct"])
    # Create Bivariate
    create_bivariate_plot_matplotlib_final(fig2, df, "pop_2011_prct", "talks_prct",
                                           file_name="PopvsTalk2011",
                                           x_axis_name="Population", y_axis_name="Talking Ability",
                                           title="Population vs Talking Ability 2011")

    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"
    # Load population data
    df = pd.read_csv(data_dir + "t15743200100.csv", delimiter=';')
    print(df.columns)
    # Make Columns Numeric
    cols_list = [
        "Total", "No sap llegir o escriure", "Sense estudis", "Primer grau",
        "ESO, EGB, Batx. elem.", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
        "Diplomatura", "Llicenciatura i doctorat"
    ]
    df = make_cols_numeric(df, cols_list)
    # Make Education Level Percentages
    df["analfabetic_prct"] = 100 * df["No sap llegir o escriure"] / df["Total"]
    df["no_diploma_prct"] = 100 * df["Sense estudis"] / df["Total"]
    df["primary_diploma_prct"] = 100 * df["Primer grau"] / df["Total"]
    df["ESO_diploma_prct"] = 100 * df["ESO, EGB, Batx. elem."] / df["Total"]
    df["batxi_diploma_prct"] = 100 * df["Batxillerat superior"] / df["Total"]
    df["professional_middle_degree_diploma_prct"] = 100 * df["FP grau mitjà"] / df["Total"]
    df["professional_degree_diploma_prct"] = 100 * df["FP grau superior"] / df["Total"]
    df["old_university_degree_diploma_prct"] = 100 * df["Diplomatura"] / df["Total"]
    df["master_and_doctor_diploma_prct"] = 100 * df["Llicenciatura i doctorat"] / df["Total"]

    # Filter important columns
    col_list = [
        "no_diploma_prct", "primary_diploma_prct", "ESO_diploma_prct",
        "batxi_diploma_prct", "professional_middle_degree_diploma_prct",
        "professional_degree_diploma_prct", "old_university_degree_diploma_prct",
        "master_and_doctor_diploma_prct", "nom_comar", "analfabetic_prct"
    ]
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    print(df.isnull().any())

    # Standardize the dataset
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(standardized_data)

    # Store PCA results in a DataFrame
    pca_df = pd.DataFrame(data=pca_result, columns=['PC_Educational'], index=df.index)
    print(pca_df)

    # Get the loadings
    loadings = pca.components_
    loading_df = pd.DataFrame(loadings, columns=df.columns, index=['PC_Educational'])
    print(loading_df.T)

    # Catalan Knowledge
    cat_knowledge_df = pd.read_csv(data_dir + "cat2001.csv", delimiter=';')
    cols_dict = {
        "Unnamed: 0": "nom_comar",
    }
    cat_knowledge_df = cat_knowledge_df.rename(columns=cols_dict)
    print(cat_knowledge_df.columns)

    # Make Columns Numeric
    cols_list = [
        "Població de 2 anys i més", "L'entén", "El sap parlar",
        "El sap llegir", "El sap escriure"
    ]
    cat_knowledge_df = make_cols_numeric(cat_knowledge_df, cols_list)

    # Make Language Proficiency Percentage Columns
    cat_knowledge_df["understands_prct"] = 100 * cat_knowledge_df["L'entén"] / cat_knowledge_df[
        "Població de 2 anys i més"]
    cat_knowledge_df["speaks_prct"] = 100 * cat_knowledge_df["El sap parlar"] / cat_knowledge_df[
        "Població de 2 anys i més"]
    cat_knowledge_df["reads_prct"] = 100 * cat_knowledge_df["El sap llegir"] / cat_knowledge_df[
        "Població de 2 anys i més"]
    cat_knowledge_df["writes_prct"] = 100 * cat_knowledge_df["El sap escriure"] / cat_knowledge_df[
        "Població de 2 anys i més"]

    # Filter important columns
    col_list = [
        "nom_comar", "understands_prct", "speaks_prct",
        "reads_prct", "writes_prct"
    ]
    cat_knowledge_df = cat_knowledge_df[col_list]
    cat_knowledge_df.set_index('nom_comar', inplace=True)

    # Standardize the dataset
    scaler = StandardScaler()
    cat_knowledge_standardized_data = scaler.fit_transform(cat_knowledge_df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(cat_knowledge_standardized_data)

    # Store PCA results in a DataFrame
    cat_knowledge_pca_df = pd.DataFrame(data=pca_result, columns=['PC_Catalan'], index=df.index)
    print(cat_knowledge_pca_df)

    # Get the loadings
    loadings = pca.components_
    cat_knowledge_loading_df = pd.DataFrame(loadings, columns=cat_knowledge_df.columns, index=['PC_Catalan'])
    print(cat_knowledge_loading_df.T)

    df = merge(cat_knowledge_pca_df, pca_df, left_index=True, right_index=True)
    print(df)

    # Add geometry etc.
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC_Educational", "PC_Catalan"])
    print(df)
    create_bivariate_plot_matplotlib_final(fig3, df, 'PC_Educational_prct', 'PC_Catalan_prct',
                                     file_name="EduvsCat_2001", x_axis_name="Educational Level",
                                     y_axis_name="Catalan Level", title="Education vs Catalan Level")

    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"

    # In the following we will consider data from 2011
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    # Load population data
    pop_df = pd.read_csv(data_dir + "pop_gen_1_comarques.csv", delimiter=';')
    # Select relevant population data columns and rename
    cols_dict = {
        'Unnamed: 0': "nom_comar",
        "2001": "pop",
    }
    pop_df = select_and_rename_columns(pop_df, cols_dict)
    pop_df = make_cols_numeric(pop_df, ['pop'])
    pop_df.loc[pop_df['nom_comar'] == "Aran", 'nom_comar'] = "Val d'Aran"
    # Merge Dataframes obtained up until now
    df = pd.merge(com_df, pop_df)
    # Rescale
    df = rescale_percentages(df, cols=['pop'])
    # Load catalan knowledge data
    cat_knowledge_df = pd.read_csv(data_dir + "cat2001.csv", delimiter=';')
    # Make Dataframe compatible
    cols_dict = {
        "Unnamed: 0": "nom_comar",
        "% sap parlar": "talks",
    }
    cat_knowledge_df = select_and_rename_columns(cat_knowledge_df, cols_dict)
    # Merge again
    df = pd.merge(df, cat_knowledge_df)
    # Make Numeric and rescale
    df = make_cols_numeric(df, ["talks"])
    df = rescale_percentages(df, cols=['talks'])
    print(df["pop_prct"])
    print(df["talks_prct"])
    # Create Bivariate
    create_bivariate_plot_matplotlib_final(fig1, df, "pop_prct", "talks_prct", file_name="PopvsTalk2001",
                                     x_axis_name="Population", y_axis_name="Talking Ability",
                                     title="Population vs Talking Ability 2001")

    data_dir = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"
    # Load population data
    df = pd.read_csv(data_dir + "nivell_formacio_assolit.csv", delimiter=';')
    # Make Columns Numeric
    cols_list = [
        "Total", "No sap llegir o escriure", "Sense estudis", "Educació primària",
        "ESO", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
        "Diplomatura", "Grau universitari", "Llicenciatura i doctorat"
    ]
    df = make_cols_numeric(df, cols_list)
    # Make Education Level Percentages
    df["no_diploma_prct"] = 100 * df["Sense estudis"] / df["Total"]
    df["primary_diploma_prct"] = 100 * df["Educació primària"] / df["Total"]
    df["ESO_diploma_prct"] = 100 * df["ESO"] / df["Total"]
    df["batxi_diploma_prct"] = 100 * df["Batxillerat superior"] / df["Total"]
    df["professional_middle_degree_diploma_prct"] = 100 * df["FP grau mitjà"] / df["Total"]
    df["professional_degree_diploma_prct"] = 100 * df["FP grau superior"] / df["Total"]
    df["old_university_degree_diploma_prct"] = 100 * df["Diplomatura"] / df["Total"]
    df["university_degree_diploma_prct"] = 100 * df["Grau universitari"] / df["Total"]
    df["master_and_doctor_diploma_prct"] = 100 * df["Llicenciatura i doctorat"] / df["Total"]

    # Filter important columns
    col_list = [
        "no_diploma_prct", "primary_diploma_prct", "ESO_diploma_prct",
        "batxi_diploma_prct", "professional_middle_degree_diploma_prct",
        "professional_degree_diploma_prct", "old_university_degree_diploma_prct",
        "university_degree_diploma_prct", "master_and_doctor_diploma_prct",
        "nom_comar",
    ]
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    print(df.isnull().any())

    # Standardize the dataset
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(standardized_data)

    # Store PCA results in a DataFrame
    pca_df = pd.DataFrame(data=pca_result, columns=['PC_Educational'], index=df.index)
    print(pca_df)

    # Get the loadings
    loadings = pca.components_
    loading_df = pd.DataFrame(loadings, columns=df.columns, index=['PC_Educational'])
    print(loading_df.T)

    # Catalan Knowledge
    cat_knowledge_df = pd.read_csv(data_dir + "cat2011.csv", delimiter=';')
    cols_dict = {
        "Unnamed: 0": "nom_comar",
    }
    cat_knowledge_df = cat_knowledge_df.rename(columns=cols_dict)
    print(cat_knowledge_df.columns)

    # Make Columns Numeric
    cols_list = [
        "Població de 2 anys i més", "L'entén", "El sap parlar",
        "El sap llegir", "El sap escriure"
    ]
    cat_knowledge_df = make_cols_numeric(cat_knowledge_df, cols_list)

    # Make Language Proficiency Percentage Columns
    cat_knowledge_df["understands_prct"] = 100 * cat_knowledge_df["L'entén"] / cat_knowledge_df[
        "Població de 2 anys i més"]
    cat_knowledge_df["speaks_prct"] = 100 * cat_knowledge_df["El sap parlar"] / cat_knowledge_df[
        "Població de 2 anys i més"]
    cat_knowledge_df["reads_prct"] = 100 * cat_knowledge_df["El sap llegir"] / cat_knowledge_df[
        "Població de 2 anys i més"]
    cat_knowledge_df["writes_prct"] = 100 * cat_knowledge_df["El sap escriure"] / cat_knowledge_df[
        "Població de 2 anys i més"]

    # Filter important columns
    col_list = [
        "nom_comar", "understands_prct", "speaks_prct",
        "reads_prct", "writes_prct"
    ]
    cat_knowledge_df = cat_knowledge_df[col_list]
    cat_knowledge_df.set_index('nom_comar', inplace=True)

    # Standardize the dataset
    scaler = StandardScaler()
    cat_knowledge_standardized_data = scaler.fit_transform(cat_knowledge_df)

    # Apply PCA
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(cat_knowledge_standardized_data)

    # Store PCA results in a DataFrame
    cat_knowledge_pca_df = pd.DataFrame(data=pca_result, columns=['PC_Catalan'], index=df.index)
    print(cat_knowledge_pca_df)

    # Get the loadings
    loadings = pca.components_
    cat_knowledge_loading_df = pd.DataFrame(loadings, columns=cat_knowledge_df.columns, index=['PC_Catalan'])
    print(cat_knowledge_loading_df.T)

    df = merge(cat_knowledge_pca_df, pca_df, left_index=True, right_index=True)
    print(df)

    # Add geometry etc.
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(data_dir + "comarq.geojson")
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC_Educational", "PC_Catalan"])
    print(df)
    create_bivariate_plot_matplotlib_final(fig4, df, 'PC_Educational_prct', 'PC_Catalan_prct',
                                     file_name="EduvsCat_2011", x_axis_name="Educational Level",
                                     y_axis_name="Catalan Level", title="Education vs Catalan Level")

    saving_dir = f"{os.path.dirname(__file__)}/../../Figures/Lucas/"

    plt.savefig(f"{saving_dir}FinalPiece.jpg", bbox_inches='tight')

final_piece()