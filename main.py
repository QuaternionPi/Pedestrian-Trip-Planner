from sys import argv
import data_collection
import os

# main function and entry point of program program execution
if __name__ == "__main__":
    folder = os.path.join(os.pardir, "british-columbia-latest-free.shp")
    files = ["gis_osm_landuse_a_free_1.dbf"]
    data = data_collection.read_dbf(folder, files)
    pass
