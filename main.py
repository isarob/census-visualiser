import sys

import geopandas as gpd
import pandas as pd

from calculations import electorate_summary
from config import ELECTORATES, GENERATE_HEATMAPS
from data_loader import load_cached_datasets
from fields import (
    SUMMARY_FIELDS,
    HEATMAP_COLUMNS,
    POPUP_FIELDS,
    TOOLTIP_FIELDS,
)
from maps import generate_heatmap, generate_html_map
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

        # Generate heatmaps when enabled on config.py.
        if GENERATE_HEATMAPS:
            for col in HEATMAP_COLUMNS:
                generate_heatmap(
                    sa1_divisions,
                    sed,
                    electorate,
                    highlight_field=col,
                    save_chart=True,
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
        colour_column='Feasibility',
        popup_fields=POPUP_FIELDS,

        tooltip_fields=TOOLTIP_FIELDS,

        services_df=services_df

    )
