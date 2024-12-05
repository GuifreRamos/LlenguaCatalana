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


def make_popvtalk_plot(year, final=False, fig=None):
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
    if not final:
        create_bivariate_plot_matplotlib(df, f"pop_{year}_prct", "talksnot_prct", file_name=f"PopvsTalk{year}",
                                         x_axis_name="Population", y_axis_name="Cannot Talk",
                                         title=f"Population vs Talking Ability {year}")
    else:
        create_bivariate_plot_matplotlib_final(fig, df, f"pop_{year}_prct", "talksnot_prct",
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


def make_eduvcat_plot(year, final=False, fig=None):
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
    if not final:
        create_bivariate_plot_matplotlib(df, 'PC_Educational_prct', 'PC_No_Catalan_prct',
                                         file_name=f"EduvsCat_{year}", x_axis_name="Educational Level",
                                         y_axis_name="Lack of Catalan",
                                         title=f"Education vs Catalan Level {year}")
    else:
        create_bivariate_plot_matplotlib_final(fig, df, 'PC_Educational_prct', 'PC_No_Catalan_prct',
                                               x_axis_name="Educational Level", y_axis_name="Catalan Level",
                                               title=f"Education vs Catalan Level {year}")

make_eduvcat_plot(2011)
make_eduvcat_plot(2001)


def final_piece():
    fig = plt.figure(constrained_layout=True, figsize=(10, 10))
    subplots = fig.subfigures(1, 2)

    fig1 = subplots[0]
    fig2 = subplots[1]

    # Add the four Plots
    make_popvtalk_plot(2001, final=True, fig=fig1)
    make_popvtalk_plot(2011, final=True, fig=fig2)

    # Save the Plot
    saving_dir = f"{os.path.dirname(__file__)}/../../Figures/Lucas/"
    plt.savefig(f"{saving_dir}FinalPiece.jpg", bbox_inches='tight')


final_piece()