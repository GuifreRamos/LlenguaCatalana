import pandas as pd

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


plt.bar(df_2015_estudis_baixos['comarca o Aran'], df_2015_estudis_baixos['valor'])
plt.xticks(rotation='vertical')
plt.show()

data_dir = "Dades/"
vegueries = gpd.read_file(data_dir + "divisions-administratives-v2r1-vegueries-250000-20240705.json")
vegueries.plot()
plt.show()

comarques = gpd.read_file(data_dir + "divisions-administratives-v2r1-comarques-250000-20240705.json")
comarques.plot()
print(comarques.columns)
plt.show()

municipis = gpd.read_file(data_dir + "divisions-administratives-v2r1-municipis-250000-20240705.json")
municipis.plot()
print(municipis.columns)
plt.show()

data_dir = "dades_david/"
comarques = gpd.read_file(data_dir + "comarq.geojson")

print(comarques.columns)


df_2015_estudis_baixos = df_2015_estudis_baixos.rename(columns={"comarca o Aran": "nom_comar"})
print("Here are the heads ...")
print(df_2015_estudis_baixos.columns)
print(comarques.columns)

comarques_new = pd.merge(comarques, df_2015_estudis_baixos)
print(comarques_new.columns)


columns_to_keep = ['nom_comar', 'valor', 'geometry']
comarques_new = comarques_new[columns_to_keep]
print(comarques_new.columns)
df_catalan_knowledge = df_2015_estudis_baixos.rename(columns={'valor': "percentage low studies"})
comarques_new.plot(column='valor', legend=True)
plt.show()

df_catalan_knowledge = pd.read_csv(data_dir + "cat2011.csv", delimiter=';')
df_catalan_knowledge = df_catalan_knowledge.rename(columns={'Unnamed: 0': "nom_comar"})
comarques_new = pd.merge(comarques_new, df_catalan_knowledge)
columns_to_keep = ['nom_comar', 'valor', '% sap parlar', 'geometry']
comarques_new = comarques_new[columns_to_keep]
print(comarques_new.columns)


gdf = comarques_new

gdf['% sap parlar'] = gdf['% sap parlar'].apply(lambda x: x.replace(',', '.'))
gdf['% sap parlar'] = pd.to_numeric(gdf['% sap parlar'], errors='coerce')
# Normalize the two variables to scale 0-1 for bivariate mapping
gdf['valor_norm'] = (gdf['valor'] - gdf['valor'].min()) / (gdf['valor'].max() - gdf['valor'].min())
gdf['parlar_norm'] = (gdf['% sap parlar'] - gdf['% sap parlar'].min()) / (gdf['% sap parlar'].max() - gdf['% sap parlar'].min())


# Create a grid of colors (2D colormap) for the bivariate map
# Example: Combining two gradients (one for each variable)
def bivariate_color(val, parlar):
    """Create a bivariate color using a linear interpolation of two normalized variables."""
    r = int(val * 255)  # Red channel based on `valor`
    g = int(parlar * 255)  # Green channel based on `% sap parlar`
    b = 0
    return f"rgb({r},{g},{b})"


# Apply the bivariate color function
gdf['bivariate_color'] = gdf.apply(lambda row: bivariate_color(row['valor_norm'], row['parlar_norm']), axis=1)

# Convert GeoDataFrame to GeoJSON
gdf_json = gdf.__geo_interface__

# Create a choropleth map with Plotly using the bivariate color mapping
fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf_json,
    locations=gdf.index,  # Match on index
    color='bivariate_color',  # Custom bivariate color mapping
    mapbox_style="carto-positron",
    center={"lat": 41.3851, "lon": 2.1734},  # Adjust center (example: Barcelona)
    zoom=8,
    title="Bivariate Choropleth Map"
)

# Remove the default color scale
fig.update_traces(marker=dict(opacity=1))

# Create a bivariate legend using matplotlib
figsize = 3
x = np.linspace(0, 1, 100)
y = np.linspace(0, 1, 100)
x, y = np.meshgrid(x, y)
colors = np.zeros((100, 100, 3))
colors[..., 0] = x  # Red increases with valor
colors[..., 1] = y  # Green increases with parlar
colors[..., 2] = 0  # Blue is not used

fig_legend, ax = plt.subplots(figsize=(figsize, figsize))
ax.imshow(colors, origin="lower", extent=[0, 1, 0, 1])
ax.set_xlabel("Valor (Red)", fontsize=10)
ax.set_ylabel("% Sap Parlar (Green)", fontsize=10)
ax.set_title("Bivariate Legend", fontsize=12)
plt.tight_layout()

# Save the legend as an image in memory
buf = io.BytesIO()
plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
buf.seek(0)
plt.close(fig_legend)

# Overlay the legend as an image in Plotly
image = Image.open(buf)
fig.add_layout_image(
    dict(
        source=image,
        xref="paper", yref="paper",
        x=1.02, y=0.5,  # Adjust position (to the right of the map)
        sizex=0.3, sizey=0.3,  # Adjust size
        xanchor="left", yanchor="middle",
        layer="above"
    )
)

# Show the map with the legend
fig.show()