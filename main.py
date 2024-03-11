from sys import argv
import dbf
import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

pd.options.display.max_rows = 5000


def get_features(folder: str):
    if os.path.exists(folder) == False:
        raise Exception(f'"{folder}" does not exist')
    if os.path.isdir(folder) == False:
        raise Exception(f'"{folder} is not a folder')

    landuse_filename = "gis_osm_landuse_a_free_1.dbf"
    railways_filename = "gis_osm_railways_free_1.dbf"
    roads_filename = "gis_osm_roads_free_1.dbf"
    traffic_filename = "gis_osm_traffic_a_free_1.dbf"

    path_to = lambda filename: os.path.join(folder, filename)

    landuse_path = path_to(landuse_filename)
    railways_path = path_to(railways_filename)
    roads_path = path_to(roads_filename)
    traffic_path = path_to(traffic_filename)

    landuse_features = dbf.read(landuse_path)
    railways_features = dbf.read(railways_path)
    roads_features = dbf.read(roads_path)
    traffic_features = dbf.read(traffic_path)


def within_zone(input: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # the latitude and longitude bounds for the lower mainland
    xmin = -123.3
    xmax = -122.5
    ymin = 49.0
    ymax = 49.4
    return input.cx[xmin:xmax, ymin:ymax]


def cache_zone(folder: str) -> None:
    if os.path.exists(folder) == False:
        raise Exception(f'"{folder}" does not exist')
    if os.path.isdir(folder) == False:
        raise Exception(f'"{folder} is not a folder')

    if os.path.exists("cache") == False:
        os.mkdir("cache")
    filenames: list[str] = [
        "gis_osm_landuse_a_free_1.shp",
        "gis_osm_railways_free_1.shp",
        "gis_osm_roads_free_1.shp",
        "gis_osm_traffic_a_free_1.shp",
    ]

    path_to_source = lambda filename: os.path.join(folder, filename)
    path_to_destination = lambda filename: os.path.join("cache", filename)

    for filename in filenames:
        source = path_to_source(filename)

        input_df: gpd.GeoDataFrame = gpd.read_file(source)
        output_df: gpd.GeoDataFrame = within_zone(input_df)

        destionation = path_to_destination(filename)
        output_df.to_file(destionation)


def rate_point(x: float, y: float):
    pass


def is_skytrain(row) -> bool:
    name = str(row.train_name)
    return "SkyTrain" in name


# get metro rail routes, in Vancouver that's the SkyTrain
def get_metro_rail() -> gpd.GeoDataFrame:
    railways: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_railways_free_1.shp")
    railways["train_name"] = railways["name"]
    mask: gpd.GeoSeries = railways.apply(is_skytrain, axis=1)
    skytrain = railways[mask]
    return skytrain


def is_parking(row) -> bool:
    name = str(row.traffic_name)
    fclass = str(row.fclass)
    return "parking" in name.lower() or ("parking" in fclass and "under" not in fclass)


# get above ground parking lots
def get_parking() -> gpd.GeoDataFrame:
    traffic: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_traffic_a_free_1.shp")
    traffic["traffic_name"] = traffic["name"]
    mask: gpd.GeoSeries = traffic.apply(is_parking, axis=1)
    parking = traffic[mask]
    return parking


def get_landuse_positive() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_landuse_a_free_1.shp")
    key: str = (
        "nature_reserve|park|retail|forest|recreation_ground|grass|commercial|meadow|orchard|vineyard"
    )
    positive: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return positive


def get_landuse_neutral() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_landuse_a_free_1.shp")
    key: str = "cemetary|scrub|health"
    neutral: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return neutral


def get_landuse_negative() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_landuse_a_free_1.shp")
    key: str = "farmland|military|allotments|quary"
    negative: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return negative


# main function and entry point of program program execution
if __name__ == "__main__":
    folder = argv[1]

    # if there is no cache of location-limmited files then create one
    if (os.path.exists("cache") == False) or (len(os.listdir("cache")) != 4 * 5):
        for filename in os.listdir("cache"):
            os.remove(f"cache/{filename}")
        os.rmdir("cache")
        cache_zone(folder)

    roads: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_roads_free_1.shp")
    print(roads["fclass"].unique())
    # roads.plot()
    # plt.show()
