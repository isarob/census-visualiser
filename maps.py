import os
import re

import contextily as ctx
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from calculations import calculate_extra_columns
from config import CARTO_API_KEY
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
        tiles=None,
        cmap="viridis",
        save_path=None
):
    if tiles is None:
        tiles = (
            "https://basemaps.cartocdn.com/"
            "rastertiles/positron/"
            "{z}/{x}/{y}.png"
            f"?key={CARTO_API_KEY}"
        )

    if save_path is None:

        if isinstance(electorate, str):
            save_path = (
                f"{electorate}_nswsocialists_data_2027.html"
            )

        elif len(electorate) == 1:
            save_path = (
                f"{electorate[0]}_nswsocialists_data_2027.html"
            )

        else:
            save_path = (
                "multi_nswsocialists_data_2027.html"
            )

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

    """
    Interactive map of sa1 divisions within an electorate.
    Click a sa1 division to view its attributes.
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

    explore_kwargs = {
        "popup": popup_columns,
        "tooltip": tooltip_columns,
        "popup_kwds": popup_kwds,
        "tooltip_kwds": tooltip_kwds,
        "tiles": tiles,
        "attr": "© OpenStreetMap contributors © CARTO",
        "style_kwds": {
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.2,
        }
    }

    if colour_column is not None:

        explore_kwargs.update({
            "column": colour_column,
            "cmap": cmap,
            "scheme": "Quantiles",
            "k": 5,
            "legend": False,
        })

    m = electorate_mesh.explore(
        **explore_kwargs
    )

    electorate_polygon.explore(
        m=m,
        style_kwds={
            "color": "red",
            "weight": 3,
            "fill": False
        },
        name="Electorate Boundary"
    )

    if services_df is not None and not services_df.empty:

        # Work on a copy so the original services GeoDataFrame
        # is not modified.
        services_df = services_df.copy()

        # --------------------------------------------------
        # Categorise services
        # --------------------------------------------------

        services_df["category"] = "Other"

        if "amenity" in services_df.columns:

            services_df.loc[
                services_df["amenity"] == "hospital",
                "category"
            ] = "Hospitals"

            services_df.loc[
                services_df["amenity"] == "school",
                "category"
            ] = "Schools"

            services_df.loc[
                services_df["amenity"].isin(
                    [
                        "childcare",
                        "kindergarten"
                    ]
                ),
                "category"
            ] = "Childcare"

            services_df.loc[
                services_df["amenity"]
                == "community_centre",
                "category"
            ] = "Community Centres"

            services_df.loc[
                services_df["amenity"]
                == "place_of_worship",
                "category"
            ] = "Churches"

            services_df.loc[
                services_df["amenity"].isin(
                    [
                        "nursing_home",
                        "social_facility"
                    ]
                ),
                "category"
            ] = "Aged Care"

        if "shop" in services_df.columns:

            services_df.loc[
                services_df["shop"] == "mall",
                "category"
            ] = "Shopping Centres"

        if "social_facility" in services_df.columns:

            services_df.loc[
                services_df["social_facility"]
                == "nursing_home",
                "category"
            ] = "Aged Care"

        if "leisure" in services_df.columns:

            services_df.loc[
                services_df["leisure"].isin(
                    [
                        "sports_centre",
                        "stadium",
                        "pitch",
                        "track",
                        "fitness_centre",
                        "sports_hall",
                        "swimming_pool",
                        "golf_course"
                    ]
                ),
                "category"
            ] = "Sports Facilities"

        if "amenity" in services_df.columns:

            clinic_mask = (
                services_df["amenity"]
                == "clinic"
            )

        else:

            clinic_mask = pd.Series(
                False,
                index=services_df.index
            )

        if "healthcare" in services_df.columns:

            clinic_mask = (
                clinic_mask
                |
                (
                    services_df["healthcare"]
                    == "clinic"
                )
            )

        services_df.loc[
            clinic_mask,
            "category"
        ] = "Clinics"

        # --------------------------------------------------
        # Optional OSM fields
        # --------------------------------------------------

        empty_series = pd.Series(
            pd.NA,
            index=services_df.index,
            dtype="object"
        )

        operator_type = services_df.get(
            "operator:type",
            empty_series
        )

        ownership = services_df.get(
            "ownership",
            empty_series
        )

        services_df["Ownership"] = (
            operator_type
            .fillna(ownership)
        )

        services_df["Beds"] = services_df.get(
            "beds",
            empty_series
        )

        services_df["Emergency"] = services_df.get(
            "emergency",
            empty_series
        )

        services_df["Hospital_Type"] = services_df.get(
            "hospital:type",
            empty_series
        )

        school_type = services_df.get(
            "school:type",
            empty_series
        )

        services_df["School_Type"] = (
            school_type
            .fillna(operator_type)
        )

        services_df["Enrolment"] = services_df.get(
            "school:enrolment",
            empty_series
        )

        services_df["Grades"] = services_df.get(
            "grades",
            empty_series
        )

        services_df["Selective"] = services_df.get(
            "school:selective",
            empty_series
        )

        services_df["Religion"] = services_df.get(
            "religion",
            empty_series
        )

        services_df["Specialty"] = services_df.get(
            "healthcare:speciality",
            empty_series
        )

        services_df["Bulk_Billing"] = services_df.get(
            "bulkbilling",
            empty_series
        )

        # --------------------------------------------------
        # Get marker coordinates
        # --------------------------------------------------

        services_wgs84 = services_df.to_crs(
            "EPSG:4326"
        )

        representative_points = (
            services_wgs84.geometry
            .representative_point()
        )

        services_df["latitude"] = (
            representative_points.y
        )

        services_df["longitude"] = (
            representative_points.x
        )

        # --------------------------------------------------
        # Marker icons
        # --------------------------------------------------

        icon_lookup = {
            "Hospitals": (
                "plus-circle",
                "red"
            ),

            "Schools": (
                "graduation-cap",
                "blue"
            ),

            "Childcare": (
                "child",
                "green"
            ),

            "Community Centres": (
                "users",
                "purple"
            ),

            "Shopping Centres": (
                "shopping-cart",
                "orange"
            ),

            "Clinics": (
                "stethoscope",
                "darkred"
            ),

            "Churches": (
                "church",
                "cadetblue"
            ),

            "Aged Care": (
                "home",
                "pink"
            ),

            "Sports Facilities": (
                "futbol",
                "darkgreen"
            ),

            "Other": (
                "info-circle",
                "gray"
            ),
        }

        # --------------------------------------------------
        # Create markers
        # --------------------------------------------------

        for _, row in services_df.iterrows():

            icon_name, icon_colour = icon_lookup.get(
                row["category"],
                (
                    "info-sign",
                    "gray"
                )
            )

            name = row.get(
                "name",
                ""
            )

            popup_html = f"""
            <b>{name}</b><br>
            <b>Category:</b>
            {row.get("category", "")}<br>
            """

            for col, value in row.items():

                if col in [
                    "name",
                    "category",
                    "latitude",
                    "longitude",
                    "geometry",
                    "tags",
                    "members"
                ]:
                    continue

                if pd.notna(value):

                    popup_html += (
                        f"<b>{col.replace('_', ' ')}:</b> "
                        f"{value}<br>"
                    )

            folium.Marker(
                location=[
                    row["latitude"],
                    row["longitude"]
                ],
                popup=folium.Popup(
                    popup_html,
                    max_width=400
                ),
                tooltip=name,
                icon=folium.DivIcon(
                    html=f"""
                    <i class="fa fa-{icon_name}"
                       style="
                           color:{icon_colour};
                           font-size:16px;
                       ">
                    </i>
                    """
                )
            ).add_to(m)

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
        saveChart=False
):
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
            f"Column '{highlight_column}' "
            f"not found in electorate mesh data."
        )

    electorate_mesh[highlight_column] = (
        pd.to_numeric(
            electorate_mesh[highlight_column],
            errors="coerce"
        )
    )

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

    electorate_polygon.boundary.plot(
        ax=ax,
        color="black",
        linewidth=2
    )

    ctx.add_basemap(
        ax,
        source=(
            "https://basemaps.cartocdn.com/rastertiles/"
            "voyager/{z}/{x}/{y}.png"
            f"?key={CARTO_API_KEY}"
        ),
        attribution=False
    )

    ax.set_title(
        f"{electorate} — {display_name}",
        fontsize=18,
        pad=20
    )

    ax.set_axis_off()
    ax.set_aspect("equal")

    plt.tight_layout()

    if saveChart:

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

        os.makedirs(
            "Heatmaps",
            exist_ok=True
        )

        filename = (
            f"Heatmaps/"
            f"{safe_electorate}_"
            f"{safe_field}_"
            f"2021.png"
        )

        fig.savefig(
            filename,
            dpi=300,
            bbox_inches="tight"
        )

        print(
            f"Heatmap saved to: {filename}"
        )

        plt.close(fig)

    else:

        plt.show()

        plt.close(fig)