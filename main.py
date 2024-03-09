from sys import argv
import dbf
import os

# main function and entry point of program program execution
if __name__ == "__main__":
    folder = argv[1]
    landuse_filename = "gis_osm_landuse_a_free_1.dbf"
    natural_filename = "gis_osm_natural_a_free_1.dbf"
    points_of_interest_filename = "gis_osm_pois_a_free_1.dbf"
    railways_filename = "gis_osm_railways_free_1.dbf"
    roads_filename = "gis_osm_roads_free_1.dbf"
    traffic_filename = "gis_osm_traffic_a_free_1.dbf"
    transport_filename = "gis_osm_transport_a_free_1.dbf"

    landuse = dbf.read(os.path.join(folder, landuse_filename))
    natural = dbf.read(os.path.join(folder, natural_filename))
    points_of_interest = dbf.read(os.path.join(folder, points_of_interest_filename))
    railways = dbf.read(os.path.join(folder, railways_filename))
    roads = dbf.read(os.path.join(folder, roads_filename))
    traffic = dbf.read(os.path.join(folder, traffic_filename))
    transport = dbf.read(os.path.join(folder, transport_filename))
