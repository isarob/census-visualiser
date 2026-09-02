from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from pyrosm import OSM
import ast
import contextily as ctx
import re
import folium
import pandas as pd
import geopandas as gpd
import os

DATA_DIR = Path(__file__).resolve().parent
CACHE_DIR = DATA_DIR / "cache"
SA1_YEAR=2021

def load_cached_datasets(
    data_dir=DATA_DIR,
    force_reload=False,
    gcp_tables=None
):
    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    sa1_cache = CACHE_DIR / "sa1.parquet"
    suburbs_cache = CACHE_DIR / "suburbs.parquet"
    sed_cache = CACHE_DIR / "sed.parquet"
    pois_cache = CACHE_DIR / "pois.parquet"

    # --------------------------------------------------------------
    # Load from cache
    # --------------------------------------------------------------

    if (
        not force_reload
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

    # --------------------------------------------------------------
    # Load all NSW SA1 GCP CSVs
    # --------------------------------------------------------------

    #which gcp tables to use. if you change this make sure to set force_reload to true to get the new data
    gcp_tables=[
        "G01",
        "G02",  # summary indicators
        "G08",  # ancestry
        "G09A",
        "G09B",
        "G09C",
        "G09D", # birthplace
        "G13", # languages
        "G40",  # rent G40 for 2021, G36 for 2016
        "G41",  # dwelling structure
        "G43",  # labour summary
        "G46",  # labour force status
        "G54",  # industry
        "G60",  # occupation
        "G61"
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

            #change the name of columns to include their original table to avoid duplicates
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
                    f"SA1_CODE_{str(SA1_YEAR)[-2:]}":"SA1_CODE", #2021 format
                    f"SA1_7DIGITCODE_{SA1_YEAR}":"SA1_CODE", #2016 format
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
                f"SA1_CODE{str(SA1_YEAR)[-2:]}":"SA1_CODE",
                f"SA1_7DIGITCODE_{SA1_YEAR}":"SA1_CODE",
                f"SA1_7DIGIT":"SA1_CODE",
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

    suburbs_lookup = suburbs[
        [
            "SAL_CODE21",
            "SAL_NAME21",
            "geometry"
        ]
    ].copy()

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
                "SAL_CODE21",
                "SAL_NAME21"
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

    sa1 = sa1.rename(
        columns={
            "SAL_CODE": "_SUBURB_CODE",
            "SAL_NAME21": "_SUBURB"
        }
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

    '''
    comment out the loading and uncomment this if you've loaded osm data before and are changing the census cache
    pois = gpd.read_parquet(
            pois_cache
            )
    '''
    osm = OSM(
        "new-south-wales-latest.osm.pbf"
    )

    pois = osm.get_pois(
        custom_filter = {
            "amenity": [
                "hospital",
                "clinic",
                "doctors",
                "school",
                "childcare",
                "kindergarten",
                "community_centre",
                "library",
                "place_of_worship",
            ],

            "healthcare": [
                "hospital",
                "clinic",
                "doctor",
                "physiotherapist",
                "rehabilitation",
                "centre",
            ],

            "shop": [
                "mall",
            ],

            "leisure": [
                "sports_centre",
                "stadium",
            ],

            "social_facility": True,
        }
    )

    #put tags in poi["tags"] into main tags
    pois = expand_osm_tags(pois)

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
    type=None
):
    """
    Recursively find a shapefile for one of the project datasets.

    type:
        "SA1" -> SA1 Divisions
        "SAL"  -> Suburbs and Localities
        "SED"  -> State Electoral Divisions
    """

    data_dir = Path(data_dir)

    all_shapefiles = list(
        data_dir.rglob("*.shp")
    )

    matches = [
        shp for shp in all_shapefiles
        if type in str(shp)
        
    ]

    if len(matches) == 0:
        raise FileNotFoundError(
            f"Could not find {type} shapefile."
        )

    if len(matches) > 1:
        print(
            f"\nMultiple {type} shapefiles found:"
        )

        for shp in matches:
            print(f"  {shp}")

        raise RuntimeError(
            f"More than one {type} shapefile found."
        )

    return matches[0]




def find_sed_name_column(sed):
    """
    Find the State Electoral Division name field.
    Allows for the changing of electoral divisions
    """

    for column in sed.columns:

        name = str(column).upper()

        if "SED" in name and "NAME" in name:
            return column

    raise ValueError(
        "Could not identify the SED name column.\n\n"
        "Available columns:\n"
        + "\n".join(
            f"  {column}"
            for column in sed.columns
        )
    )


def associate_electorates(
    sa1_divisions,
    sed
):
    """
    Spatially associate every Mesh Block with its 2021
    State Electoral Division.
    """

    if sa1_divisions.crs is None:
        raise ValueError(
            "Mesh Blocks do not have a CRS."
        )

    if sed.crs is None:
        raise ValueError(
            "State Electoral Divisions do not have a CRS."
        )

    if sa1_divisions.crs != sed.crs:
        sed = sed.to_crs(
            sa1_divisions.crs
        )

    sed_name_column = find_sed_name_column(
        sed
    )

    print(
        f"\nUsing electorate name column: "
        f"{sed_name_column}"
    )

    sed_code_column = None

    for column in [
        "SED_CODE21",
        "SED_CODE",
        "SED_CODE_2021"
    ]:
        if column in sed.columns:
            sed_code_column = column
            break

    mesh = sa1_divisions.copy()

    mesh["_mesh_point"] = (
        mesh.geometry
        .representative_point()
    )

    sed_columns = [
        sed_name_column,
        "geometry"
    ]

    if sed_code_column:
        sed_columns.insert(
            0,
            sed_code_column
        )

    sed_lookup = sed[
        sed_columns
    ].copy()

    rename_dict = {
        sed_name_column: "_ELECTORATE"
    }

    if sed_code_column:
        rename_dict[
            sed_code_column
        ] = "_ELECTORATE_CODE"

    sed_lookup = sed_lookup.rename(
        columns=rename_dict
    )

    joined = gpd.sjoin(
        mesh.set_geometry("_mesh_point"),
        sed_lookup,
        how="left",
        predicate="within"
    )

    joined = joined.set_geometry(
        mesh.geometry.name
    )

    joined = joined.drop(
        columns=[
            "_mesh_point",
            "index_right"
        ],
        errors="ignore"
    )

    unmatched = (
        joined["_ELECTORATE"]
        .isna()
        .sum()
    )

    print(
        "\nMesh blocks associated with "
        "2021 electorates."
    )

    if unmatched:
        print(
            f"WARNING: {unmatched:,} sa1 divisions "
            f"could not be associated."
        )
    else:
        print(
            "All sa1 divisions were associated "
            "with an electorate."
        )

    return joined

def sa1_divisions_in_electorate(
    sa1_divisions,
    electorate
):
    """
    Return all sa1 divisions belonging to a 2021
    State Electoral Division.
    """

    # normalise to list
    if isinstance(electorate, str):
        electorates = [electorate]
    else:
        electorates = list(electorate)

    electorates = {
        e.strip().casefold()
        for e in electorates
    }

    mask = (
        sa1_divisions["_ELECTORATE"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .isin(electorates)
    )


    result = sa1_divisions.loc[
        mask
    ].copy()

    if result.empty:
        print(
            f"No sa1 divisions found for "
            f"'{electorate}'."
        )
    else:
        print(
            f"Found {len(result):,} sa1 divisions "
            f"for '{electorate}'."
        )

    return result


def get_electorate(
    sed,
    electorate
):
    """
    Return one or more State Electoral Division polygons.

    electorate can be:
    - "Auburn"
    - ["Auburn", "Bankstown", "Parramatta"]
    """

    name_column = find_sed_name_column(sed)

    # normalise to list
    if isinstance(electorate, str):
        electorates = [electorate]
    else:
        electorates = list(electorate)

    electorates = {
        e.strip().casefold()
        for e in electorates
    }

    mask = (
        sed[name_column]
        .astype(str)
        .str.strip()
        .str.casefold()
        .isin(electorates)
    )

    result = sed.loc[mask].copy()

    if result.empty:
        print(
            f"No electorate found for "
            f"{electorate!r}."
        )

    return result



def list_electorate_names(
    sed,
    sort=True,
    print_names=True
):
    """
    Return all unique electorate names from a 2021 SED GeoDataFrame.

    Parameters
    ----------
    sed : GeoDataFrame
        State Electoral Divisions layer.
    sort : bool
        Sort names alphabetically.
    print_names : bool
        Print names to console.

    Returns
    -------
    list[str]
    """

    electorate_names = (
        sed["SED_NAME25"]
        .dropna()
        .unique()
        .tolist()
    )

    if sort:
        electorate_names = sorted(electorate_names)

    if print_names:
        print(
            f"{len(electorate_names)} electorates found:\n"
        )

        for name in electorate_names:
            print(name, end=", ")

    return electorate_names


def get_top_languages(row, n=5):
    language_cols = [
        c for c in row.index
        if re.match(r"G13._POL_(?!Tot)[^_\W]*_Tot$",c)
       
    ]

    langs = []

    for col in language_cols:

        count = pd.to_numeric(row[col], errors="coerce")

        if pd.notna(count) and count > 0:

            name = re.sub(r"G13._POL_", "", col)

            name = (
                name
                .replace("_Tot", "")
                .replace("_", " ")
            )



            langs.append((name, count))

    langs.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return "<br>".join(
        f"{lang}: {count:,}"
        for lang, count in langs[:n]
    )


def electorate_summary(
    sa1_divisions,
    sed,
    electorate,
    summary_fields
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

    # make some columns numeric
    cols = [
        "G40_Tot_Tot",
        "G41_Total_Total",
        "G41_Flt_apart_Tot_Total",
        "G41_Separate_house_Total",
        "G46B_P_Tot_Emp_Tot",
        "G46B_P_Tot_LF_Tot"
    ]

    for col in cols:
        if col in electorate_mesh.columns:
            electorate_mesh[col] = pd.to_numeric(
                electorate_mesh[col],
                errors="coerce"
            )

    '''
    print("electorate cols are")
    for col in electorate_mesh.columns:
        print(col)
    '''

    electorate_mesh["Pct_Renting"] = (
        electorate_mesh["G40_Tot_Tot"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Pct_Apartments"] = (
        electorate_mesh["G41_Flt_apart_Tot_Total"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Pct_Separate_Houses"] = (
        electorate_mesh["G41_Separate_house_Total"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    cols = [
        "Australian_citizen_P",
        "G02_Median_tot_hhd_inc_weekly",
        "Pct_Renting",
        "G02_Median_age_persons"
    ]

    scaler = MinMaxScaler()

    scaled = scaler.fit_transform(
        electorate_mesh[cols]
    )

    scaled_df = pd.DataFrame(
        scaled,
        columns=cols,
        index=electorate_mesh.index
    )

    electorate_mesh["Feasibility"] = (
        (0.5 * scaled_df["Australian_citizen_P"])
        * (1 - scaled_df["G02_Median_tot_hhd_inc_weekly"])
        * scaled_df["Pct_Renting"]
        * (1 - scaled_df["G02_Median_age_persons"])
    )

    electorate_mesh["employment_rate"] = (
        electorate_mesh["G46B_P_Tot_Emp_Tot"]
        / electorate_mesh["G46B_P_Tot_LF_Tot"]
    ) * 100

    # -------------------------
    # SUMS
    # -------------------------

    sum_rows = []

  
    for col, label in summary_fields.items():

        if col not in electorate_mesh.columns:
            continue

        values = pd.to_numeric(
            electorate_mesh[col],
            errors="coerce"
        )

        if not values.notna().any():
            continue

        if (
            col.startswith("Pct_")
            or col.startswith("pct_")
            or col == "employment_rate"
            or "Average" in col
            or "Median" in col
        ):

            sum_rows.append({
                "column": label,
                "value": values.mean(),
                "aggregation": "mean"
            })

        else:

            sum_rows.append({
                "column": label,
                "value": values.sum(),
                "aggregation": "sum"
            })

    sums_df = pd.DataFrame(sum_rows)

  
    # -------------------------
    # FOREIGN LANGUAGE TOTALS
    # -------------------------

    language_rows = []

    for col in electorate_mesh.columns:

        if "_POL_" not in col:
            continue

        if not col.endswith("_Tot"):
            continue

        if "UOLSE" in col:
            continue

        values = pd.to_numeric(
            electorate_mesh[col],
            errors="coerce"
        )

        if not values.notna().any():
            continue

        language_name = col

        language_name = language_name.split("_POL_", 1)[1]
        language_name = language_name[:-4]  # remove _Tot

        language_rows.append({
            "language": language_name,
            "total": values.sum()
        })
        language_df = (
            pd.DataFrame(language_rows)
            .sort_values(
                "total",
                ascending=False
            )
        )

    print("\n===== COUNTS (SUMS) =====")
    print(
        sums_df.to_csv(
            index=False
        )
    )


    print("\n===== FOREIGN LANGUAGE TOTALS =====")
    print(
        language_df.to_csv(
            index=False
        )
    )

    return {
        "sums": sums_df,
        "languages": language_df
    }

def generate_html_map(
    sa1_divisions,
    sed,
    electorate,
    colour_column=None,
    popup_fields=None,      # dict
    tooltip_fields=None,    # dict
    services_df=None,
    tiles="CartoDB positron",
    cmap="viridis",
    save_path=None
):

    if save_path == None:
        if len(electorate) == 1 or isinstance(electorate, str):
            save_path = electorate[0]+"_nswsocialists_data_2027.html"
        else:
            save_path = "multi_nswsocialists_data_2027.html"


    popup_columns = None
    popup_kwds = {}

    if popup_fields:
        popup_columns = list(popup_fields.keys())
        popup_kwds["aliases"] = list(popup_fields.values())

    tooltip_columns = None
    tooltip_kwds = {}

    if tooltip_fields:
        tooltip_columns = list(tooltip_fields.keys())
        tooltip_kwds["aliases"] = list(tooltip_fields.values())

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

    #make some columns numeric
    cols = [
    "G40_Tot_Tot",
    "G41_Total_Total",
    "G41_Flt_apart_Tot_Total",
    "G41_Separate_house_Total",
    "G46B_P_Tot_Emp_Tot",
    "G46B_P_Tot_LF_Tot"

    ]

    for col in cols:
        electorate_mesh[col] = pd.to_numeric(
            electorate_mesh[col],
            errors="coerce"
        )

    occupation_cols = {
        "managers": "G60B_P_Tot_Managers",
        "professionals": "G60B_P_Tot_Professionals",
        "technic_trades": "G60B_P_Tot_TechnicTrades_W",
        "community_personal_service": "G60B_P_Tot_CommunPersnlSvc_W",
        "clerical_admin": "G60B_P_Tot_ClericalAdminis_W",
        "sales": "G60B_P_Tot_Sales_W",
        "machinery_drivers": "G60B_P_Tot_Mach_oper_drivers",
        "labourers": "G60B_P_Tot_Labourers",
        "occ_not_stated": "G60B_P_Tot_Occu_ID_NS",
    }


    for name, col in occupation_cols.items():
        electorate_mesh[col] = pd.to_numeric(
            electorate_mesh[col],
            errors="coerce"
        )
        electorate_mesh[f"pct_{name}"] = (
            electorate_mesh[col] /
            electorate_mesh["G46B_P_Tot_Emp_Tot"]
        ) * 100

    electorate_mesh["Pct_Renting"] = (
        electorate_mesh["G40_Tot_Tot"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Pct_Apartments"] = (
        electorate_mesh["G41_Flt_apart_Tot_Total"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Pct_Separate_Houses"] = (
        electorate_mesh["G41_Separate_house_Total"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Top Languages"] = (
            electorate_mesh.apply(
                get_top_languages,
                axis=1
            )
        )

    cols = [
        "Australian_citizen_P",
        "G02_Median_tot_hhd_inc_weekly",
        "Pct_Renting",
        "G02_Median_age_persons"
    ]

    scaler = MinMaxScaler()

    scaled = scaler.fit_transform(
        electorate_mesh[cols]
    )

    scaled_df = pd.DataFrame(
        scaled,
        columns=cols,
        index=electorate_mesh.index
    )

    electorate_mesh["Feasibility"] = (
        (0.5*scaled_df["Australian_citizen_P"])
        * (1-scaled_df["G02_Median_tot_hhd_inc_weekly"])
        * scaled_df["Pct_Renting"]
        * (1-scaled_df["G02_Median_age_persons"])
    )

    electorate_mesh["employment_rate"] = (
        electorate_mesh["G46B_P_Tot_Emp_Tot"] /
        electorate_mesh["G46B_P_Tot_LF_Tot"]
    ) * 100

    explore_kwargs = {
        "popup":popup_columns,
        "tooltip":tooltip_columns,
        "popup_kwds":popup_kwds,
        "tooltip_kwds":tooltip_kwds,
        "tiles": tiles,
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
            "scheme":"Quantiles",
            "k":5,
            "legend": False,
        })



    m = electorate_mesh.explore(**explore_kwargs)

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

        # --------------------------------------------------
        # Categorise services
        # --------------------------------------------------

        services_df["category"] = "Other"

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
                ["childcare", "kindergarten"]
            ),
            "category"
        ] = "Childcare"

        services_df.loc[
            services_df["amenity"] == "community_centre",
            "category"
        ] = "Community Centres"

        services_df.loc[
            services_df["shop"] == "mall",
            "category"
        ] = "Shopping Centres"

        # Churches
        services_df.loc[
            (
                (services_df["amenity"] == "place_of_worship")
            ),
            "category"
        ] = "Churches"


        # Aged Care
        services_df.loc[
            (
                (services_df["amenity"] == "social_facility") &
                (services_df["social_facility"] == "nursing_home")
            ),
            "category"
        ] = "Aged Care"

        services_df.loc[
            services_df["amenity"].isin([
                "nursing_home",
                "social_facility"
            ]),
            "category"
        ] = "Aged Care"


        services_df.loc[
            services_df["leisure"].isin([
                "sports_centre",
                "stadium",
                "pitch",
                "track",
                "fitness_centre",
                "sports_hall",
                "swimming_pool",
                "golf_course"
            ]),
            "category"
        ] = "Sports Facilities"

        services_df.loc[
            (
                services_df["amenity"] == "clinic"
            )
            |
            (
                services_df["healthcare"] == "clinic"
            ),
            "category"
        ] = "Clinics"

        services_df["Ownership"] = (
            services_df["operator:type"]
            .fillna(services_df["ownership"])
        )

        services_df["Beds"] = services_df["beds"]

        services_df["Emergency"] = services_df["emergency"]

        services_df["Hospital_Type"] = (
            services_df["hospital:type"]
        )

        services_df["School_Type"] = (
            services_df["school:type"]
            .fillna(services_df["operator:type"])
        )

        services_df["Enrolment"] = (
            services_df["school:enrolment"]
        )

        services_df["Grades"] = (
            services_df["grades"]
        )

        services_df["Selective"] = (
            services_df["school:selective"]
        )

        services_df["Religion"] = (
            services_df["religion"]
        )

        services_df["Specialty"] = (
            services_df["healthcare:speciality"]
        )

        services_df["Bulk_Billing"] = (
            services_df["bulkbilling"]
        )

        centroids = (
            services_df
            .to_crs("EPSG:7856")
            .geometry
            .representative_point()
        )

        centroids = gpd.GeoSeries(
            centroids,
            crs="EPSG:7856"
        ).to_crs("EPSG:4326")

        services_df["latitude"] = centroids.y.values
        services_df["longitude"] = centroids.x.values


        icon_lookup = {
            "Hospitals": ("plus-circle", "red"),
            "Schools": ("graduation-cap", "blue"),
            "Childcare": ("child", "green"),
            "Community Centres": ("users", "purple"),
            "Shopping Centres": ("shopping-cart", "orange"),
            "Clinics": ("stethoscope", "darkred"),

            "Churches": ("church", "cadetblue"),
            "Aged Care": ("home", "pink"),
            "Sports Facilities": ("futbol", "darkgreen"),

            "Other": ("info-circle", "gray"),
        }

        for _, row in services_df.iterrows():

            icon_name, icon_colour = icon_lookup.get(
                row["category"],
                ("info-sign", "gray")
            )

            popup_html = f"""
            <b>{row.get('name', '')}</b><br>
            <b>Category:</b> {row.get('category', '')}<br>
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
                tooltip=row["name"],
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
        print(f"Interactive map saved to: {save_path}")

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

    column_name = list(highlight_field.keys())[0]
    display_name = list(highlight_field.values())[0]

    cols = [
        "G40_Tot_Tot",
        "G41_Total_Total",
        "G41_Flt_apart_Tot_Total",
        "G41_Separate_house_Total",
        "G46B_P_Tot_Emp_Tot",
        "G46B_P_Tot_LF_Tot"
    ]

    for col in cols:
        if col in electorate_mesh.columns:
            electorate_mesh[col] = pd.to_numeric(
                electorate_mesh[col],
                errors="coerce"
            )

    electorate_mesh["Pct_Renting"] = (
        electorate_mesh["G40_Tot_Tot"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Pct_Apartments"] = (
        electorate_mesh["G41_Flt_apart_Tot_Total"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Pct_Separate_Houses"] = (
        electorate_mesh["G41_Separate_house_Total"]
        / electorate_mesh["G41_Total_Total"]
        * 100
    )

    electorate_mesh["Top Languages"] = (
        electorate_mesh.apply(
            get_top_languages,
            axis=1
        )
    )

    feasibility_cols = [
        "Australian_citizen_P",
        "G02_Median_tot_hhd_inc_weekly",
        "Pct_Renting",
        "G02_Median_age_persons"
    ]

    if all(
        col in electorate_mesh.columns
        for col in feasibility_cols
    ):
        scaler = MinMaxScaler()

        scaled = scaler.fit_transform(
            electorate_mesh[feasibility_cols]
        )

        scaled_df = pd.DataFrame(
            scaled,
            columns=feasibility_cols,
            index=electorate_mesh.index
        )

        electorate_mesh["Feasibility"] = (
            (0.5 * scaled_df["Australian_citizen_P"])
            * (1 - scaled_df["G02_Median_tot_hhd_inc_weekly"])
            * scaled_df["Pct_Renting"]
            * (1 - scaled_df["G02_Median_age_persons"])
        )

    electorate_mesh["employment_rate"] = (
        electorate_mesh["G46B_P_Tot_Emp_Tot"]
        / electorate_mesh["G46B_P_Tot_LF_Tot"]
    ) * 100

    if column_name not in electorate_mesh.columns:
        raise ValueError(
            f"Column '{column_name}' not found in electorate mesh data."
        )

    electorate_mesh[column_name] = pd.to_numeric(
        electorate_mesh[column_name],
        errors="coerce"
    )

    electorate_mesh = electorate_mesh.to_crs(
        epsg=3857
    )

    electorate_polygon = electorate_polygon.to_crs(
        epsg=3857
    )

    fig, ax = plt.subplots(
        figsize=(12, 12)
    )

    electorate_mesh.plot(
        column=column_name,
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
            f"?key=cb1_296x_1_e8d7efe65c17bb102d553727"
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

        if not os.path.exists("Heatmaps"):
            os.makedirs("Heatmaps")

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
    else:
        plt.show()


def expand_osm_tags(gdf):

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

    return pd.concat(
        [gdf.reset_index(drop=True),
         tag_df.reset_index(drop=True)],
        axis=1
    )


if __name__ == "__main__":

    sa1_divisions, suburbs, sed, services = (
        load_cached_datasets(
            force_reload=False
        )
    )

    #uncomment this to list all electorate names 
    #list_electorate_names(sed)
 
    #add an electorate name here to include it in the maps
    electorates = [
        "Auburn",
        "Granville",
        "Summer Hill",
        "Newtown",
        "Wollongong",
        "Wallsend"
                
    ]

    '''
       
    '''
    #add a column here to generate a heatmap based on it
    heatmap_columns = [{"G40_Tot_LT_Ste_ter_hsg_auth": "Public Housing (absolute)"},
        {"G02_Median_tot_prsnl_inc_weekly": "Median Personal Income ($/week)"},
        {"Pct_Renting": "Renting (%)"},
        {"G13C_POL_Arabic_Tot":"Arabic Speakers (absolute)"},
        {"G13E_POL_Vietnamese_Tot":"Vietnamese Speakers (absolute)"},
        {"G13C_POL_CL_Canton_Tot":"Cantonese Speakers (absolute)"},
        {"G13D_POL_CL_Tot_Tot":"Chinese Langage Speakers (absolute)"},
        {"G13D_POL_Persian_ED_Tot":"Farsi and Persian Speakers (absolute)"},
        {"G13D_POL_Korean_Tot":"Korean Speakers (absolute)"},
        {"G13E_POL_Tamil_Tot":"Tamil Speakers (absolute)"},
        {"G02_Median_age_persons": "Median Age"},

    ]

    
    
    for electorate in electorates:
        #print electorate summaries
        summary = electorate_summary(
            sa1_divisions,
            sed,
            electorate,
            summary_fields = {
                
                
                # Population
                "Tot_P_P": "Population",
                "Australian_citizen_P": "Australian Citizens",

                # Census summaries
                "G02_Median_age_persons": "Median Age",
                "G02_Median_tot_prsnl_inc_weekly": "Median Personal Income ($/week)",
                "G02_Median_tot_hhd_inc_weekly": "Median Household Income ($/week)",
                "G02_Median_tot_fam_inc_weekly": "Median Family Income ($/week)",
                "G02_Median_rent_weekly": "Median Rent ($/week)",
                "G02_Median_mortgage_repay_monthly": "Median Mortgage Repayment ($/month)",

                # Diversity
                "Lang_used_home_Eng_only_P": "English Only at Home",
                "Lang_used_home_Oth_Lang_P": "Other Language at Home",


                # Landlord type
                "G40_Tot_LT_Real_eSte_agent": "Rentals via Real Estate Agent",
                "G40_Tot_LT_Psn_not_Sme_hhd": "Rentals via Private Landlord",
                "G40_Tot_LT_Ste_ter_hsg_auth": "State/Territory Housing Authority",
                "G40_Tot_LT_com_hou_pro": "Community Housing Provider",
                "G40_Tot_Tot": "Total Rentals",


                # Households
                "G41_Total_Total": "Total Households",
                "G41_Flt_apart_Tot_Total": "Total Apartments",

                "G02_Average_household_size": "Average Household Size",

                "G61B_P_Tot_0": "Worked 0 Hours",
                "G61B_P_Tot_1_19": "Worked 1–19 Hours",
                "G61B_P_Tot_20_29": "Worked 20–29 Hours",
                "G61B_P_Tot_30_34": "Worked 30–34 Hours",
                "G61B_P_Tot_35_39": "Worked 35–39 Hours",
                "G61B_P_Tot_40_44": "Worked 40–44 Hours",
                "G61B_P_Tot_45_49": "Worked 45–49 Hours",
                "G61B_P_Tot_50_over": "Worked 50+ Hours",
                "G61B_P_Tot_hours_NS": "Hours Worked Not Stated",


                },
        )

        '''
        #uncomment this to generate heatmaps
        for col in heatmap_columns:
            generate_heatmap(
                sa1_divisions,
                sed,
                electorate,
                highlight_field= col,
                saveChart = True
            )
        '''

    
    



    #get the services for the electorates we're looking at
    services_dfs = []

    for electorate in electorates:
        electorate_gdf = get_electorate(
            sed,
            electorate
        )

        electorate_gdf = electorate_gdf.to_crs(
            services.crs
        )

        services_dfs.append(
            gpd.clip(
                services,
                electorate_gdf
            )
        )

    services_df = pd.concat(
        services_dfs,
        ignore_index=True
    )

  
    #create interactable map
    generate_html_map(
    sa1_divisions,
    sed,
    electorates,
    colour_column= 'Feasibility',
    popup_fields = {
    # Geography
    "SA1_CODE": "SA1 Code",
    "SA2_NAME21": "SA2",
    
    # Population
    "Tot_P_P": "Population",
    "Australian_citizen_P": "Australian Citizens",

    # Census summaries
    "G02_Median_age_persons": "Median Age",
    "G02_Median_tot_prsnl_inc_weekly": "Median Personal Income ($/week)",
    "G02_Median_tot_hhd_inc_weekly": "Median Household Income ($/week)",
    "G02_Median_tot_fam_inc_weekly": "Median Family Income ($/week)",
    "G02_Median_rent_weekly": "Median Rent ($/week)",
    "G02_Median_mortgage_repay_monthly": "Median Mortgage Repayment ($/month)",

    # Diversity
    "Lang_used_home_Eng_only_P": "English Only at Home",
    "Lang_used_home_Oth_Lang_P": "Other Language at Home",
    "Top Languages": "Top Languages",

    # Housing
    "Pct_Renting": "Renting (%)",
    "Pct_Apartments": "Apartments (%)",

    # Landlord type
    "G40_Tot_LT_Real_eSte_agent": "Rentals via Real Estate Agent",
    "G40_Tot_LT_Psn_not_Sme_hhd": "Rentals via Private Landlord",
    "G40_Tot_LT_Ste_ter_hsg_auth": "State/Territory Housing Authority",
    "G40_Tot_LT_com_hou_pro": "Community Housing Provider",

    # Households
    "G41_Total_Total": "Total Households",
    "G02_Average_household_size": "Average Household Size",


    # Employment
    "employment_rate": "Employment Rate (%)",
    "pct_managers": "Managers (%)",
    "pct_professionals": "Professionals (%)",
    "pct_technic_trades": "Technicians & Trades (%)",
    "pct_community_personal_service": "Community & Personal Service (%)",
    "pct_clerical_admin": "Clerical & Administrative (%)",
    "pct_sales": "Sales (%)",
    "pct_machinery_drivers": "Machinery Operators & Drivers (%)",
    "pct_labourers": "Labourers (%)",
    "pct_occ_not_stated": "Occupation Not Stated (%)",
    },



    tooltip_fields = {
        "Tot_P_P": "Population",
        "G41_Total_Total": "Total Households",
        "G02_Median_age_persons": "Median Age",
        "G02_Median_tot_prsnl_inc_weekly": "Median Personal Income ($/week)",
        "Pct_Renting": "Renting (%)",
        "G02_Median_rent_weekly": "Median Rent ($/week)",
        "Pct_Apartments": "Apartments (%)",
        "Lang_used_home_Eng_only_P": "English Only at Home",
        "Lang_used_home_Oth_Lang_P": "Other Language at Home",
        "Top Languages": "Top Languages",

    },

    services_df=services_df

    ) 



    

