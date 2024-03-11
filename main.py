from sys import argv
import dbf
import os
import geopandas as gpd
import matplotlib.pyplot as plt


def get_features(folder: str):
    if os.path.exists(folder) == False:
        raise Exception(f'"{folder}" does not exist')
    if os.path.isdir(folder) == False:
        raise Exception(f'"{folder} is not a folder')

    landuse_filename = "gis_osm_landuse_a_free_1.dbf"
    natural_filename = "gis_osm_natural_a_free_1.dbf"
    places_filename = "gis_osm_places_free_1.dbf"
    points_filename = "gis_osm_pois_a_free_1.dbf"
    railways_filename = "gis_osm_railways_free_1.dbf"
    roads_filename = "gis_osm_roads_free_1.dbf"
    traffic_filename = "gis_osm_traffic_a_free_1.dbf"
    transport_filename = "gis_osm_transport_a_free_1.dbf"

    path_to = lambda filename: os.path.join(folder, filename)

    landuse_path = path_to(landuse_filename)
    natural_path = path_to(natural_filename)
    places_path = path_to(places_filename)
    points_path = path_to(points_filename)
    railways_path = path_to(railways_filename)
    roads_path = path_to(roads_filename)
    traffic_path = path_to(traffic_filename)
    transport_path = path_to(transport_filename)

    landuse_features = dbf.read(landuse_path)
    natural_features = dbf.read(natural_path)
    places_features = dbf.read(places_path)
    points_features = dbf.read(points_path)
    railways_features = dbf.read(railways_path)
    roads_features = dbf.read(roads_path)
    traffic_features = dbf.read(traffic_path)
    transport_features = dbf.read(transport_path)


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

    filenames: list[str] = [
        "gis_osm_landuse_a_free_1.shp",
        "gis_osm_natural_a_free_1.shp",
        "gis_osm_places_free_1.shp",
        "gis_osm_pois_a_free_1.shp",
        "gis_osm_railways_free_1.shp",
        "gis_osm_roads_free_1.shp",
        "gis_osm_traffic_a_free_1.shp",
        "gis_osm_transport_a_free_1.shp",
    ]

    path_to_source = lambda filename: os.path.join(folder, filename)
    path_to_destination = lambda filename: os.path.join("cache", filename)

    for filename in filenames:
        source = path_to_source(filename)

        input_df: gpd.GeoDataFrame = gpd.read_file(source)
        output_df: gpd.GeoDataFrame = within_zone(input_df)

        destionation = path_to_destination(filename)
        output_df.to_file(destionation)


# main function and entry point of program program execution
if __name__ == "__main__":
    folder = argv[1]

    # if there is no cache then write to it
    if (os.path.exists("cache") == False) or (len(os.listdir("cache")) != 8 * 5):
        cache_zone(folder)

    input_df: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_railways_free_1.shp")
    input_df.plot()
    plt.show()
