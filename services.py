import folium
import pandas as pd

# Maps OSM service categories to Font Awesome icons.
# Each entry contains:
#     (icon name, icon colour)

SERVICE_ICONS = {
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


def categorise_services(services_df):
    """
    Assign each OSM service to a human-readable category.

    Services are classified primarily using OSM amenity,
    shop, social_facility, healthcare, and leisure tags.

    Returns a copy of the input GeoDataFrame.
    """
    # Work on a copy so the original services GeoDataFrame
    # is not modified.
    services_df = services_df.copy()

    # Default anything that does not match a known category
    # to "Other".
    services_df["category"] = "Other"

    # Categorise services using their OSM amenity tags.
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

    # Categorise shopping centres using the OSM shop tag.
    if "shop" in services_df.columns:
        services_df.loc[
            services_df["shop"] == "mall",
            "category"
        ] = "Shopping Centres"

    # Some nursing homes are identified using the
    # dedicated social_facility tag.
    if "social_facility" in services_df.columns:
        services_df.loc[
            services_df["social_facility"]
            == "nursing_home",
            "category"
        ] = "Aged Care"

    # Categorise common OSM leisure tags as sports facilities.
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

    # Clinics can be identified using either the amenity
    # or healthcare OSM tag.
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
        clinic_mask = (clinic_mask | (services_df["healthcare"] == "clinic"))

    services_df.loc[
        clinic_mask,
        "category"
    ] = "Clinics"
    return services_df


def add_service_fields(services_df):
    """
    Add simplified, human-readable fields from OSM tags.

    Missing OSM fields are represented as empty values.
    Returns a copy of the input GeoDataFrame.
    """
    # Work on a copy so the original service data is unchanged.
    services_df = services_df.copy()

    # Use empty values when an optional OSM field is missing.
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

    # Prefer operator:type, falling back to ownership.
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
    return services_df


def add_service_coordinates(services_df):
    """
    Add latitude and longitude columns to services.

    Representative points are used so that polygons and
    other non-point geometries receive a sensible marker
    location.
    """
    services_df = services_df.copy()

    # Convert to WGS84 because Folium expects latitude/longitude.
    services_wgs84 = services_df.to_crs(
        "EPSG:4326"
    )

    # Representative points place markers inside
    # polygons and other non-point geometries.
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
    return services_df


def prepare_services(services_df):
    """
    Prepare OSM services for display on an interactive map.

    Performs:
        1. Service categorisation
        2. Human-readable OSM field creation
        3. Marker coordinate generation

    Returns a prepared copy of the GeoDataFrame.
    """

    services_df = categorise_services(services_df)
    services_df = add_service_fields(services_df)
    services_df = add_service_coordinates(services_df)

    return services_df


def add_service_markers(services_df, map_object):
    """
    Add prepared service data as markers to a Folium map.

    Each service receives an icon based on its category.
    Available OSM attributes are displayed in the popup.
    """

    # Create a marker for each service.
    for _, row in services_df.iterrows():

        icon_name, icon_colour = SERVICE_ICONS.get(
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
        # Build a popup containing the service name,
        # category, and available OSM attributes.
        popup_html = f"""
        <b>{name}</b><br>
        <b>Category:</b>
        {row.get("category", "")}<br>
        """

        for col, value in row.items():

            if col in {
                "name",
                "category",
                "latitude",
                "longitude",
                "geometry",
                "tags",
                "members"
            }:
                continue

            if pd.notna(value):
                popup_html += (
                    f"<b>{col.replace('_', ' ')}:</b> "
                    f"{value}<br>"
                )

        # Add the service marker using its category-specific icon.
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
        ).add_to(map_object)
