import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from pandas import merge
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from utils import select_and_rename_columns, make_cols_numeric, \
    rescale_percentages, rescale_principal_components, make_percentages, do_PCA
from imaging import create_bivariate_plot_matplotlib, biplot, create_bivariate_plot_matplotlib_final
import os

DATA_DIR = f"{os.path.dirname(__file__)}/../../Dades/Lucas/"


def make_popvtalk_plot(year):
    # Initializing som variables to be used
    pop_col = f"pop_{year}"
    cat_file = f"cat{year}.csv"
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(DATA_DIR + "comarq.geojson")
    # Load population data
    pop_df = pd.read_csv(DATA_DIR + "pop_gen_1_comarques.csv", delimiter=';')
    # Select relevant year population data columns
    # and rename where necessary for compatibility
    cols_dict = {
        'Unnamed: 0': "nom_comar",
        f"{year}": pop_col,
    }
    pop_df = select_and_rename_columns(pop_df, cols_dict)
    pop_df = make_cols_numeric(pop_df, [pop_col])
    pop_df.loc[pop_df['nom_comar'] == "Aran", 'nom_comar'] = "Val d'Aran"
    # Merge Dataframes obtained up until now
    df = pd.merge(com_df, pop_df)
    # Rescale
    df = rescale_percentages(df, cols=[pop_col])
    # Load catalan knowledge data
    cat_knowledge_df = pd.read_csv(DATA_DIR + cat_file, delimiter=';')
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
    df["talksnot"] = 100 - df["talks"]
    df = rescale_percentages(df, cols=['talksnot'])
    # Create Bivariate
    create_bivariate_plot_matplotlib(df, f"pop_{year}_prct", "talksnot_prct", file_name=f"PopvsTalk{year}",
                                     x_axis_name="Population", y_axis_name="Cannot Talk",
                                     title=f"Population vs Talking Ability {year}")


make_popvtalk_plot(2011)
make_popvtalk_plot(2001)


def make_PCA_plots(year):
    # Initializing som variables to be used
    form_file = f"nivell_formacio_assolit_{year}.csv"
    cat_file = f"cat{year}.csv"
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(DATA_DIR + "comarq.geojson")
    # Load population data
    niv_df = pd.read_csv(DATA_DIR + form_file, delimiter=';')
    df = pd.merge(com_df, niv_df)
    cat_knowledge_df = pd.read_csv(DATA_DIR + cat_file, delimiter=';')
    cols_dict = {
        "Unnamed: 0": "nom_comar",
    }
    cat_knowledge_df = cat_knowledge_df.rename(columns=cols_dict)
    df = pd.merge(df, cat_knowledge_df)

    # Make Columns Numeric
    if year == 2011:
        cols_list = [
            "Població de 2 anys i més", "L'entén", "El sap parlar",
            "El sap llegir", "El sap escriure", "No l'entén", "No sap llegir o escriure",
            "Total", "No sap llegir o escriure", "Sense estudis", "Educació primària",
            "ESO", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
            "Diplomatura", "Grau universitari", "Llicenciatura i doctorat"
        ]
    if year == 2001:
        cols_list = [
            "Població de 2 anys i més", "L'entén", "El sap parlar",
            "El sap llegir", "El sap escriure", "No l'entén", 'No sap llegir o escriure',
            'Sense estudis', 'Primer grau', 'ESO, EGB, Batx. elem.', 'FP grau mitjà',
            'FP grau superior', 'Batxillerat superior', 'Diplomatura',
            'Llicenciatura i doctorat', 'Total'
        ]
    df = make_cols_numeric(df, cols_list)

    # Make Language Proficiency Percentage Columns
    cols_dict = {
        "L'entén": "understands_prct",
        "El sap parlar": "speaks_prct",
        "El sap llegir": "reads_prct",
        "El sap escriure": "writes_prct",
    }
    df = make_percentages(df, cols_dict, "Població de 2 anys i més")

    # Make Education Level Percentages
    if year == 2011:
        cols_dict = {
            "Sense estudis": "no_diploma_prct",
            "Educació primària": "primary_diploma_prct",
            "ESO": "ESO_diploma_prct",
            "Batxillerat superior": "batxi_diploma_prct",
            "FP grau mitjà": "professional_middle_degree_diploma_prct",
            "FP grau superior": "professional_degree_diploma_prct",
            "Diplomatura": "old_university_degree_diploma_prct",
            "Grau universitari": "university_degree_diploma_prct",
            "Llicenciatura i doctorat": "master_and_doctor_diploma_prct"
        }
    if year == 2001:
        cols_dict = {
            "No sap llegir o escriure": "analfabetic_prct",
            "Sense estudis": "no_diploma_prct",
            "Primer grau": "primary_diploma_prct",
            "ESO, EGB, Batx. elem.": "ESO_diploma_prct",
            "Batxillerat superior": "batxi_diploma_prct",
            "FP grau mitjà": "professional_middle_degree_diploma_prct",
            "FP grau superior": "professional_degree_diploma_prct",
            "Diplomatura": "old_university_degree_diploma_prct",
            "Llicenciatura i doctorat": "master_and_doctor_diploma_prct"
        }
    df = make_percentages(df, cols_dict, "Total")

    # Filter important columns
    col_list = [
        "understands_prct", "speaks_prct", "reads_prct",
        "writes_prct", "nom_comar",
    ] + list(cols_dict.values())
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    loading_df, pca_df = do_PCA(df, 2)

    biplot(pca_df, loading_df.T, year, labels=df.index)

    # Add geometry etc.
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, pca_df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC0", "PC1"])
    create_bivariate_plot_matplotlib(df, 'PC0_prct', 'PC1_prct', file_name=f"MatplotlibBivariatePlotPCA{year}",
                                     x_axis_name="Advanced education and Catalan",
                                     y_axis_name="Basic education and Catalan",
                                     title=f"Principal Components {year}")


make_PCA_plots(2011)
make_PCA_plots(2001)


def make_eduvcat_plot(year):
    # Load population data
    df = pd.read_csv(DATA_DIR + f"nivell_formacio_assolit_{year}.csv", delimiter=';')
    # Make Columns Numeric
    if year == 2011:
        cols_list = [
            "No sap llegir o escriure", "Sense estudis", "Educació primària",
            "ESO", "Batxillerat superior", "FP grau mitjà", "FP grau superior",
            "Diplomatura", "Grau universitari", "Llicenciatura i doctorat", "Total"
        ]
    if year == 2001:
        cols_list = [
            'No sap llegir o escriure','Sense estudis', 'Primer grau',
            'ESO, EGB, Batx. elem.', 'FP grau mitjà',
            'FP grau superior', 'Batxillerat superior', 'Diplomatura',
            'Llicenciatura i doctorat', 'Total'
        ]
    df = make_cols_numeric(df, cols_list)
    # Make Education Level Percentages
    if year == 2011:
        cols_dict = {
            "Sense estudis": "no_diploma_prct",
            "Educació primària": "primary_diploma_prct",
            "ESO": "ESO_diploma_prct",
            "Batxillerat superior": "batxi_diploma_prct",
            "FP grau mitjà": "professional_middle_degree_diploma_prct",
            "FP grau superior": "professional_degree_diploma_prct",
            "Diplomatura": "old_university_degree_diploma_prct",
            "Grau universitari": "university_degree_diploma_prct",
            "Llicenciatura i doctorat": "master_and_doctor_diploma_prct"
        }
        df = make_percentages(df, cols_dict, "Total")
    if year == 2001:
        cols_dict = {
            "No sap llegir o escriure": "analfabetic_prct",
            "Sense estudis": "no_diploma_prct",
            "Primer grau": "primary_diploma_prct",
            "ESO, EGB, Batx. elem.": "ESO_diploma_prct",
            "Batxillerat superior": "batxi_diploma_prct",
            "FP grau mitjà": "professional_middle_degree_diploma_prct",
            "FP grau superior": "professional_degree_diploma_prct",
            "Diplomatura": "old_university_degree_diploma_prct",
            "Llicenciatura i doctorat": "master_and_doctor_diploma_prct"
        }
        df = make_percentages(df, cols_dict, "Total")

    # Filter important columns
    col_list = ["nom_comar"] + list(cols_dict.values())
    df = df[col_list]
    df.set_index('nom_comar', inplace=True)

    loading_df, pca_df = do_PCA(df, 1)
    pca_df.rename(columns={"PC0": "PC_Educational"}, inplace=True)

    # Catalan Knowledge
    cat_knowledge_df = pd.read_csv(DATA_DIR + f"cat{year}.csv", delimiter=';')
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
    cols_dict = {
        "L'entén": "understands_prct",
        "El sap parlar": "speaks_prct",
        "El sap llegir": "reads_prct",
        "El sap escriure": "writes_prct",
    }
    cat_knowledge_df = make_percentages(cat_knowledge_df, cols_dict, "Població de 2 anys i més")

    # Filter important columns
    col_list = [
        "nom_comar", "understands_prct", "speaks_prct",
        "reads_prct", "writes_prct"
    ]
    cat_knowledge_df = cat_knowledge_df[col_list]
    cat_knowledge_df.set_index('nom_comar', inplace=True)

    loading_df, cat_knowledge_pca_df = do_PCA(cat_knowledge_df, 1)
    cat_knowledge_pca_df.rename(columns={"PC0": "PC_Catalan"}, inplace=True)

    df = merge(cat_knowledge_pca_df, pca_df, left_index=True, right_index=True)

    # Add geometry etc.
    # Load GeoJSON for the Comarques
    com_df = gpd.read_file(DATA_DIR + "comarq.geojson")
    com_df.set_index('nom_comar', inplace=True)
    df = merge(com_df, df, left_index=True, right_index=True)
    df['nom_comar'] = df.index

    df = rescale_principal_components(df, ["PC_Educational", "PC_Catalan"])
    df["PC_No_Catalan_prct"] = 100 - df["PC_Catalan_prct"]
    create_bivariate_plot_matplotlib(df, 'PC_Educational_prct', 'PC_No_Catalan_prct',
                                     file_name=f"EduvsCat_{year}", x_axis_name="Educational Level",
                                     y_axis_name="Lack of Catalan", title=f"Education vs Catalan Level {year}")


make_eduvcat_plot(2011)
make_eduvcat_plot(2001)


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
                                     y_axis_name="Catalan Level", title="Education vs Catalan Level 2001")

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
                                     y_axis_name="Catalan Level", title="Education vs Catalan Level 2011")

    saving_dir = f"{os.path.dirname(__file__)}/../../Figures/Lucas/"

    plt.savefig(f"{saving_dir}FinalPiece.jpg", bbox_inches='tight')


final_piece()