import re

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from fields import get_gcp_column
from spatial import (
    get_electorate,
    sa1_divisions_in_electorate,
)


def get_top_languages(row, n=5):
    language_cols = [
        c for c in row.index
        if re.match(r"G13._POL_(?!Tot)[^_\W]*_Tot$", c)

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

    electorate_mesh = calculate_extra_columns(electorate_mesh)

    '''
    print("electorate cols are")
    for col in electorate_mesh.columns:
        print(col)
    '''

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
            get_top_languages,
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
