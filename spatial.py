import geopandas as gpd


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
    Spatially associate each SA1 division with a State Electoral Division.
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
        "\nSA1 divisions associated with "
        "State Electoral Divisions."
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
    Return all SA1 divisions belonging to the selected
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
