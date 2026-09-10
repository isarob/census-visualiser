# Project modules for data calculations, configuration,
# service markers, and spatial selection.

import re

import contextily as ctx
import folium
import matplotlib.pyplot as plt
import pandas as pd

from calculations import calculate_extra_columns
from config import (
    CARTO_TILES,
    CARTO_ATTRIBUTION, HEATMAP_DIR, MAP_DIR, SA1_YEAR,
)
from services import (
    prepare_services,
    add_service_markers,
)
from spatial import (
    get_electorate,
    sa1_divisions_in_electorate,
)


def generate_html_map(
        sa1_divisions,
        sed,
        electorate,
        colour_column=None,
        popup_fields=None,
        tooltip_fields=None,
        services_df=None,
        tiles=CARTO_TILES,
        cmap="viridis",
        save_path=None
):
    """
    Generate an interactive Folium map of SA1 divisions
    within an electorate.

    Optionally displays:
        - SA1 data using a colour scale
        - SA1 popup and tooltip informationA
        - Electorate boundary
        - OSM service markers
    """

    # Determine the default output path if one was not provided.
    # Determine the default output path if one was not provided.
    if save_path is None:

        # Create the maps output directory if it does not exist.
        MAP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if isinstance(electorate, str):
            save_path = (
                    MAP_DIR
                    / f"{electorate}_nswsocialists_data_{SA1_YEAR}.html"
            )

        elif len(electorate) == 1:
            save_path = (
                    MAP_DIR
                    / f"{electorate[0]}_nswsocialists_data_{SA1_YEAR}.html"
            )

        else:
            save_path = (
                    MAP_DIR
                    / f"multi_nswsocialists_data_{SA1_YEAR}.html"
            )

    # Convert popup and tooltip field dictionaries into
    # the format expected by GeoPandas.explore().
    popup_columns = None
    popup_kwds = {}

    if popup_fields:
        popup_columns = list(
            popup_fields.keys()
        )

        popup_kwds["aliases"] = list(
            popup_fields.values()
        )

    tooltip_columns = None
    tooltip_kwds = {}

    if tooltip_fields:
        tooltip_columns = list(
            tooltip_fields.keys()
        )

        tooltip_kwds["aliases"] = list(
            tooltip_fields.values()
        )

    # Load the electorate boundary and SA1 divisions
    # belonging to the selected electorate.
    electorate_polygon = get_electorate(
        sed,
        electorate
    )

    if electorate_polygon.empty:
        return None

    electorate_mesh = sa1_divisions_in_electorate(
        sa1_divisions,
        electorate
    )

    if electorate_mesh.empty:
        return None

    # Work on a copy so the original SA1 data is not modified.
    electorate_mesh = electorate_mesh.copy()

    # Calculate additional fields used by the map.
    electorate_mesh = calculate_extra_columns(
        electorate_mesh
    )

    # Folium/Leaflet expects WGS84 latitude/longitude.
    # Use copies so the original GeoDataFrames aren't modified.
    mesh_wgs84 = electorate_mesh.to_crs(epsg=4326)
    polygon_wgs84 = electorate_polygon.to_crs(epsg=4326)

    # Compute map centre from mesh centroid (WGS84)
    center = mesh_wgs84.geometry.union_all().centroid
    center_lat = center.y
    center_lon = center.x

    # Create the map without Folium's default basemap.
    # The CARTO layer is added explicitly below.
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles=None)

    # Add the CARTO Voyager basemap.
    folium.TileLayer(
        tiles=tiles,
        attr=CARTO_ATTRIBUTION,
        name="CARTO Voyager",
        overlay=False,
        control=True,
        max_zoom=20,
    ).add_to(m)

    # Configure how GeoPandas draws the SA1 divisions
    # onto the existing Folium map.
    explore_kwargs = {
        "m": m,
        "popup": popup_columns,
        "tooltip": tooltip_columns,
        "popup_kwds": popup_kwds,
        "tooltip_kwds": tooltip_kwds,
        "style_kwds": {
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.2,
        },
    }
    # Add a colour scale when a data column was provided.
    if colour_column is not None:
        explore_kwargs.update({
            "column": colour_column,
            "cmap": cmap,
            "scheme": "Quantiles",
            "k": 5,
            "legend": False,
        })

    # Draw the SA1 divisions.
    m = electorate_mesh.explore(
        **explore_kwargs
    )

    # Draw the electorate boundary above the SA1 divisions.
    polygon_wgs84.explore(
        m=m,
        style_kwds={
            "color": "red",
            "weight": 3,
            "fill": False,
        },
        name="Electorate Boundary",
    )

    # Add OSM service markers when service data is available.
    if services_df is not None and not services_df.empty:
        # Categorise services, add display fields,
        # and calculate marker coordinates.
        services_df = prepare_services(services_df)

        # Add the prepared services to the Folium map.
        add_service_markers(
            services_df,
            m,
        )

    # Save the generated map when an output path was supplied.
    if save_path:
        m.save(save_path)

        print(
            f"Interactive map saved to: "
            f"{save_path}"
        )

    return m


def generate_heatmap(
        sa1_divisions,
        sed,
        electorate,
        highlight_field,
        save_chart=False
):
    """
    Generate a static heatmap of an electorate's SA1 divisions.

    The selected field is displayed using a colour scale
    with the electorate boundary overlaid.
    """
    electorate_polygon = get_electorate(
        sed,
        electorate
    )

    if electorate_polygon.empty:
        return None

    electorate_mesh = sa1_divisions_in_electorate(
        sa1_divisions,
        electorate
    )

    if electorate_mesh.empty:
        return None

    # Work on a copy so the original SA1 data is not modified.
    electorate_mesh = electorate_mesh.copy()

    # Calculate additional fields used by the heatmap.
    electorate_mesh = calculate_extra_columns(
        electorate_mesh
    )

    # Extract the data column and human-readable label
    # selected for the heatmap.
    highlight_column = (
        list(highlight_field.keys())[0]
    )

    display_name = (
        list(highlight_field.values())[0]
    )

    if highlight_column not in electorate_mesh.columns:
        raise ValueError(
            f"Column '{highlight_column}' "
            f"not found in electorate mesh data."
        )

    # Convert the selected field to numeric values.
    # Invalid or missing values become NaN.
    electorate_mesh[highlight_column] = (
        pd.to_numeric(
            electorate_mesh[highlight_column],
            errors="coerce"
        )
    )
    # Convert the data and boundary to Web Mercator,
    # which is the projection expected by web basemaps.
    electorate_mesh = electorate_mesh.to_crs(
        epsg=3857
    )

    electorate_polygon = (
        electorate_polygon.to_crs(
            epsg=3857
        )
    )

    fig, ax = plt.subplots(
        figsize=(12, 12)
    )
    # Plot SA1 values using a yellow-to-red colour scale.
    electorate_mesh.plot(
        column=highlight_column,
        cmap="YlOrRd",
        linewidth=0.1,
        edgecolor="white",
        legend=True,
        categorical=False,
        alpha=0.5,
        missing_kwds={
            "color": "lightgrey",
            "label": "No data",
        },
        legend_kwds={
            "label": display_name,
            "shrink": 0.8
        },
        ax=ax
    )
    # Overlay the electorate boundary.
    electorate_polygon.boundary.plot(
        ax=ax,
        color="black",
        linewidth=2
    )

    # Add the authenticated CARTO Voyager basemap.
    ctx.add_basemap(
        ax,
        source=CARTO_TILES,
        attribution=CARTO_ATTRIBUTION,
    )

    ax.set_title(
        f"{electorate} — {display_name}",
        fontsize=18,
        pad=20
    )

    ax.set_axis_off()
    ax.set_aspect("equal")

    plt.tight_layout()

    # Create filesystem-safe names for the output file.
    if save_chart:

        safe_electorate = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            str(electorate)
        ).strip("_")

        safe_field = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            display_name
        ).strip("_")

        # Create the output directory if it does not exist.
        HEATMAP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
                HEATMAP_DIR
                / f"{safe_electorate}_{safe_field}_{SA1_YEAR}.png"
        )

        # Save at high resolution for clearer output.
        fig.savefig(
            filename,
            dpi=300,
            bbox_inches="tight"
        )

        print(
            f"Heatmap saved to: {filename}"
        )



    else:

        plt.show()

    plt.close(fig)
    return None
