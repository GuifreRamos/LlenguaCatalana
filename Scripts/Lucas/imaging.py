import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.colors import rgb2hex
from generativepy.color import Color
from PIL import ImageColor
import os

def create_bivariate_plot_matplotlib_final(fig, df, col1, col2, file_name, x_axis_name, y_axis_name, title):
    ### percentile bounds defining upper boundaries of color classes
    percentile_bounds = [i*20+ 0.01 for i in range(1, 6)]

    ### function to convert hex color to rgb to Color object (generativepy package)
    def hex_to_Color(hexcode):
        rgb = ImageColor.getcolor(hexcode, 'RGB')
        rgb = [v / 256 for v in rgb]
        rgb = Color(*rgb)
        return rgb

    ### get corner colors
    c00 = hex_to_Color('#f3f3f3')
    c10 = hex_to_Color('#e1a800')
    c01 = hex_to_Color('#8997c4')
    c11 = hex_to_Color('#000000')

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
    ax = fig.subplots(1, 1)
    ax.title.set_text(title)

    df['color_bivariate'] = [get_bivariate_choropleth_color(p1, p2) for p1, p2 in
                              zip(df[col1].values, df[col2].values)]
    print(df['color_bivariate'])
    df.plot(ax=ax, color=df['color_bivariate'], alpha=alpha, legend=False)
    ax.set_xticks([])
    ax.set_yticks([])

    ### now create inset legend
    ax = ax.inset_axes([0.6, 0.1, 0.2, 0.2])
    ax.set_aspect('equal', adjustable='box')
    count = 0
    xticks = [0]
    yticks = [0]
    for i, percentile_bound_p1 in enumerate(percentile_bounds):
        for j, percentile_bound_p2 in enumerate(percentile_bounds):
            percentileboxes = [Rectangle((i, j), 1, 1)]
            pc = PatchCollection(percentileboxes, facecolor=colorlist[count], alpha=alpha, zorder=1)
            count += 1
            ax.add_collection(pc)
            if i == 0:
                yticks.append(percentile_bound_p2)
        xticks.append(percentile_bound_p1)

    _ = ax.set_xlim([0, len(percentile_bounds)])
    _ = ax.set_ylim([0, len(percentile_bounds)])
    _ = ax.set_xlabel(x_axis_name)
    _ = ax.set_ylabel(y_axis_name)
    _ = ax.set_xticks([])
    _ = ax.set_yticks([])

    # Add scatter points to the inset legend
    # Add scatter on a separate axis that is perfectly aligned
    scatter_ax = ax.inset_axes([0, 0, 1, 1], zorder=10)
    scatter_ax.set_xlim(0, 100)
    scatter_ax.set_ylim(0, 100)
    scatter_ax.set_xticks([])
    scatter_ax.set_yticks([])

    # Plot the scatter on the separate layer
    print(df[col1].values, df[col2].values)
    scatter_ax.scatter(df[col1].values, df[col2].values, color='#d85047', marker='x', s=10, alpha=0.9)

    # Make sure scatter_ax does not interfere with the original axis
    scatter_ax.set_facecolor((1, 1, 1, 0))  # Transparent background



def create_bivariate_plot_matplotlib(df, col1, col2, file_name, x_axis_name, y_axis_name, title):
    ### percentile bounds defining upper boundaries of color classes
    percentile_bounds = [i*20+ 0.01 for i in range(1, 6)]

    ### function to convert hex color to rgb to Color object (generativepy package)
    def hex_to_Color(hexcode):
        rgb = ImageColor.getcolor(hexcode, 'RGB')
        rgb = [v / 256 for v in rgb]
        rgb = Color(*rgb)
        return rgb

    ### get corner colors
    c00 = hex_to_Color('#f3f3f3')
    c10 = hex_to_Color('#e1a800')
    c01 = hex_to_Color('#8997c4')
    c11 = hex_to_Color('#000000')

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
    plt.title(title)

    df['color_bivariate'] = [get_bivariate_choropleth_color(p1, p2) for p1, p2 in
                              zip(df[col1].values, df[col2].values)]
    print(df['color_bivariate'])
    df.plot(ax=ax, color=df['color_bivariate'], alpha=alpha, legend=False)
    ax.set_xticks([])
    ax.set_yticks([])

    ### now create inset legend
    ax = ax.inset_axes([0.6, 0.1, 0.2, 0.2])
    ax.set_aspect('equal', adjustable='box')
    count = 0
    xticks = [0]
    yticks = [0]
    for i, percentile_bound_p1 in enumerate(percentile_bounds):
        for j, percentile_bound_p2 in enumerate(percentile_bounds):
            percentileboxes = [Rectangle((i, j), 1, 1)]
            pc = PatchCollection(percentileboxes, facecolor=colorlist[count], alpha=alpha, zorder=1)
            count += 1
            ax.add_collection(pc)
            if i == 0:
                yticks.append(percentile_bound_p2)
        xticks.append(percentile_bound_p1)

    _ = ax.set_xlim([0, len(percentile_bounds)])
    _ = ax.set_ylim([0, len(percentile_bounds)])
    _ = ax.set_xlabel(x_axis_name)
    _ = ax.set_ylabel(y_axis_name)
    _ = ax.set_xticks([])
    _ = ax.set_yticks([])

    # Add scatter points to the inset legend
    # Add scatter on a separate axis that is perfectly aligned
    scatter_ax = ax.inset_axes([0, 0, 1, 1], zorder=10)
    scatter_ax.set_xlim(0, 100)
    scatter_ax.set_ylim(0, 100)
    scatter_ax.set_xticks([])
    scatter_ax.set_yticks([])

    # Plot the scatter on the separate layer
    print(df[col1].values, df[col2].values)
    scatter_ax.scatter(df[col1].values, df[col2].values, color='#d85047', marker='x', s=10, alpha=0.9)

    # Make sure scatter_ax does not interfere with the original axis
    scatter_ax.set_facecolor((1, 1, 1, 0))  # Transparent background

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

def biplot(pc_df, loadings, labels=None):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot the scores for localities
    ax.scatter(pc_df['PC1'], pc_df['PC2'], alpha=0.5, c='grey', label='Localities')

    # If you want to label the localities:
    if labels is not None:
        for i, txt in enumerate(labels):
            ax.annotate(txt, (pc_df['PC1'][i], pc_df['PC2'][i]), fontsize=9, alpha=0.7)

    # Plot the loadings (original variable vectors)
    print(loadings)
    for i in range(loadings.shape[0]):
        ax.arrow(0, 0, loadings['PC1'][i], loadings['PC2'][i],
                 color='red', alpha=0.8, head_width=0.03)
        plt.text(loadings['PC1'][i] * 1.15, loadings['PC2'][i] * 1.15,
                 loadings.index[i], color='red', ha='center', va='center', fontsize=10)

    # Formatting
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.axhline(y=0, color='grey', linestyle='--', linewidth=0.7)
    ax.axvline(x=0, color='grey', linestyle='--', linewidth=0.7)
    plt.title('Biplot of PCA')
    plt.grid()
    plt.show()

