import sys

import geopandas as gpd
import pandas as pd

from calculations import electorate_summary
from config import ELECTORATES, GENERATE_HEATMAPS, MAP_DIR, HEATMAP_DIR, SA1_YEAR
from data_loader import load_cached_datasets
from fields import (
    SUMMARY_FIELDS,
    HEATMAP_COLUMNS,
    POPUP_FIELDS,
    TOOLTIP_FIELDS,
)
from maps import generate_heatmap, generate_html_map, generate_folium_heatmap
from spatial import get_electorate

if __name__ == "__main__":

    args = sys.argv[1:]

    if args:
        if args[0] not in ["all", "census"]:
            raise RuntimeError('Reload argument must be "census" or "all" (census, osm)')
    else:
        args.append("none")

    print(f"Regenerating {args[0]}")

    sa1_divisions, suburbs, sed, services = (
        load_cached_datasets(
            force_reload=args[0],
            electorates=ELECTORATES
        )
    )

    # uncomment this to list all electorate names
    # list_electorate_names(sed)
    
    for electorate in ELECTORATES:

        # Generate and print the electorate summary.
        summary = electorate_summary(
            sa1_divisions,
            sed,
            electorate,
            SUMMARY_FIELDS,
        )
        
        print("\n===== Summary =====")
        print(summary["sums"].to_csv(index=False))

        print("\n===== Language Totals =====")
        for language, amount in summary["languages"]:
            print(language + ", " + str(amount))


        print("\n===== Language Proficiency =====")
        print(summary["language_proficiency"].to_string(index=False))

        print("\n===== Nationality Totals =====")
        for nationality, amount in summary["nationalities"]:
            print(nationality + ", " + str(amount))

        print("\n===== Ancestry Totals =====")
        for ancestry, amount in summary["ancestries"]:
            print(ancestry + ", " + str(amount))

        print("\n===== Religion Totals =====")
        for religion, amount in summary["religions"]:
            print(religion + ", " + str(amount))

        print("\n===== Industry Totals =====")
        for industry, amount in summary["industries"]:
            print(industry + ", " + str(amount))


        # generate tables

        summary["sums"].to_html(
            HEATMAP_DIR / f"{electorate}_summary_table_2021.html",
            index=False
        )

        pd.DataFrame(
            summary["languages"],
            columns=["language", "amount"]
        ).to_html(
            HEATMAP_DIR / f"{electorate}_languages_table_2021.html",
            index=False
        )

        summary["language_proficiency"].to_html(
            HEATMAP_DIR / f"{electorate}_language_proficiency_table_2021.html",
            index=False
        )

        pd.DataFrame(
            summary["nationalities"],
            columns=["nationality", "amount"]
        ).to_html(
            HEATMAP_DIR / f"{electorate}_nationalities_table_2021.html",
            index=False
        )

        pd.DataFrame(
            summary["ancestries"],
            columns=["ancestry", "amount"]
        ).to_html(
            HEATMAP_DIR / f"{electorate}_ancestries_table_2021.html",
            index=False
        )

        pd.DataFrame(
            summary["religions"],
            columns=["religion", "amount"]
        ).to_html(
            HEATMAP_DIR / f"{electorate}_religions_table_2021.html",
            index=False
        )

        pd.DataFrame(
            summary["industries"],
            columns=["industry", "amount"]
        ).to_html(
            HEATMAP_DIR / f"{electorate}_industries_table_2021.html",
            index=False
        )


        # Generate heatmaps when enabled on config.py.
        if GENERATE_HEATMAPS:
            '''
            save as images
            for col in HEATMAP_COLUMNS:
                generate_folium_heatmap(
                    sa1_divisions,
                    sed,
                    electorate,
                    highlight_field=col,
                    save_chart=True,
                )
            '''

            #new heatmap method
            print("\n===== Languages heatmap =====")
            heatmap_fields = {}
            for col, label in summary["languages"][:20]:
                if("Tot_Tot" in col) or "UOLSE" in col or "Oth" in col:
                    print(f"\ndiscarding {col}")
                    continue
                heatmap_fields[col] = label

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,

                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=heatmap_fields,
                save_path=HEATMAP_DIR/f"{electorate}_languages_{SA1_YEAR}.html"
                )

            heatmap_fields = {}
            print("\n===== Nationalities heatmap =====")
            for col, label in summary["nationalities"][:8]:
                if("Tot_Tot" in col):
                    continue
                heatmap_fields[col] = label

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,

                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=heatmap_fields,
                save_path=HEATMAP_DIR/f"{electorate}_nationalities_{SA1_YEAR}.html"
                )


            heatmap_fields = {}
            print("\n===== Ancestries heatmap =====")
            for col, label in summary["ancestries"][:8]:
                if("Tot_Tot" in col):
                    continue
                heatmap_fields[col] = label

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,

                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=heatmap_fields,
                save_path=HEATMAP_DIR/f"{electorate}_ancestries_{SA1_YEAR}.html"
                )

            heatmap_fields = {}
            print("\n===== religions heatmap =====")
            for col, label in summary["religions"][:8]:
                if("Tot_P" in col):
                    continue
                heatmap_fields[col] = label

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,

                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=heatmap_fields,
                save_path=HEATMAP_DIR/f"{electorate}_religions_{SA1_YEAR}.html"
                )

            heatmap_fields = {}
            print("\n===== industries heatmap =====")
            for col, label in summary["industries"][:8]:
                if "Tot_Tot" in col or "ID_NS" in col:
                    continue
                heatmap_fields[col] = label

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,

                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=heatmap_fields,
                save_path=HEATMAP_DIR/f"{electorate}_industries_{SA1_YEAR}.html"
                )

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,
                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=TOOLTIP_FIELDS,
                save_path=HEATMAP_DIR/f"{electorate}_summary_{SA1_YEAR}.html"
                )

            print("\n===== services heatmap =====")
            electorate_gdf = get_electorate(
                sed,
                electorate
            )

            electorate_gdf = electorate_gdf.to_crs(
                services.crs
            )

            services_df = gpd.clip(
                services,
                electorate_gdf
                )

            generate_html_map(
                sa1_divisions,
                sed,
                electorate,
                popup_fields=POPUP_FIELDS,

                tooltip_fields=TOOLTIP_FIELDS,
                heatmap_fields=TOOLTIP_FIELDS,
                save_path=HEATMAP_DIR/f"{electorate}_services_{SA1_YEAR}.html",
                services_df=services_df,
                )

    # get the services for the electorates we're looking at
    services_dfs = []

    for electorate in ELECTORATES:
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

    # create interactable map
    generate_html_map(
        sa1_divisions,
        sed,
        ELECTORATES,
        popup_fields=POPUP_FIELDS,

        tooltip_fields=TOOLTIP_FIELDS,
        heatmap_fields=TOOLTIP_FIELDS,

        services_df=services_df

    )
