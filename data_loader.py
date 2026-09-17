from pathlib import Path

import geopandas as gpd
import pandas as pd

from config import CACHE_DIR, SA1_YEAR, DATA_DIR
from fields import get_geography_column, get_gcp_table_id
from osm import load_osm_pois
from spatial import associate_electorates, get_electorate


def load_cached_datasets(
        data_dir=DATA_DIR,
        force_reload="none",
        electorates=None,
):
    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    sa1_cache = CACHE_DIR / f"sa1_{SA1_YEAR}.parquet"
    suburbs_cache = CACHE_DIR / f"suburbs_{SA1_YEAR}.parquet"
    sed_cache = CACHE_DIR / "sed_2025.parquet"

    if electorates is None:
        raise ValueError(
            "Electorates must be provided"
        )

    electorate_key = "_".join(
        sorted(
            e.strip().casefold().replace(" ", "-")
            for e in electorates
        )
    )

    pois_cache = CACHE_DIR / f"pois_{electorate_key}.parquet"

    # --------------------------------------------------------------
    # Load from cache
    # --------------------------------------------------------------

    if (
            force_reload == "none"
            and sa1_cache.exists()
            and suburbs_cache.exists()
            and sed_cache.exists()
            and pois_cache.exists()
    ):
        print("Loading cached datasets...")

        sa1 = gpd.read_parquet(
            sa1_cache
        )

        suburbs = gpd.read_parquet(
            suburbs_cache
        )

        sed = gpd.read_parquet(
            sed_cache
        )

        pois = gpd.read_parquet(
            pois_cache
        )

        print(
            f"SA1 divisions    : {len(sa1):,}"
        )

        print(
            f"Suburbs          : {len(suburbs):,}"
        )

        print(
            f"State electorates: {len(sed):,}"
        )

        print(
            f"GCP columns : {len(sa1.columns):,}"
        )

        print(
            f"Services : {len(pois):,}"
        )

        return sa1, suburbs, sed, pois

    # --------------------------------------------------------------
    # Find datasets
    # --------------------------------------------------------------

    print("Cache not found or force_reload=True.")
    print("Loading original datasets...")

    sa1_path = find_dataset_shapefile(
        data_dir,
        f"SA1_{SA1_YEAR}"
    )

    suburbs_path = find_dataset_shapefile(
        data_dir,
        "SAL_2021"
        if SA1_YEAR == 2021
        else "SSC_2016"
    )

    sed_path = find_dataset_shapefile(
        data_dir,
        "SED_2025"
    )

    # --------------------------------------------------------------
    # Load spatial datasets
    # --------------------------------------------------------------

    print("\nLoading SA1...")
    sa1 = gpd.read_file(
        sa1_path
    )

    print("Loading Suburbs and Localities...")
    suburbs = gpd.read_file(
        suburbs_path
    )

    print("Loading State Electoral Divisions...")
    sed = gpd.read_file(
        sed_path
    )

    electorate_area = get_electorate(
        sed,
        electorates
    )

    if electorate_area.empty:
        raise ValueError(
            "No selected electorates found."
        )

    # --------------------------------------------------------------
    # Load all NSW SA1 GCP CSVs
    # --------------------------------------------------------------

    # 2021 Census General Community Profile (GCP) tables.
    # Table definitions/titles:
    # https://www.abs.gov.au/census/guide-census-data/2021-census-product-release-guide
    # This selects which gcp tables to use. if you change this make sure to set force_reload to true to get the new data
    gcp_tables = [
        get_gcp_table_id(
            "selected_person_characteristics_by_sex"
        ),
        get_gcp_table_id(
            "selected_medians_and_averages"
        ),
        get_gcp_table_id(
            "ancestry_by_country_of_birth_of_parents"
        ),
        get_gcp_table_id(
            "religious_affiliation_by_sex"
        ),
        get_gcp_table_id(
            "country_of_birth_of_person_by_age_by_sex"
        ),
        get_gcp_table_id(
            "language_used_at_home_by_proficiency_in_spoken_english_by_sex"
        ),
        get_gcp_table_id(
            "rent_weekly_by_landlord_type"
        ),
        get_gcp_table_id(
            "dwelling_structure_by_number_of_bedrooms"
        ),
        get_gcp_table_id(
            "selected_labour_force_education_and_migration_characteristics_by_sex"
        ),
        get_gcp_table_id(
            "labour_force_status_by_age_by_sex"
        ),
        get_gcp_table_id(
            "industry_of_employment_by_age_by_sex"
        ),
        get_gcp_table_id(
            "occupation_by_age_by_sex"
        ),
        get_gcp_table_id(
            "occupation_by_hours_worked_by_sex"
        ),
    ]

    gcp_root = (
            Path(data_dir)
            / f"{SA1_YEAR}_GCP_SA1_for_NSW_short-header"
            / f"{SA1_YEAR} Census GCP Statistical Area 1 for NSW"
    )

    if not gcp_root.exists():

        # Allow the outer directory to have been renamed slightly
        matches = list(
            Path(data_dir).rglob(
                f"{SA1_YEAR} Census GCP Statistical Area 1 for NSW"
            )
        )

        if len(matches) == 1:
            gcp_root = matches[0]

        elif len(matches) == 0:
            raise FileNotFoundError(
                "Could not find the folder:\n"
                f"'{SA1_YEAR} Census GCP Statistical Area 1 for NSW'"
            )

        else:
            raise RuntimeError(
                "Multiple GCP SA1 folders found:\n"
                + "\n".join(
                    str(path)
                    for path in matches
                )
            )

    if gcp_tables is None:

        gcp_files = sorted(
            gcp_root.glob(
                f"{SA1_YEAR}Census_G*_NSW_SA1.csv"
            )
        )

    else:

        gcp_files = []

        for table in gcp_tables:

            matches = sorted(
                gcp_root.glob(
                    f"{SA1_YEAR}Census_{table}*_NSW_SA1.csv"
                )
            )

            if not matches:
                raise FileNotFoundError(
                    f"Could not find any files for {table}"
                )

            gcp_files.extend(matches)

    if not gcp_files:
        raise FileNotFoundError(
            "No SA1 GCP CSV files found in:\n"
            f"{gcp_root}"
        )

    print(
        f"\nLoading {len(gcp_files)} GCP tables..."
    )

    gcp_data = None

    for i, csv_path in enumerate(
            gcp_files,
            start=1
    ):

        print(
            f"  [{i:02d}/{len(gcp_files):02d}] "
            f"{csv_path.name}"
        )

        table = pd.read_csv(
            csv_path,
            dtype=str,
            low_memory=False
        )

        # ----------------------------------------------------------
        # Find SA1 code column
        # ----------------------------------------------------------

        sa1_code_column = None

        for column in [
            f"SA1_CODE_{SA1_YEAR}",
            f"SA1_7DIGITCODE_{SA1_YEAR}",
            f"SA1_7DIG{str(SA1_YEAR)[-2:]}",
        ]:
            if column in table.columns:
                sa1_code_column = column
                break

        if sa1_code_column is None:
            raise ValueError(
                f"Could not find SA1 code column in "
                f"{csv_path.name}.\n\n"
                f"Columns:\n"
                + "\n".join(
                    f"  {column}"
                    for column in table.columns
                )
            )

        table = table.rename(
            columns={
                sa1_code_column: "SA1_CODE"
            }
        )

        # Ensure the join key is consistently a string
        table["SA1_CODE"] = (
            table["SA1_CODE"]
            .astype(str)
            .str.strip()
        )

        # Remove duplicate SA1 code columns if present
        table = table.loc[
            :,
            ~table.columns.duplicated()
        ]

        # ----------------------------------------------------------
        # Merge this table into the GCP dataset
        # ----------------------------------------------------------

        if gcp_data is None:

            gcp_data = table

        else:

            # change the name of columns to include their original table to avoid duplicates
            table_name = (
                csv_path.stem
                .replace(f"{SA1_YEAR}Census_", "")
                .replace("_NSW_SA1", "")
            )

            table = table.rename(
                columns={
                    column: f"{table_name}_{column}"
                    for column in table.columns
                    if column != "SA1_CODE"
                }
            )

            gcp_data = gcp_data.rename(
                columns={
                    f"SA1_CODE_{str(SA1_YEAR)[-2:]}": "SA1_CODE",  # 2021 format
                    f"SA1_7DIGITCODE_{SA1_YEAR}": "SA1_CODE",  # 2016 format
                }
            )

            gcp_data = gcp_data.merge(
                table,
                on="SA1_CODE",
                how="outer",
                validate="one_to_one"
            )

    print(
        f"\nGCP data loaded:"
    )

    print(
        f"  SA1 records : {len(gcp_data):,}"
    )

    print(
        f"  GCP columns : {len(gcp_data.columns):,}"
    )

    # --------------------------------------------------------------
    # Join GCP data to SA1 geometry
    # --------------------------------------------------------------

    sa1 = sa1.rename(
        columns={
            f"SA1_CODE{str(SA1_YEAR)[-2:]}": "SA1_CODE",
            f"SA1_7DIGITCODE_{SA1_YEAR}": "SA1_CODE",
            f"SA1_7DIG{str(SA1_YEAR)[-2:]}": "SA1_CODE",
            f"SA1_7DIGIT": "SA1_CODE",
        }
    )

    sa1["SA1_CODE"] = (
        sa1["SA1_CODE"]
        .astype(str)
        .str.strip()
    )

    sa1 = sa1.merge(
        gcp_data,
        on="SA1_CODE",
        how="left",
        validate="one_to_one"
    )

    # Restore GeoDataFrame after pandas merge
    sa1 = gpd.GeoDataFrame(
        sa1,
        geometry="geometry",
        crs=sa1.crs
    )

    # --------------------------------------------------------------
    # Associate SA1s with suburbs
    # --------------------------------------------------------------

    print(
        "\nAssociating SA1s with suburbs..."
    )

    if sa1.crs != suburbs.crs:
        suburbs = suburbs.to_crs(
            sa1.crs
        )

    sa1_points = (
        sa1.geometry
        .representative_point()
    )

    sa1_point_gdf = gpd.GeoDataFrame(
        sa1[
            [
                "SA1_CODE"
            ]
        ].copy(),
        geometry=sa1_points,
        crs=sa1.crs
    )

    suburb_code_column = get_geography_column(
        "suburb_code"
    )

    suburb_name_column = get_geography_column(
        "suburb_name"
    )

    suburbs_lookup = suburbs[
        [
            suburb_code_column,
            suburb_name_column,
            "geometry",
        ]

    ].copy()

    suburbs_lookup = suburbs_lookup.rename(
        columns={
            suburb_code_column: "_SUBURB_CODE",
            suburb_name_column: "_SUBURB",
        }
    )

    suburb_join = gpd.sjoin(
        sa1_point_gdf,
        suburbs_lookup,
        how="left",
        predicate="within"
    )

    suburb_lookup = (
        suburb_join[
            [
                "SA1_CODE",
                "_SUBURB_CODE",
                "_SUBURB",
            ]
        ]
        .drop_duplicates(
            "SA1_CODE"
        )
    )

    sa1 = sa1.merge(
        suburb_lookup,
        on="SA1_CODE",
        how="left",
        validate="one_to_one"
    )


    # --------------------------------------------------------------
    # Associate SA1s with 2021 electorates
    # --------------------------------------------------------------

    print(
        "\nAssociating SA1s with "
        "2021 electorates..."
    )

    sa1 = associate_electorates(
        sa1,
        sed
    )

    print(
        "\nGetting OSM points of interest "
        "(this could take a while)"
    )

    if force_reload == "census" and pois_cache.exists():

        print(
            f"Loading cached OSM data: {pois_cache}"
        )

        pois = gpd.read_parquet(
            pois_cache
        )

    else:

        pois = load_osm_pois(
            data_dir / "new-south-wales-latest.osm.pbf",
            electorate_area=electorate_area
        )

    # --------------------------------------------------------------
    # Save cache
    # --------------------------------------------------------------

    print(
        "\nCreating cache..."
    )

    sa1.to_parquet(
        sa1_cache
    )

    suburbs.to_parquet(
        suburbs_cache
    )

    sed.to_parquet(
        sed_cache
    )

    pois.to_parquet(
        pois_cache
    )

    print(
        "Cache created successfully."
    )

    print(
        f"SA1 records : {len(sa1):,}"
    )

    print(
        f"SA1 columns : {len(sa1.columns):,}"
    )

    return sa1, suburbs, sed, pois


def find_dataset_shapefile(
        data_dir=DATA_DIR,
        dataset_type=None
):
    """
    Recursively find a shapefile for one of the project datasets.

    The search is case-insensitive.

    dataset_type:
        "SA1" -> SA1 divisions
        "SAL" -> Suburbs and Localities
        "SSC" -> State Suburbs
        "SED" -> State Electoral Divisions
    """

    data_dir = Path(data_dir)

    all_shapefiles = list(
        data_dir.rglob("*.shp")
    )

    matches = [
        shp
        for shp in all_shapefiles
        if dataset_type.casefold() in str(shp).casefold()
    ]

    if len(matches) == 0:
        raise FileNotFoundError(
            f"Could not find {dataset_type} shapefile."
        )

    if len(matches) > 1:
        print(
            f"\nMultiple {dataset_type} shapefiles found:"
        )

        for shp in matches:
            print(f"  {shp}")

        raise RuntimeError(
            f"More than one {dataset_type} shapefile found."
        )

    return matches[0]
