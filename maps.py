# Project modules for data calculations, configuration,
# service markers, and spatial selection.

import re
import branca
from branca.element import Element

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
        popup_fields=None,
        tooltip_fields=None,
        heatmap_fields=None,
        services_df=None,
        tiles=CARTO_TILES,
        cmap="viridis",          
        save_path=None
):
    # Determine output path.
    if save_path is None:

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

    # Load electorate boundary.
    electorate_polygon = get_electorate(
        sed,
        electorate
    )

    if electorate_polygon.empty:
        return None

    # Load SA1 divisions.
    electorate_mesh = sa1_divisions_in_electorate(
        sa1_divisions,
        electorate
    )

    if electorate_mesh.empty:
        return None

    electorate_mesh = electorate_mesh.copy()

    electorate_mesh = calculate_extra_columns(
        electorate_mesh
    )

    # Convert to WGS84 for Folium.
    mesh_wgs84 = electorate_mesh.to_crs(
        epsg=4326
    )
    print("Optimisation: ")
    print(len(mesh_wgs84.columns))
    print(f"original columns: {len(mesh_wgs84.columns)}")
    print(mesh_wgs84.columns.tolist())

    needed_columns = (
    ["geometry"]
    + list(heatmap_fields.keys())
    + list(popup_fields.keys())
    + list(tooltip_fields.keys())
)

    unique_list = list(dict.fromkeys(needed_columns))
 
    mesh_wgs84 = mesh_wgs84[unique_list]
    print(mesh_wgs84.columns[mesh_wgs84.columns.duplicated()])
    print(f"trimmed columns: {len(mesh_wgs84.columns)}")
    print(mesh_wgs84.columns.tolist())
    
    polygon_wgs84 = electorate_polygon.to_crs(
        epsg=4326
    )

    # Calculate map centre.
    center = (
        mesh_wgs84.geometry
        .union_all()
        .centroid
    )

    center_lat = center.y
    center_lon = center.x

    # Create map.
    m = folium.Map(
        location=[
            center_lat,
            center_lon
        ],
        zoom_start=11,
        tiles=None
    )

    # Add basemap.
    folium.TileLayer(
        tiles=tiles,
        attr=CARTO_ATTRIBUTION,
        name="CARTO Voyager",
        overlay=False,
        control=True,
        max_zoom=20,
    ).add_to(m)

    # Build popup HTML.
    if popup_fields:

        popup_html = []

        for _, row in mesh_wgs84.iterrows():

            html = ""

            for col, alias in popup_fields.items():

                if col not in row.index:
                    continue

                value = row[col]

                if pd.notna(value):

                    html += (
                        f"<b>{alias}:</b> "
                        f"{value}<br>"
                    )

            popup_html.append(html)

        mesh_wgs84["_popup_html"] = popup_html




    # ------------------------------------------------------------------
    # Heatmap layers
    # ------------------------------------------------------------------

    legend_switches = ""

    if heatmap_fields:

        first_field = next(
            iter(heatmap_fields.keys())
        )
        
        total = 0
        for field, label in heatmap_fields.items():

            total += 1
            print(f"processing {label} layer [{total} / {len(heatmap_fields)}]")
            if field not in mesh_wgs84.columns:
                continue

            mesh_wgs84[field] = pd.to_numeric(
                mesh_wgs84[field],
                errors="coerce"
            )

            valid_values = (
                mesh_wgs84[field]
                .dropna()
            )

            if valid_values.empty:
                continue

            vmin = valid_values.min()
            vmax = valid_values.max()

            if vmin == vmax:
                vmax = vmin + 1

            legend_name = (
                    f"legend_{field}"
                    .replace(" ", "_")
                    .replace("%", "pct")
            )

            legend_html = f"""
            <div id="{legend_name}"
                 class="heatmap-legend"
                 style="
                     display:{'block' if field == first_field else 'none'};
                     position: fixed;
                     bottom: 50px;
                     left: 50px;
                     z-index: 9999;
                     background-color: white;
                     border: 2px solid grey;
                     padding: 10px;
                     font-size: 14px;
                     min-width: 200px;
                 ">
                <b>{label}</b><br>
                Min: {vmin:,.2f}<br>
                Max: {vmax:,.2f}
            </div>
            """

            colormap = (
                branca.colormap.linear.YlOrRd_09
                .scale(
                    vmin,
                    vmax
                )
            )

            colormap.caption = label

            layer = folium.FeatureGroup(
                name=label,
                overlay=True,
                control=True,
                show=(field == first_field)
            )

            def style_function(
                    feature,
                    field=field,
                    colormap=colormap,
                    vmin=vmin,
                    vmax=vmax
            ):

                value = feature["properties"].get(field)

                try:
                    value = float(value)

                    fill_color = colormap(value)

                    alpha = (value - vmin) / (vmax - vmin)

                    alpha = max(
                        0.1,
                        min(alpha, 1.0)
                    )

                except (
                        TypeError,
                        ValueError
                ):
                    fill_color = "#d3d3d3"
                    alpha = 0.1

                return {
                    "fillColor": fill_color,
                    "fillOpacity": alpha,
                    "color": "black",
                    "weight": 1,
                }

            geojson = folium.GeoJson(
                mesh_wgs84,
                name=label,
                style_function=style_function,
                highlight_function=lambda x: {
                    "weight": 3,
                    "fillOpacity": 0.8,
                },
            )

            if popup_fields:

                folium.GeoJsonPopup(
                    fields=["_popup_html"],
                    aliases=[""],
                    labels=False,
                    parse_html=True,
                ).add_to(
                    geojson
                )

            if tooltip_fields:

                for feature in geojson.data["features"]:

                    properties = feature["properties"]

                    tooltip_html = """
                    <b>Demographics</b><br>
                    """

                    for column, alias in tooltip_fields.items():

                        tooltip_html += (
                                f"{alias}: {properties.get(column, '')}<br>"
                                )

                    tooltip_html += """
                    <br>
                    <b>Heatmap</b><br>
                    """

                    for column, alias in heatmap_fields.items():
                        if column in tooltip_fields.keys():
                            continue

                        tooltip_html += (
                                f"{alias}: {properties.get(column, '')}<br>"
                                )
                    feature["properties"]["tooltip_html"] = tooltip_html

                folium.GeoJsonTooltip(
                        fields=["tooltip_html"],
                        aliases=[""],
                        labels=False,
                        localize=False,
                        sticky=False,
                        ).add_to(
                                geojson
                                )

                #iterate tooltip_columns and tooltip_aliases to populate this

            geojson.add_to(
                layer
            )

            m.get_root().html.add_child(
                    folium.Element(legend_html)
                    )

            layer.add_to(
                m
            )

            legend_name = (
                f"legend_{field}"
                .replace(" ", "_")
                .replace("%", "pct")
            )

            legend_switches += f"""
            if (e.name === "{label}") {{

                document
                    .querySelectorAll(".heatmap-legend")
                    .forEach(
                        el => el.style.display = "none"
                    );

                document
                    .getElementById("{legend_name}")
                    .style.display = "block";
            }}
            """

    # ------------------------------------------------------------------
    # Electorate boundary
    # ------------------------------------------------------------------

    folium.GeoJson(
        polygon_wgs84,
        name="Electorate Boundary",
        style_function=lambda feature: {
            "color": "red",
            "weight": 3,
            "fillOpacity": 0,
        },
    ).add_to(
        m
    )

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------
    if (
            services_df is not None
            and not services_df.empty
    ):

        print("adding services")
        services_df = prepare_services(
            services_df
        )

        add_service_markers(
            services_df,
            m,
        )

    # ------------------------------------------------------------------
    # Layer selector
    # ------------------------------------------------------------------

    folium.LayerControl(
        collapsed=False
    ).add_to(
        m
    )

    map_name = m.get_name()

    m.get_root().script.add_child(
        Element(
            f"""
    setTimeout(function() {{

        {map_name}.on(
            'overlayadd',
            function(e) {{

                {legend_switches}

            }}
        );

    }}, 1000);
    """
        )
    )


    # ------------------------------------------------------------------
    # Save map
    # ------------------------------------------------------------------
    print("saving map")
    if save_path:

        m.save(
            str(save_path)
        )

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

def generate_folium_heatmap(
        sa1_divisions,
        sed,
        electorate,
        highlight_field,
        save_chart=False
):
    """
    Generate an interactive Folium heatmap for an electorate.

    highlight_field example:
        {
            "G02_Median_age_persons": "Median Age"
        }
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

    electorate_mesh = electorate_mesh.copy()

    electorate_mesh = calculate_extra_columns(
        electorate_mesh
    )

    highlight_column = (
        list(highlight_field.keys())[0]
    )

    display_name = (
        list(highlight_field.values())[0]
    )

    if highlight_column not in electorate_mesh.columns:
        raise ValueError(
            f"Column '{highlight_column}' not found."
        )

    electorate_mesh[highlight_column] = pd.to_numeric(
        electorate_mesh[highlight_column],
        errors="coerce"
    )

    # Folium expects WGS84
    electorate_mesh = electorate_mesh.to_crs(
        epsg=4326
    )

    electorate_polygon = electorate_polygon.to_crs(
        epsg=4326
    )

    bounds = electorate_polygon.total_bounds

    center_lat = (
        bounds[1] + bounds[3]
    ) / 2

    center_lon = (
        bounds[0] + bounds[2]
    ) / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="CartoDB positron"
    )

    choropleth = folium.Choropleth(
        geo_data=electorate_mesh,
        data=electorate_mesh,
        columns=[
            electorate_mesh.index,
            highlight_column
        ],
        key_on="feature.id",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="lightgray",
        legend_name=display_name,
        highlight=True,
    ).add_to(m)

    tooltip_fields = [
        highlight_column
    ]

    tooltip_aliases = [
        display_name
    ]

    if "SA1_CODE21" in electorate_mesh.columns:
        tooltip_fields.insert(
            0,
            "SA1_CODE21"
        )

        tooltip_aliases.insert(
            0,
            "SA1"
        )

    folium.GeoJson(
        electorate_mesh,
        style_function=lambda feature: {
            "fillOpacity": 0,
            "color": "transparent",
            "weight": 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
        )
    ).add_to(m)

    folium.GeoJson(
        electorate_polygon,
        style_function=lambda feature: {
            "fillColor": "none",
            "color": "black",
            "weight": 3,
            "fillOpacity": 0
        },
        name="Electorate Boundary"
    ).add_to(m)

    m.fit_bounds([
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]]
    ])

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

        HEATMAP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            HEATMAP_DIR
            / f"{safe_electorate}_{safe_field}_{SA1_YEAR}.html"
        )

        m.save(str(filename))

        print(
            f"Heatmap saved to: {filename}"
        )

    else:

        tmp_file = Path(
            tempfile.gettempdir()
        ) / "heatmap.html"

        m.save(str(tmp_file))

        webbrowser.open(
            f"file://{tmp_file}"
        )

    return None
