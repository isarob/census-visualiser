from config import SA1_YEAR, GEOGRAPHY_COLUMNS
from field_definitions import GCP_TABLES, GCP_COLUMNS


def get_summary_fields(get_gcp_column):
    return {
        # Population
        "Tot_P_P": "Population",
        "Australian_citizen_P": "Australian Citizens",

        # Census summaries
        get_gcp_column("median_age"): "Median Age",
        get_gcp_column("median_personal_income"):
            "Median Personal Income ($/week)",
        get_gcp_column("median_household_income"):
            "Median Household Income ($/week)",
        get_gcp_column("median_family_income"):
            "Median Family Income ($/week)",
        get_gcp_column("median_rent"):
            "Median Rent ($/week)",
        get_gcp_column("median_mortgage_repayment"):
            "Median Mortgage Repayment ($/month)",

        # Diversity
        get_gcp_column("english_only_at_home"):
            "English Only at Home",

        get_gcp_column("other_language_at_home"):
            "Other Language at Home",


        # Landlord type
        get_gcp_column("rent_via_real_estate_agent"):
            "Rentals via Real Estate Agent",
        get_gcp_column("rent_via_private_landlord"):
            "Rentals via Private Landlord",
        get_gcp_column("state_housing_authority"):
            "State/Territory Housing Authority",
        get_gcp_column("community_housing_provider"):
            "Community Housing Provider",
        get_gcp_column("total_rentals"):
            "Total Rentals",


        # Households
        get_gcp_column("total_households"):
            "Total Households",
        get_gcp_column("apartments"):
            "Total Apartments",

        get_gcp_column("average_household_size"):
            "Average Household Size",

        # Hours worked
        get_gcp_column("worked_0_hours"):
            "Worked 0 Hours",
        get_gcp_column("worked_1_19_hours"):
            "Worked 1–19 Hours",
        get_gcp_column("worked_20_29_hours"):
            "Worked 20–29 Hours",
        get_gcp_column("worked_30_34_hours"):
            "Worked 30–34 Hours",
        get_gcp_column("worked_35_39_hours"):
            "Worked 35–39 Hours",
        get_gcp_column("worked_40_44_hours"):
            "Worked 40–44 Hours",
        get_gcp_column("worked_45_49_hours"):
            "Worked 45–49 Hours",
        get_gcp_column("worked_50_plus_hours"):
            "Worked 50+ Hours",
        get_gcp_column("hours_worked_not_stated"):
            "Hours Worked Not Stated",
    }

def get_popup_fields(get_gcp_column):
    return {
        # Geography
        "SA1_CODE": "SA1 Code",
        get_geography_column("sa2_name"): "SA2",

        # Population
        "Tot_P_P": "Population",
        "Australian_citizen_P": "Australian Citizens",

        # Census summaries
        get_gcp_column("median_age"): "Median Age",
        get_gcp_column("median_personal_income"):
            "Median Personal Income ($/week)",
        get_gcp_column("median_household_income"):
            "Median Household Income ($/week)",
        get_gcp_column("median_family_income"):
            "Median Family Income ($/week)",
        get_gcp_column("median_rent"):
            "Median Rent ($/week)",
        get_gcp_column("median_mortgage_repayment"):
            "Median Mortgage Repayment ($/month)",

        # Diversity
        get_gcp_column("english_only_at_home"):
            "English Only at Home",

        get_gcp_column("other_language_at_home"):
            "Other Language at Home",
        "Top Languages": "Top Languages",

        # Housing
        "Pct_Renting": "Renting (%)",
        "Pct_Apartments": "Apartments (%)",

        # Landlord type
        get_gcp_column("rent_via_real_estate_agent"):
            "Rentals via Real Estate Agent",
        get_gcp_column("rent_via_private_landlord"):
            "Rentals via Private Landlord",
        get_gcp_column("state_housing_authority"):
            "State/Territory Housing Authority",
        get_gcp_column("community_housing_provider"):
            "Community Housing Provider",

        # Households
        get_gcp_column("total_households"):
            "Total Households",
        get_gcp_column("average_household_size"):
            "Average Household Size",

        # Employment
        "employment_rate": "Employment Rate (%)",
    }

def get_tooltip_fields(get_gcp_column):
    return {
        "Tot_P_P": "Population",
        get_gcp_column("total_households"):
            "Total Households",
        get_gcp_column("median_age")    :
            "Median Age",
        get_gcp_column("median_personal_income"):
            "Median Personal Income ($/week)",
        "Pct_Renting": "Renting (%)",
        get_gcp_column("median_rent"):
            "Median Rent ($/week)",
        "Pct_Apartments": "Apartments (%)",

        # Language
        get_gcp_column("english_only_at_home"):
            "English Only at Home",
        get_gcp_column("other_language_at_home"):
            "Other Language at Home",

        "Top Languages": "Top Languages",
    }

def get_heatmap_columns(get_gcp_column):
    return [
        {
            get_gcp_column("state_housing_authority"):
                "Public Housing (absolute)"
        },
        {
            get_gcp_column("median_personal_income"):
                "Median Personal Income ($/week)"
        },
        {
            "Pct_Renting":
                "Renting (%)"
        },
        {
            "Pct_Public_Housing":
                "Public Housing (% of Households)"
        },

        # Language-specific fields
        {
            get_gcp_column("arabic_speakers"):
                "Arabic Speakers (absolute)"
        },
        {
            get_gcp_column("vietnamese_speakers"):
                "Vietnamese Speakers (absolute)"
        },
        {
            get_gcp_column("cantonese_speakers"):
                "Cantonese Speakers (absolute)"
        },
        {
            get_gcp_column("chinese_language_speakers"):
                "Chinese Language Speakers (absolute)"
        },
        {
            get_gcp_column("farsi_persian_speakers"):
                "Farsi and Persian Speakers (absolute)"
        },
        {
            get_gcp_column("korean_speakers"):
                "Korean Speakers (absolute)"
        },
        {
            get_gcp_column("tamil_speakers"):
                "Tamil Speakers (absolute)"
        },

        {
            get_gcp_column("median_age"):
                "Median Age"
        },
    ]


def get_gcp_column(column_name):
    """
    Return the physical GCP column name for the current SA1_YEAR.

    Check the GCP_COLUMNS dictionary in config.py for the names of
    available logical GCP columns and their corresponding physical
    Census-year-specific column names.
    """

    # Check that the requested Census year is supported.
    if SA1_YEAR not in GCP_COLUMNS:
        raise ValueError(
            f"Unsupported Census year: {SA1_YEAR}"
        )

    # Check that the requested logical column exists.
    if column_name not in GCP_COLUMNS[SA1_YEAR]:
        raise ValueError(
            f"Unknown GCP column '{column_name}' "
            f"for Census {SA1_YEAR}"
        )

    return GCP_COLUMNS[SA1_YEAR][column_name]

def get_geography_column(column_name):
    """
    Return the physical geography column name for the current SA1_YEAR.

    Check the GEOGRAPHY_COLUMNS dictionary in config.py for the names
    of the year-specific geography fields.
    """

    # Check that the requested Census year is supported.
    if SA1_YEAR not in GEOGRAPHY_COLUMNS:
        raise ValueError(
            f"Unsupported Census year: {SA1_YEAR}"
        )

    # Check that the requested logical column exists.
    if column_name not in GEOGRAPHY_COLUMNS[SA1_YEAR]:
        raise ValueError(
            f"Unknown geography column '{column_name}' "
            f"for Census {SA1_YEAR}"
        )

    return GEOGRAPHY_COLUMNS[SA1_YEAR][column_name]


def get_gcp_table_id(table_name=None, suffix=None):
    """
        Return the GCP table ID or base ID for a logical table name,
        based on the current SA1_YEAR.

        Check the GCP_TABLES dictionary in config.py for the names of
        available Census statistics.

        Some GCP tables are split across multiple physical CSV files,
        identified by letter suffixes such as G09A, G09B, G09C, etc.
        When no suffix is provided, the base table ID is returned so that
        the data loader can automatically match all physical files belonging
        to that table. A suffix can be provided to request a specific
        physical file.

        Examples
        --------
        G01 -> "G01"
        G13A-G13E -> "G13"
        get_gcp_table_id("...", suffix="A") -> "G13A"

        Parameters
        ----------
        table_name : str
            Logical name of the GCP table.
        suffix : str, optional
            Letter suffix of a specific physical GCP file.

        Returns
        -------
        str
            GCP table ID or base table ID.

        Raises
        ------
        ValueError
            If the Census year, table name, or suffix is unsupported.
        """

    # Check that the requested Census year is supported.
    if SA1_YEAR not in GCP_TABLES:
        raise ValueError(
            f"Unsupported Census year: {SA1_YEAR}"
        )

    # Check that the requested table exists.
    if table_name not in GCP_TABLES[SA1_YEAR]:
        raise ValueError(
            f"Unknown GCP table '{table_name}' "
            f"for Census {SA1_YEAR}"
        )

    # Get all physical table IDs associated with the logical table.
    table_ids = GCP_TABLES[SA1_YEAR][table_name]

    # No suffix requested:
    # Return the base table ID.
    #
    # For example:
    # ["G13A", "G13B", "G13C", "G13D", "G13E"] -> "G13"
    #
    # The glob in load_cached_datasets() will then find all of the
    # physical files beginning with G13.

    if suffix is None:
        if len(table_ids) == 1:
            return table_ids[0]

        # Remove the final character (the suffix) from each
        # physical table ID and ensure they all share the same base.
        base_ids = {
            table_id[:-1]
            for table_id in table_ids
        }

        if len(base_ids) != 1:
            print(f"\nLoading table: {base_ids.pop()}")
            raise ValueError(
                f"Could not determine a common base ID for "
                f"GCP table '{table_name}': "
                f"{', '.join(table_ids)}"
            )

        # Return the common base table ID.
        return base_ids.pop()

    # --------------------------------------------------------------
    # Suffix requested:
    # Return the specific physical table ID.
    # --------------------------------------------------------------

    suffix = suffix.upper()

    for table_id in table_ids:
        if table_id.endswith(suffix):
            return table_id

    raise ValueError(
        f"Unknown suffix '{suffix}' for table '{table_name}'. "
        f"Available suffixes: "
        f"{', '.join(table_id[-1] for table_id in table_ids)}"
    )


SUMMARY_FIELDS = get_summary_fields(get_gcp_column)
POPUP_FIELDS = get_popup_fields(get_gcp_column)
TOOLTIP_FIELDS = get_tooltip_fields(get_gcp_column)
HEATMAP_COLUMNS = get_heatmap_columns(get_gcp_column)


