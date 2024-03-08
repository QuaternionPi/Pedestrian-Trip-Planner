from sys import argv
import data_collection
import os

# main function and entry point of program program execution
if __name__ == "__main__":
    folder = argv[1]
    files = [
        "gis_osm_landuse_a_free_1.dbf",
        "gis_osm_buildings_a_free_1.dbf",
        "gis_osm_natural_a_free_1.dbf",
        "gis_osm_natural_free_1.dbf",
    ]
    data = data_collection.read_many_dbf(folder, files)
    pass
