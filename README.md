# census-visualiser
This is a program to generate mapping data on an electorate wide basis.


##Setup.


You need the following data in the same directory as census.py:

============

Source: https://www.abs.gov.au/census/find-census-data/datapacks

This program uses SA1 level data, so ensure you have geography set to Statistical Area 1

Name: General community profile for Statistical Areas 1,       Example folder name: 2021_GCP_SA1_for_NSW_short-header

=============

Source: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files

Name: Statistical Areas Level 1 - 2021 - Shapefile,       Example folder name: SA1_2021_AUST_SHP_GDA94

Name: Suburbs and Localities - 2021 - Shapefile,           Example folder name: SAL_2021_AUST_GDA2020_SHP

Name: State Electoral Divisions - 2025 - Shapefile,       Example folder name: SED_2025_AUST_GDA2020

===========

Source: https://download.openstreetmap.fr/extracts/oceania/australia/

Name: new-south-wales-latest.osm.pbf

============

So your folder should have:

census.py

new-south-wales-latest.osm.pbf

SED_2025_AUST_GDA2020/

SAL_2021_AUST_GDA2020_SHP/

SA1_2021_AUST_SHP_GDA94/

2021_GCP_SA1_for_NSW_short-header/



Hypothetically this program will work with other states' data although I haven't tested it.


Once you have all the data in the folder run census.py. It will take quite a long time to load in all the data (~5mins on my machine)


###python3 census.py


In order to not have to process all this data every time the program runs it creates a cache in /cache. You can toggle generation of the cache by using arguments:

###python3 census.py all

Reloads census and open streetmap cache. Useful when updating all datasets

### python3 census.py census

Only reloads census cache. Useful when making changes to which census tables you are working with.


##Functions

###calculate_extra_columns

Adds extra variables to sa1 data such as Percentages, Feasability etc. If you want to calculate new variables this is the place to do it. Adds them to all maps, summaries etc.

###electorate_summary

Creates a summary of a total electorate and prints it to the command line.

note: This function adds up all sa1 divisions. Where the variable is a median (eg median income), it takes the mean of all the medians, and is probably not statistically useful

###generate_heatmap

Creates a heatmap of an electoral division for some census variable.

###generate_html_map

Creates an interactable html map of one or more electoral divisions



##Data




Auburn electorate:

2016 public housing households: 1626
2016 total housholds: 29348
2016 public housing percent: 5.5%

2021 public housing households: 1569
2021 total housholds: 32198
2021 public housing percent: 4.9%

Assuming public housing has continued to decrease at the same rate, it is now only 4.2% of housing stock in Auburn

