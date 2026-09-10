# GCP table definitions by Census year.
# Add another Census year here when support is needed.
#
# Each logical table name maps to a list of physical GCP table IDs.
#
# Some GCP tables are split across multiple CSV files. For example:
#   2021 G09 -> G09A-G09H
#   2021 G13 -> G13A-G13E
#   2016 G44 -> G44A-G44F
#
# The values below correspond to the physical files supplied by the ABS
# in the NSW SA1 short-header GCP DataPacks.
GCP_TABLES = {
    2016: {
        # General / demographic
        "selected_person_characteristics_by_sex": ["G01"],
        "selected_medians_and_averages": ["G02"],
        "place_of_usual_residence_by_place_of_enumeration_on_census_night_by_age": ["G03"],
        "age_by_sex": ["G04A", "G04B"],
        "registered_marital_status_by_age_by_sex": ["G05"],
        "social_marital_status_by_age_by_sex": ["G06"],
        "indigenous_status_by_age_by_sex": ["G07"],

        # Ancestry / birthplace / language / religion
        "ancestry_by_country_of_birth_of_parents": ["G08"],
        "country_of_birth_of_person_by_age_by_sex": [
            "G09A",
            "G09B",
            "G09C",
            "G09D",
            "G09E",
            "G09F",
            "G09G",
            "G09H",
        ],
        "country_of_birth_of_person_by_year_of_arrival_in_australia": [
            "G10A",
            "G10B",
            "G10C",
        ],
        "proficiency_in_spoken_english_language_by_year_of_arrival_in_australia_by_age": [
            "G11A",
            "G11B",
            "G11C",
            "G11D",
        ],
        "proficiency_in_spoken_english_language_of_parents_by_age_of_dependent_children": [
            "G12A",
            "G12B",
        ],
        "language_used_at_home_by_proficiency_in_spoken_english_by_sex": [
            "G13A",
            "G13B",
            "G13C",
            "G13D",
        ],
        "religious_affiliation_by_sex": ["G14"],

        # Education / income
        "type_of_educational_institution_attending_by_full_part_time_student_status_by_age_by_sex": [
            "G15"
        ],
        "highest_year_of_school_completed_by_age_by_sex": [
            "G16A",
            "G16B",
        ],
        "total_personal_income_weekly_by_age_by_sex": [
            "G17A",
            "G17B",
            "G17C",
        ],

        # Personal / unpaid work
        "core_activity_need_for_assistance_by_age_by_sex": ["G18"],
        "voluntary_work_for_an_organisation_or_group_by_age_by_sex": ["G19"],
        "unpaid_domestic_work_number_of_hours_by_age_by_sex": [
            "G20A",
            "G20B",
        ],
        "unpaid_assistance_to_a_person_with_a_disability_by_age_by_sex": ["G21"],
        "unpaid_child_care_by_age_by_sex": [
            "G22A",
            "G22B",
        ],

        # Household / family
        "relationship_in_household_by_age_by_sex": [
            "G23A",
            "G23B",
        ],
        "number_of_children_ever_born_by_age_of_parent": ["G24"],
        "family_composition": ["G25"],
        "family_composition_and_country_of_birth_of_father_and_or_mother_by_age_of_dependent_children": [
            "G26"
        ],
        "family_blending": ["G27"],
        "total_family_income_weekly_by_family_composition": ["G28"],
        "total_household_income_weekly_by_household_composition": ["G29"],
        "number_of_motor_vehicles_by_dwellings": ["G30"],
        "household_composition_by_number_of_persons_usually_resident": ["G31"],

        # Dwelling / housing
        "dwelling_structure": ["G32"],
        "tenure_and_landlord_type_by_dwelling_structure": ["G33"],
        "mortgage_repayment_monthly_by_dwelling_structure": ["G34"],
        "mortgage_repayment_monthly_by_family_composition": ["G35"],
        "rent_weekly_by_landlord_type": ["G36"],
        "internet_access_by_dwelling_structure": ["G37"],
        "dwelling_structure_by_number_of_bedrooms": ["G38"],
        "dwelling_structure_by_household_composition_and_family_composition": [
            "G39"
        ],

        # Labour force / education / migration
        "selected_labour_force_education_and_migration_characteristics_by_sex": [
            "G40"
        ],
        "place_of_usual_residence_1_year_ago_by_sex": ["G41"],
        "place_of_usual_residence_5_years_ago_by_sex": ["G42"],
        "labour_force_status_by_age_by_sex": [
            "G43A",
            "G43B",
        ],
        "labour_force_status_by_sex_of_parents_by_age_of_dependent_children_for_couple_families": [
            "G44A",
            "G44B",
            "G44C",
            "G44D",
            "G44E",
            "G44F",
        ],
        "labour_force_status_by_sex_of_parent_by_age_of_dependent_children_for_one_parent_families": [
            "G45A",
            "G45B",
        ],
        "highest_non_school_qualification_level_of_education_by_age_by_sex": [
            "G46A",
            "G46B",
        ],
        "highest_non_school_qualification_field_of_study_by_age_by_sex": [
            "G47A",
            "G47B",
            "G47C",
        ],
        "highest_non_school_qualification_field_of_study_by_occupation_by_sex": [
            "G48A",
            "G48B",
            "G48C",
        ],
        "highest_non_school_qualification_level_of_education_by_occupation_by_sex": [
            "G49A",
            "G49B",
            "G49C",
        ],
        "highest_non_school_qualification_level_of_education_by_industry_of_employment_by_sex": [
            "G50A",
            "G50B",
            "G50C",
        ],

        # Employment
        "industry_of_employment_by_age_by_sex": [
            "G51A",
            "G51B",
            "G51C",
            "G51D",
        ],
        "industry_of_employment_by_hours_worked_by_sex": [
            "G52A",
            "G52B",
            "G52C",
            "G52D",
        ],
        "industry_of_employment_by_occupation": [
            "G53A",
            "G53B",
        ],
        "total_family_income_weekly_by_labour_force_status_of_partners_for_couple_families_with_no_children": [
            "G54A",
            "G54B",
        ],
        "total_family_income_weekly_by_labour_force_status_of_parents_partners_for_couple_families_with_children": [
            "G55A",
            "G55B",
        ],
        "total_family_income_weekly_by_labour_force_status_of_parent_for_one_parent_families": [
            "G56A",
            "G56B",
        ],
        "occupation_by_age_by_sex": [
            "G57A",
            "G57B",
        ],
        "occupation_by_hours_worked_by_sex": [
            "G58A",
            "G58B",
        ],
        "method_of_travel_to_work_by_sex": ["G59"],
    },

    2021: {
        # General / demographic
        "selected_person_characteristics_by_sex": ["G01"],
        "selected_medians_and_averages": ["G02"],
        "place_of_usual_residence_by_place_of_enumeration_on_census_night_by_age": [
            "G03"
        ],
        "age_by_sex": [
            "G04A",
            "G04B",
        ],
        "registered_marital_status_by_age_by_sex": ["G05"],
        "social_marital_status_by_age_by_sex": ["G06"],
        "indigenous_status_by_age_by_sex": ["G07"],

        # Ancestry / birthplace / language / religion
        "ancestry_by_country_of_birth_of_parents": ["G08"],
        "country_of_birth_of_person_by_age_by_sex": [
            "G09A",
            "G09B",
            "G09C",
            "G09D",
            "G09E",
            "G09F",
            "G09G",
            "G09H",
        ],
        "country_of_birth_of_person_by_year_of_arrival_in_australia": [
            "G10A",
            "G10B",
            "G10C",
        ],
        "proficiency_in_spoken_english_by_year_of_arrival_in_australia_by_age": [
            "G11A",
            "G11B",
            "G11C",
            "G11D",
        ],
        "proficiency_in_spoken_english_of_parents_by_age_of_dependent_children": [
            "G12A",
            "G12B",
        ],
        "language_used_at_home_by_proficiency_in_spoken_english_by_sex": [
            "G13A",
            "G13B",
            "G13C",
            "G13D",
            "G13E",
        ],
        "religious_affiliation_by_sex": ["G14"],

        # Education / income
        "type_of_education_institution_attending_by_full_part_time_student_status_by_age_by_sex": [
            "G15"
        ],
        "highest_year_of_school_completed_by_age_by_sex": [
            "G16A",
            "G16B",
        ],
        "total_personal_income_weekly_by_age_by_sex": [
            "G17A",
            "G17B",
            "G17C",
        ],

        # Health / disability
        "core_activity_need_for_assistance_by_age_by_sex": ["G18"],
        "type_of_long_term_health_condition_by_age_by_sex": [
            "G19A",
            "G19B",
            "G19C",
        ],
        "count_of_selected_long_term_health_conditions_by_age_by_sex": [
            "G20A",
            "G20B",
        ],
        "type_of_long_term_health_condition_by_selected_person_characteristics": [
            "G21A",
            "G21B",
            "G21C",
        ],

        # Other personal characteristics
        "australian_defence_force_service_by_age_by_sex": ["G22"],
        "voluntary_work_for_an_organisation_or_group_by_age_by_sex": ["G23"],
        "unpaid_domestic_work_number_of_hours_by_age_by_sex": ["G24A", "G24B"],
        "unpaid_assistance_to_a_person_with_a_disability_health_condition_or_due_to_old_age_by_age_by_sex": [
            "G25"
        ],
        "unpaid_child_care_by_age_by_sex": ["G26A", "G26B"],

        # Household / family
        "relationship_in_household_by_age_by_sex": ["G27A"],
        "number_of_children_ever_born": ["G28"],
        "family_composition": ["G29"],
        "family_composition_and_country_of_birth_of_parents_by_age_of_dependent_children": [
            "G30"
        ],
        "family_blending": ["G31"],
        "total_family_income_weekly_by_family_composition": ["G32"],
        "total_household_income_weekly_by_household_composition": ["G33"],
        "number_of_motor_vehicles_by_dwellings": ["G34"],
        "household_composition_by_number_of_persons_usually_resident": ["G35"],

        # Dwelling / housing
        "dwelling_structure": ["G36"],
        "tenure_and_landlord_type_by_dwelling_structure": ["G37"],
        "mortgage_repayment_monthly_by_dwelling_structure": ["G38"],
        "mortgage_repayment_monthly_by_family_composition": ["G39"],
        "rent_weekly_by_landlord_type": ["G40"],
        "dwelling_structure_by_number_of_bedrooms": ["G41"],
        "dwelling_structure_by_household_composition_and_family_composition": [
            "G42"
        ],

        # Labour force / education / migration
        "selected_labour_force_education_and_migration_characteristics_by_sex": [
            "G43"
        ],
        "place_of_usual_residence_1_year_ago_by_sex": ["G44"],
        "place_of_usual_residence_5_years_ago_by_sex": ["G45"],
        "labour_force_status_by_age_by_sex": [
            "G46A",
            "G46B",
        ],
        "labour_force_status_by_sex_of_parents_by_age_of_dependent_children_for_couple_families": [
            "G47A",
            "G47B",
            "G47C",
            "G47D",
            "G47E",
            "G47F",
        ],
        "labour_force_status_by_sex_of_parent_by_age_of_dependent_children_for_one_parent_families": [
            "G48A",
            "G48B",
        ],
        "highest_non_school_qualification_level_of_education_by_age_by_sex": [
            "G49A",
            "G49B",
        ],
        "highest_non_school_qualification_field_of_study_by_age_by_sex": [
            "G50A",
            "G50B",
            "G50C",
        ],
        "highest_non_school_qualification_field_of_study_by_occupation_by_sex": [
            "G51A",
            "G51B",
            "G51C",
        ],
        "highest_non_school_qualification_level_of_education_by_occupation_by_sex": [
            "G52A",
            "G52B",
            "G52C",
        ],
        "highest_non_school_qualification_level_of_education_by_industry_of_employment_by_sex": [
            "G53A",
            "G53B",
            "G53C",
        ],

        # Employment
        "industry_of_employment_by_age_by_sex": [
            "G54A",
            "G54B",
            "G54C",
            "G54D",
        ],
        "industry_of_employment_by_hours_worked_by_sex": [
            "G55A",
            "G55B",
            "G55C",
            "G55D",
        ],
        "industry_of_employment_by_occupation": [
            "G56A",
            "G56B",
        ],
        "total_family_income_weekly_by_labour_force_status_of_partners_for_couple_families_with_no_children": [
            "G57A",
            "G57B",
        ],
        "total_family_income_weekly_by_labour_force_status_of_parents_partners_for_couple_families_with_children": [
            "G58A",
            "G58B",
        ],
        "total_family_income_weekly_by_labour_force_status_of_parent_for_one_parent_families": [
            "G59A",
            "G59B",
        ],
        "occupation_by_age_by_sex": [
            "G60A",
            "G60B",
        ],
        "occupation_by_hours_worked_by_sex": [
            "G61A",
            "G61B",
        ],
        "method_of_travel_to_work_by_sex": ["G62"],
    },
}
GCP_COLUMNS = {
    2016: {
        # ----------------------------------------------------------
        # Housing
        # ----------------------------------------------------------

        "total_rentals":
            "G36_Tot_Tot",

        "rent_via_real_estate_agent":
            "G36_Tot_LT_Real_eSte_agent",

        "rent_via_private_landlord":
            "G36_Tot_LT_Psn_not_Sme_hhd",

        "state_housing_authority":
            "G36_Tot_LT_Ste_ter_hsg_auth",

        "community_housing_provider":
            "G36_Tot_LT_hs_coop_com_ch_g",

        "total_households":
            "G38_Total_Total",

        "apartments":
            "G38_Flt_apart_Tot_Total",

        "separate_houses":
            "G38_Separate_house_Total",

        "average_household_size":
            "G02_Average_household_size",

        # ----------------------------------------------------------
        # Labour force / employment
        # ----------------------------------------------------------

        "total_employed":
            "G43B_P_Tot_Emp_Tot",

        "total_labour_force":
            "G43B_P_Tot_LF_Tot",

        # ----------------------------------------------------------
        # Occupation
        # ----------------------------------------------------------

        "managers":
            "G57B_P_Tot_Managers",

        "professionals":
            "G57B_P_Tot_Professionals",

        "technicians_and_trades":
            "G57B_P_Tot_TechnicTrades_W",

        "community_and_personal_service":
            "G57B_P_Tot_CommunPersnlSvc_W",

        "clerical_and_administrative":
            "G57B_P_Tot_ClericalAdminis_W",

        "sales":
            "G57B_P_Tot_Sales_W",

        "machinery_operators_and_drivers":
            "G57B_P_Tot_Mach_oper_drivers",

        "labourers":
            "G57B_P_Tot_Labourers",

        "occupation_not_stated":
            "G57B_P_Tot_Occu_ID_NS",

        # ----------------------------------------------------------
        # Hours worked
        # ----------------------------------------------------------

        "worked_0_hours":
            "G58B_P_Tot_0",

        "worked_1_19_hours":
            "G58B_P_Tot_1_19",

        "worked_20_29_hours":
            "G58B_P_Tot_20_29",

        "worked_30_34_hours":
            "G58B_P_Tot_30_34",

        "worked_35_39_hours":
            "G58B_P_Tot_35_39",

        "worked_40_44_hours":
            "G58B_P_Tot_40_44",

        "worked_45_49_hours":
            "G58B_P_Tot_45_49",

        "worked_50_plus_hours":
            "G58B_P_Tot_50_over",

        "hours_worked_not_stated":
            "G58B_P_Tot_hours_NS",

        # ----------------------------------------------------------
        # Census summary statistics
        # ----------------------------------------------------------

        "median_age":
            "G02_Median_age_persons",

        "median_personal_income":
            "G02_Median_tot_prsnl_inc_weekly",

        "median_household_income":
            "G02_Median_tot_hhd_inc_weekly",

        "median_family_income":
            "G02_Median_tot_fam_inc_weekly",

        "median_rent":
            "G02_Median_rent_weekly",

        "median_mortgage_repayment":
            "G02_Median_mortgage_repay_monthly",

        # ----------------------------------------------------------
        # Other
        # ----------------------------------------------------------

        "australian_citizen":
            "Australian_citizen_P",

        # ----------------------------------------------------------
        # Language
        #
        # The raw 2016 G13C/G13D files contain columns such as
        # POL_Arabic_Tot. The data loader prefixes these columns
        # with the physical table name, so the resulting DataFrame
        # columns are prefixed with G13C_ or G13D_ as appropriate.
        # ----------------------------------------------------------
        "english_only_at_home":
            "Lang_spoken_home_Eng_only_P",

        "other_language_at_home":
            "Lang_spoken_home_Oth_Lang_P",

        "arabic_speakers":
            "G13C_POL_Arabic_Tot",

        "korean_speakers":
            "G13D_POL_Korean_Tot",

        "cantonese_speakers":
            "G13C_POL_CL_Cantones_Tot",

        "chinese_language_speakers":
            "G13C_POL_CL_Tot_Tot",

        "farsi_persian_speakers":
            "G13D_POL_Persian_ED_Tot",

        "tamil_speakers":
            "G13D_POL_Tamil_Tot",

        "vietnamese_speakers":
            "G13D_POL_Vietnamese_Tot",
    },

    2021: {
        # ----------------------------------------------------------
        # Housing
        # ----------------------------------------------------------

        "total_rentals":
            "G40_Tot_Tot",

        "rent_via_real_estate_agent":
            "G40_Tot_LT_Real_eSte_agent",

        "rent_via_private_landlord":
            "G40_Tot_LT_Psn_not_Sme_hhd",

        "state_housing_authority":
            "G40_Tot_LT_Ste_ter_hsg_auth",

        "community_housing_provider":
            "G40_Tot_LT_com_hou_pro",

        "total_households":
            "G41_Total_Total",

        "apartments":
            "G41_Flt_apart_Tot_Total",

        "separate_houses":
            "G41_Separate_house_Total",

        "average_household_size":
            "G02_Average_household_size",

        # ----------------------------------------------------------
        # Labour force / employment
        # ----------------------------------------------------------

        "total_employed":
            "G46B_P_Tot_Emp_Tot",

        "total_labour_force":
            "G46B_P_Tot_LF_Tot",

        # ----------------------------------------------------------
        # Occupation
        # ----------------------------------------------------------

        "managers":
            "G60B_P_Tot_Managers",

        "professionals":
            "G60B_P_Tot_Professionals",

        "technicians_and_trades":
            "G60B_P_Tot_TechnicTrades_W",

        "community_and_personal_service":
            "G60B_P_Tot_CommunPersnlSvc_W",

        "clerical_and_administrative":
            "G60B_P_Tot_ClericalAdminis_W",

        "sales":
            "G60B_P_Tot_Sales_W",

        "machinery_operators_and_drivers":
            "G60B_P_Tot_Mach_oper_drivers",

        "labourers":
            "G60B_P_Tot_Labourers",

        "occupation_not_stated":
            "G60B_P_Tot_Occu_ID_NS",

        # ----------------------------------------------------------
        # Hours worked
        # ----------------------------------------------------------

        "worked_0_hours":
            "G61B_P_Tot_0",

        "worked_1_19_hours":
            "G61B_P_Tot_1_19",

        "worked_20_29_hours":
            "G61B_P_Tot_20_29",

        "worked_30_34_hours":
            "G61B_P_Tot_30_34",

        "worked_35_39_hours":
            "G61B_P_Tot_35_39",

        "worked_40_44_hours":
            "G61B_P_Tot_40_44",

        "worked_45_49_hours":
            "G61B_P_Tot_45_49",

        "worked_50_plus_hours":
            "G61B_P_Tot_50_over",

        "hours_worked_not_stated":
            "G61B_P_Tot_hours_NS",

        # ----------------------------------------------------------
        # Census summary statistics
        # ----------------------------------------------------------

        "median_age":
            "G02_Median_age_persons",

        "median_personal_income":
            "G02_Median_tot_prsnl_inc_weekly",

        "median_household_income":
            "G02_Median_tot_hhd_inc_weekly",

        "median_family_income":
            "G02_Median_tot_fam_inc_weekly",

        "median_rent":
            "G02_Median_rent_weekly",

        "median_mortgage_repayment":
            "G02_Median_mortgage_repay_monthly",

        # ----------------------------------------------------------
        # Other
        # ----------------------------------------------------------

        "australian_citizen":
            "Australian_citizen_P",

        # ----------------------------------------------------------
        # Language
        # ----------------------------------------------------------

        "english_only_at_home":
            "Lang_used_home_Eng_only_P",

        "other_language_at_home":
            "Lang_used_home_Oth_Lang_P",

        "arabic_speakers":
            "G13C_POL_Arabic_Tot",

        "korean_speakers":
            "G13D_POL_Korean_Tot",

        "cantonese_speakers":
            "G13C_POL_CL_Canton_Tot",

        "chinese_language_speakers":
            "G13D_POL_CL_Tot_Tot",

        "farsi_persian_speakers":
            "G13D_POL_Persian_ED_Tot",

        "tamil_speakers":
            "G13E_POL_Tamil_Tot",

        "vietnamese_speakers":
            "G13E_POL_Vietnamese_Tot",
    },
}
