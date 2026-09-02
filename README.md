# census-visualiser
This is a program to generate mapping data on an electorate wide basis.

Setup.


You need the following data in the same directory as census.py:

============

Source: https://www.abs.gov.au/census/find-census-data/datapacks

This program uses SA1 level data, so ensure you have geography set to Statistical Area 1

Name: General community profile for Statistical Areas 1,       Example folder name: 2021_GCP_SA1_for_NSW_short-header

============

Source:
https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files

Name: Statistical Areas Level 1 - 2021 - Shapefile,       Example folder name: SAL_2021_AUST_GDA2020_SHP

Name: Suburbs and Localities - 2021 - Shapefile,           Example folder name: SAL_2021_AUST_GDA2020_SHP

Name: State Electoral Divisions - 2025 - Shapefile,       Example folder name: SED_2025_AUST_GDA2020

=========

Source:

https://download.openstreetmap.fr/extracts/oceania/australia/

Name: new-south-wales-latest.osm.pbf

========

Hypothetically this program will work with other state's data although I haven't tested it.


In order to not have to process all this data every time the program runs it creates a cache in /cache. You can toggle generation of the cache by changing the force_reload flag to true in load_cached_datasets (it's called at the top of __main__)