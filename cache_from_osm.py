import os
import geopandas as gpd
import util

"""
Read in shapefiles
Trim GeoPandas.GeoDataFrame to fit within spatial parameters
Cache a local folder, for performance
"""


# Names of data files to be cached
_datanames = ["railways", "traffic", "roads", "landuse"]


# Cache files from an OSM data source folder
def cache_from_osm(folder: str) -> None:
    if os.path.exists(folder) == False:
        raise Exception(f'"{folder}" does not exist')
    if os.path.isdir(folder) == False:
        raise Exception(f'"{folder} is not a folder')

    for name in _datanames:
        _cache_dataname(folder, name)


# Does the cache already exist
def cache_osm_exists() -> bool:
    if not os.path.exists("cache"):
        return False

    if not len(os.listdir("cache")) == 4:
        return False

    return True


# Read a GeoPandas.GeoDataFrame from cache
def read_from_cache(filename: str) -> gpd.GeoDataFrame:
    return gpd.read_file(f"cache/{filename}/data.shp")


# Cache a folder based on data name
def _cache_dataname(folder: str, dataname: str) -> None:
    source_path: str | None = None

    # The shape files may or may not include an _a, choose the appropriate file
    base_path: str = os.path.join(folder, f"gis_osm_{dataname}_free_1.shp")
    base_path_a: str = os.path.join(folder, f"gis_osm_{dataname}_a_free_1.shp")
    if os.path.exists(base_path):
        source_path = base_path
    elif os.path.exists(base_path_a):
        source_path = base_path_a
    else:
        # If cannot find the source to read from, throw an exception
        raise Exception(
            f"Cannot find file 'gis_osm_{dataname}_a_free_1.shp' or 'gis_osm_{dataname}_free_1.shp'"
        )

    # Read and trim the data
    source_df: gpd.GeoDataFrame = gpd.read_file(source_path)
    output_df: gpd.GeoDataFrame = _within_zone(source_df)

    # Create folders to cache into
    if not os.path.exists("cache"):
        os.mkdir("cache")
    if not os.path.exists(f"cache/{dataname}"):
        os.mkdir(f"cache/{dataname}")

    # Write output
    output_path: str = f"cache/{dataname}/data.shp"
    output_df.to_file(output_path)

    # Inform that the file has been cached
    util.info(f"Cached file '{dataname}'")


# Return part of dataframe within zone
def _within_zone(input: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # The longitude and latitude bounds for the lower mainland
    """
    xmin = -123.3
    xmax = -122.5
    ymin = 49.0
    ymax = 49.4
    """
    # Test bounds to run faster
    xmin = -123.145
    xmax = -123.116
    ymin = 49.271
    ymax = 49.288
    return input.cx[xmin:xmax, ymin:ymax]
