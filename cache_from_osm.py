import os
import geopandas as gpd
import util

_datanames = ["railways", "traffic", "roads", "landuse"]


# contains code to read in shapefiles and cache a trimmed version


def cache_from_osm(folder: str) -> None:
    if os.path.exists(folder) == False:
        raise Exception(f'"{folder}" does not exist')
    if os.path.isdir(folder) == False:
        raise Exception(f'"{folder} is not a folder')

    for name in _datanames:
        _cache_dataname(folder, name)


def cache_osm_exists() -> bool:
    if not os.path.exists("cache"):
        return False

    if not len(os.listdir("cache")) == 4:
        return False

    return True


def read_from_cache(filename: str) -> gpd.GeoDataFrame:
    return gpd.read_file(f"cache/{filename}/data.shp")


def _cache_dataname(folder: str, dataname: str) -> None:
    source_path: str | None = None
    base_path = os.path.join(folder, f"gis_osm_{dataname}_free_1.shp")
    base_path_a = os.path.join(folder, f"gis_osm_{dataname}_a_free_1.shp")
    if os.path.exists(base_path):
        source_path = base_path
    elif os.path.exists(base_path_a):
        source_path = base_path_a
    else:
        raise Exception(
            f"Cannot find file 'gis_osm_{dataname}_a_free_1.shp' or 'gis_osm_{dataname}_free_1.shp'"
        )
    source_df: gpd.GeoDataFrame = gpd.read_file(source_path)
    output_df: gpd.GeoDataFrame = _within_zone(source_df)

    if not os.path.exists("cache"):
        os.mkdir("cache")
    if not os.path.exists(f"cache/{dataname}"):
        os.mkdir(f"cache/{dataname}")

    output_path: str = f"cache/{dataname}/data.shp"
    output_df.to_file(output_path)
    util.info(f"Cached file '{dataname}'")


def _within_zone(input: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # the latitude and longitude bounds for the lower mainland
    """
    xmin = -123.3
    xmax = -122.5
    ymin = 49.0
    ymax = 49.4
    """
    # test bounds to run faster
    xmin = -122.935
    xmax = -122.90
    ymin = 49.27
    ymax = 49.284
    return input.cx[xmin:xmax, ymin:ymax]
