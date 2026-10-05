from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Input/source data.
DATA_DIR = PROJECT_DIR / "data"

# Cached/generated intermediate data.
CACHE_DIR = PROJECT_DIR / "cache"

# Generated output.
OUTPUT_DIR = PROJECT_DIR / "output"
HEATMAP_DIR = OUTPUT_DIR / "heatmaps"
MAP_DIR = OUTPUT_DIR / "maps"

# Toggle heatmap generation.
GENERATE_HEATMAPS = True

SA1_YEAR = 2021
CARTO_API_KEY = "cb1_296x_1_e8d7efe65c17bb102d553727"
CARTO_TILES = (
    "https://basemaps.cartocdn.com/rastertiles/"
    "voyager/{z}/{x}/{y}.png"
    f"?key={CARTO_API_KEY}"
)

GEOGRAPHY_COLUMNS = {
    2016: {
        "suburb_code": "SSC_CODE",
        "suburb_name": "SSC_NAME",
        "sa2_name": "SA2_NAME16",
    },

    2021: {
        "suburb_code": "SAL_CODE21",
        "suburb_name": "SAL_NAME21",
        "sa2_name": "SA2_NAME21",
    },
}

CARTO_ATTRIBUTION = "© OpenStreetMap contributors, © CARTO"

ELECTORATES = [
    "Auburn",
    "Granville",
    "Summer Hill",
    "Newtown",
    "Wollongong",
    "Wallsend",
]

'''

'''

POI_FILTER = {
    "amenity": [
        "hospital",
        "clinic",
        "doctors",
        "school",
        "childcare",
        "kindergarten",
        "community_centre",
        "library",
        "place_of_worship",
    ],

    "healthcare": [
        "hospital",
        "clinic",
        "doctor",
        "physiotherapist",
        "rehabilitation",
        "centre",
    ],

    "shop": [
        "mall",
    ],

    "leisure": [
        "sports_centre",
        "stadium",
    ],

    "social_facility": True,
}


