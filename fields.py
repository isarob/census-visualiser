SUMMARY_FIELDS = {

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

}

POPUP_FIELDS = {
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
}
TOOLTIP_FIELDS = {
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
}

# add a column here to generate a heatmap based on it
HEATMAP_COLUMNS = [{"G40_Tot_LT_Ste_ter_hsg_auth": "Public Housing (absolute)"},
                   {"G02_Median_tot_prsnl_inc_weekly": "Median Personal Income ($/week)"},
                   {"Pct_Renting": "Renting (%)"},
                   {"Pct_Public_Housing": "Public Housing (% of Households))"},
                   {"G13C_POL_Arabic_Tot": "Arabic Speakers (absolute)"},
                   {"G13E_POL_Vietnamese_Tot": "Vietnamese Speakers (absolute)"},
                   {"G13C_POL_CL_Canton_Tot": "Cantonese Speakers (absolute)"},
                   {"G13D_POL_CL_Tot_Tot": "Chinese Langage Speakers (absolute)"},
                   {"G13D_POL_Persian_ED_Tot": "Farsi and Persian Speakers (absolute)"},
                   {"G13D_POL_Korean_Tot": "Korean Speakers (absolute)"},
                   {"G13E_POL_Tamil_Tot": "Tamil Speakers (absolute)"},
                   {"G02_Median_age_persons": "Median Age"},

                   ]
