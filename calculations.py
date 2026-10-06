import re

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from fields import get_gcp_column
from spatial import (
    get_electorate,
    sa1_divisions_in_electorate,
)

def get_top(df, match, split, n=5):
    cols = [
        c for c in df.columns
        if re.match(match, c)

    ]

    matches = []

    for col in cols:

        count = pd.to_numeric(df[col], errors="coerce").sum()

        if pd.notna(count) and count > 0:
            name = split(col)
            matches.append((col, f"{name}", count))

    matches.sort(
        key=lambda x: x[2],
        reverse=True
    )

    outs = []
    for col, name, count in matches:
        outs.append((col, f"{name} ({count})"))

    return outs

def get_top_languages_tooltip(df, n=5):
    language_cols = [
        c for c in df.index
        if re.match(r"G13._POL_(?!Tot$).+_Tot$", c)

    ]

    langs = []

    for col in language_cols:

        count = pd.to_numeric(df[col], errors="coerce")

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

def get_top_languages(df):
    return get_top(
        df,
        r"G13._POL_(?!Tot$).+_Tot$",
        lambda col: (
            re.sub(r"G13._POL_", "", col)
            .replace("_Tot", "")
            .replace("_", " ")
        )
    )


def get_languages(df):
    return get_top(
        df,
        r"G13._POL_(?!Tot$).",
        lambda col: (
            re.sub(r"G13._POL_", "", col)
            .replace("_Tot", "")
            .replace("_", " ")
        )
    )
    

def get_top_nationalities(df):
    def format_nationalities(col_name):
            name = re.sub(r"G09._P_", "", col_name)

            name = (
                name
                .replace("_Tot", "")
                .replace("_", " ")
            )
            return name
    nationalities = get_top(df, r"G09._P_.+_Tot$", format_nationalities)
    return nationalities

def get_top_ancestries(df):
    return get_top(
        df,
        r"G08_[A-Za-z0-9_]+_Tot_resp$",
        lambda col: (
            col
            .replace("G08_", "")
            .replace("_Tot_resp", "")
            .replace("_", " ")
        )
    )


def get_top_religions(df):
    return get_top(
        df,
        r"G14_\w*_P$",
        lambda col: (
            col
            .replace("G14_", "")
            [:-2]
            .replace("_", " ")
        )
    )


def get_top_industries(df):
    return get_top(
        df,
        r"G54._P_\w*_Tot$",
        lambda col: (
            re.sub(r"G54._P_", "", col)
            .replace("_Tot", "")
            .replace("_", " ")
        )
    )


def get_language_proficiency(df):

    top_languages = get_languages(df)

    rows = []

    for language_col, language_total in top_languages:

        match = re.match(
            r"G13(.)_POL_(.+)_Tot$",
            language_col
        )

        if not match:
            continue

        if "UOLSE" in language_col:
            continue

        language = match.group(2)
        print(language)

        vw_col = f"G13{match.group(1)}_POL_{language}_UOLSE_VWorW"
        nw_col = f"G13{match.group(1)}_POL_{language}_UOLSE_NWorNAA"
        print(f"{vw_col}, {nw_col}") 

        vw = pd.to_numeric(
            df.get(vw_col, 0),
            errors="coerce"
        )

        nw = pd.to_numeric(
            df.get(nw_col, 0),
            errors="coerce"
        )
        print(f"{vw}, {nw}")

        vw = vw.fillna(0).sum() if hasattr(vw, "fillna") else vw
        nw = nw.fillna(0).sum() if hasattr(nw, "fillna") else nw

        english_total = vw + nw

        if english_total > 0:
            rows.append({
                "language": language.replace("_", " "),
                "decent": vw,
                "not_well": nw,
                "pct_not_well": nw / english_total * 100
            })

    return pd.DataFrame(rows)

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

    electorate_mesh = calculate_extra_columns(electorate_mesh)


    '''
    print("electorate cols are")
    for col in electorate_mesh.columns:
        print(col)
    '''

    # SUMS

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

    # FOREIGN LANGUAGE TOTALS

    languages = get_top_languages(electorate_mesh)
    language_proficiency = get_language_proficiency(electorate_mesh)
    ancestries = get_top_ancestries(electorate_mesh)
    religions = get_top_religions(electorate_mesh)
    industries = get_top_industries(electorate_mesh)
    nationalities = get_top_nationalities(electorate_mesh)

    return {
        "sums": sums_df,
        "languages": languages,
        "language_proficiency": language_proficiency,
        "ancestries": ancestries,
        "religions": religions,
        "industries": industries,
        "nationalities": nationalities,
    }

def calculate_extra_columns(sa1_dataframe):
    numeric_cols = [
        get_gcp_column("total_rentals"),
        get_gcp_column("total_households"),
        get_gcp_column("apartments"),
        get_gcp_column("separate_houses"),
        get_gcp_column("total_employed"),
        get_gcp_column("total_labour_force"),
        get_gcp_column("state_housing_authority"),
    ]

    for col in numeric_cols:
        if col in sa1_dataframe.columns:
            sa1_dataframe[col] = pd.to_numeric(
                sa1_dataframe[col],
                errors="coerce"
            )

    occupation_cols = {
        "managers": get_gcp_column("managers"),
        "professionals": get_gcp_column("professionals"),
        "technic_trades": get_gcp_column("technicians_and_trades"),
        "community_personal_service": get_gcp_column(
            "community_and_personal_service"
        ),
        "clerical_admin": get_gcp_column(
            "clerical_and_administrative"
        ),
        "sales": get_gcp_column("sales"),
        "machinery_drivers": get_gcp_column(
            "machinery_operators_and_drivers"
        ),
        "labourers": get_gcp_column("labourers"),
        "occ_not_stated": get_gcp_column(
            "occupation_not_stated"
        ),
    }

    total_employed = get_gcp_column(
        "total_employed"
    )

    for name, col in occupation_cols.items():
        if col not in sa1_dataframe.columns:
            continue

        sa1_dataframe[col] = pd.to_numeric(
            sa1_dataframe[col],
            errors="coerce"
        )

        sa1_dataframe[f"pct_{name}"] = (
            sa1_dataframe[col]
            / sa1_dataframe[total_employed]
        ) * 100

    total_rentals = get_gcp_column(
        "total_rentals"
    )

    total_households = get_gcp_column(
        "total_households"
    )

    state_housing_authority = get_gcp_column(
        "state_housing_authority"
    )

    apartments = get_gcp_column(
        "apartments"
    )

    separate_houses = get_gcp_column(
        "separate_houses"
    )

    sa1_dataframe["Pct_Renting"] = (
        sa1_dataframe[total_rentals]
        / sa1_dataframe[total_households]
        * 100
    )

    sa1_dataframe["Pct_Public_Housing"] = (
        sa1_dataframe[state_housing_authority]
        / sa1_dataframe[total_households]
        * 100
    )

    sa1_dataframe["Pct_Apartments"] = (
        sa1_dataframe[apartments]
        / sa1_dataframe[total_households]
        * 100
    )

    sa1_dataframe["Pct_Separate_Houses"] = (
        sa1_dataframe[separate_houses]
        / sa1_dataframe[total_households]
        * 100
    )

    sa1_dataframe["Top Languages"] = (
        sa1_dataframe.apply(
            get_top_languages_tooltip,
            axis=1
        )
    )

    feasibility_cols = [
        get_gcp_column("australian_citizen"),
        get_gcp_column("median_household_income"),
        "Pct_Renting",
        get_gcp_column("median_age"),
    ]

    if all(
        col in sa1_dataframe.columns
        for col in feasibility_cols
    ):
        scaler = MinMaxScaler()

        scaled = scaler.fit_transform(
            sa1_dataframe[feasibility_cols]
        )

        scaled_df = pd.DataFrame(
            scaled,
            columns=feasibility_cols,
            index=sa1_dataframe.index
        )

        sa1_dataframe["Feasibility"] = (
            (0.5 * scaled_df[
                get_gcp_column("australian_citizen")
            ])
            * (
                1 - scaled_df[
                    get_gcp_column("median_household_income")
                ]
            )
            * scaled_df["Pct_Renting"]
            * (
                1 - scaled_df[
                    get_gcp_column("median_age")
                ]
            )
        )

    total_labour_force = get_gcp_column(
        "total_labour_force"
    )

    sa1_dataframe["employment_rate"] = (
        sa1_dataframe[total_employed]
        / sa1_dataframe[total_labour_force]
    ) * 100

    return sa1_dataframe
