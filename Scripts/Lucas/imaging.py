import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.colors import rgb2hex
from generativepy.color import Color
from PIL import ImageColor
import os



def create_bivariate_plot_matplotlib(df, col1, col2, file_name):
    print(df.head())

    ### percentile bounds defining upper boundaries of color classes
    percentile_bounds = [i for i in range(1, 100)]

    ### function to convert hex color to rgb to Color object (generativepy package)
    def hex_to_Color(hexcode):
        rgb = ImageColor.getcolor(hexcode, 'RGB')
        rgb = [v / 256 for v in rgb]
        rgb = Color(*rgb)
        return rgb

    ### get corner colors
    c00 = hex_to_Color('#e8e8e8')
    c10 = hex_to_Color('#be64ac')
    c01 = hex_to_Color('#5ac8c8')
    c11 = hex_to_Color('#3b4994')

    ### now create square grid of colors, using color interpolation from generativepy package
    num_grps = len(percentile_bounds)
    c00_to_c10 = []
    c01_to_c11 = []
    colorlist = []
    for i in range(num_grps):
        c00_to_c10.append(c00.lerp(c10, 1 / (num_grps - 1) * i))
        c01_to_c11.append(c01.lerp(c11, 1 / (num_grps - 1) * i))
    for i in range(num_grps):
        for j in range(num_grps):
            colorlist.append(c00_to_c10[i].lerp(c01_to_c11[i], 1 / (num_grps - 1) * j))

    ### convert back to hex color
    colorlist = [rgb2hex([c.r, c.g, c.b]) for c in colorlist]

    alpha = 0.85
    dpi = 300

    ### function to get bivariate color given two percentiles
    def get_bivariate_choropleth_color(p1, p2):
        color = [0.8, 0.8, 0.8, 1]
        print(p1, p2)
        if p1 >= 0 and p2 >= 0:
            count = 0
            stop = False
            for percentile_bound_p1 in percentile_bounds:
                for percentile_bound_p2 in percentile_bounds:
                    if (not stop) and (p1 <= percentile_bound_p1):
                        if (not stop) and (p2 <= percentile_bound_p2):
                            color = colorlist[count]
                            stop = True
                    count += 1
        return color

    ### plot map based on bivariate choropleth
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))

    df['color_bivariate'] = [get_bivariate_choropleth_color(p1, p2) for p1, p2 in
                              zip(df[col1].values, df[col2].values)]
    print(df['color_bivariate'])
    df.plot(ax=ax, color=df['color_bivariate'], alpha=alpha, legend=False)
    ax.set_xticks([])
    ax.set_yticks([])

    ### now create inset legend
    ax = ax.inset_axes([0.6, 0.1, 0.25, 0.25])
    ax.set_aspect('equal', adjustable='box')
    count = 0
    xticks = [0]
    yticks = [0]
    for i, percentile_bound_p1 in enumerate(percentile_bounds):
        for j, percentile_bound_p2 in enumerate(percentile_bounds):
            percentileboxes = [Rectangle((i, j), 1, 1)]
            pc = PatchCollection(percentileboxes, facecolor=colorlist[count], alpha=alpha)
            count += 1
            ax.add_collection(pc)
            if i == 0:
                yticks.append(percentile_bound_p2)
        xticks.append(percentile_bound_p1)

    _ = ax.set_xlim([0, len(percentile_bounds)])
    _ = ax.set_ylim([0, len(percentile_bounds)])
    _ = ax.set_xticks(list(range(len(percentile_bounds) + 1)), xticks)
    _ = ax.set_xlabel('Population percentile')
    _ = ax.set_yticks(list(range(len(percentile_bounds) + 1)), yticks)
    _ = ax.set_ylabel('Speaking Ability percentile')

    saving_dir = f"{os.path.dirname(__file__)}../../../Figures/Lucas/"

    plt.savefig(f"{saving_dir}{file_name}.jpg", dpi=dpi, bbox_inches='tight')


def create_bivariate_plot_plotly(gdf, col_1, col_2):
    # Variable Normalization
    gdf[col_1] = (gdf[col_1] - gdf[col_1].min()) / (gdf[col_1].max() - gdf[col_1].min())
    gdf[col_2] = (gdf[col_2] - gdf[col_2].min()) / (
            gdf[col_2].max() - gdf[col_2].min())

    def bivariate_color_plotly(val, parlar):
        """Create a bivariate color using a linear
        interpolation of two normalized variables."""
        r = int((1 - val) * 255)
        g = int((1 - parlar) * 255)
        b = 255
        return f"rgb({r},{g},{b})"

    # Apply the bivariate color function
    gdf['bivariate_color'] = gdf.apply(lambda row: bivariate_color_plotly(row[col_1], row[col_2]), axis=1)

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

    # Show the map with the legend
    fig.show()