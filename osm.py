import ast

import geopandas as gpd
import pandas as pd
from pyrosm import OSM

from config import POI_FILTER
from spatial import find_sed_name_column


def load_osm_pois(
        pbf_path,
        electorate_area=None
):
    """
    Load OSM points of interest for the selected electorates.
    Each electorate is processed separately to reduce memory usage.
    """

    if electorate_area is None or electorate_area.empty:
        raise ValueError(
            "electorate_area must contain at least one electorate."
        )

    electorate_wgs84 = electorate_area.to_crs(
        "EPSG:4326"
    )

    sed_name_column = find_sed_name_column(
        electorate_wgs84
    )

    all_pois = []

    for _, electorate in electorate_wgs84.iterrows():

        electorate_name = electorate[sed_name_column]

        geometry = electorate.geometry

        print(
            f"\nLoading OSM POIs for {electorate_name}..."
        )

        osm = OSM(
            pbf_path,
            bounding_box=geometry,
            engine="out_of_core",
            workers="auto"
        )

        pois = osm.get_pois(
            custom_filter=POI_FILTER
        )

        if pois is None or pois.empty:
            print(
                f"No POIs found for {electorate_name}."
            )
            continue

        pois = gpd.GeoDataFrame(
            pois,
            geometry="geometry",
            crs="EPSG:4326"
        )

        pois = expand_osm_tags(
            pois
        )

        # Pyrosm uses the bounding envelope of the
        # electorate geometry, so clip to the actual polygon.
        electorate_gdf = gpd.GeoDataFrame(
            geometry=[geometry],
            crs="EPSG:4326"
        )

        pois = gpd.clip(
            pois,
            electorate_gdf
        )

        print(
            f"  {len(pois):,} POIs retained"
        )

        all_pois.append(
            pois
        )

    if not all_pois:
        return gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:4326"
        )

    return gpd.GeoDataFrame(
        pd.concat(
            all_pois,
            ignore_index=True
        ),
        geometry="geometry",
        crs="EPSG:4326"
    )


def expand_osm_tags(
        gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    gdf = gdf.copy()

    tag_rows = []

    for tag in gdf["tags"]:

        if pd.isna(tag):
            tag_rows.append({})
            continue

        if isinstance(tag, str):

            try:
                tag = ast.literal_eval(tag)
            except Exception:
                tag = {}

        tag_rows.append(tag)

    tag_df = pd.DataFrame(tag_rows)

    result = pd.concat(
        [
            gdf.reset_index(drop=True),
            tag_df.reset_index(drop=True)
        ],
        axis=1
    )

    return gpd.GeoDataFrame(
        result,
        geometry="geometry",
        crs=gdf.crs
    )
