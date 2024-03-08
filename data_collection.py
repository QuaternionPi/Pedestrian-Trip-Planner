import os
import codecs
from collections import namedtuple

# parses acording to https://www.geofabrik.de/data/geofabrik-osm-gis-standard-0.7.pdf


Attribute = namedtuple("Attribute", ["name", "size"])
Schema = namedtuple("Schema", ["attributes", "total_size"])


def read_osm_header_line(line: str) -> Attribute:
    if len(line) != 32:
        raise Exception("Header lines must be 32 characters long")
    name: str = line[0:11].rstrip(b"\x00").decode("utf-8")
    size: int = line[16]
    output: Attribute = Attribute(name, size)
    return output


def read_osm_header(handle: codecs.StreamReaderWriter) -> Schema:
    handle.read(32)
    attributes: list[Attribute] = []
    total_size = 0
    while True:
        start = handle.read(2)
        if start[0:2] == b"\r ":  # break if start of body
            break
        line: str = start + handle.read(30)
        attribute: Attribute = read_osm_header_line(line)
        attributes.append(attribute)
        total_size += attribute.size

    output: Schema = Schema(attributes, total_size)
    return output


def read_osm_element(text: str):
    """
    id INTEGER (4 Bytes) Id of this feature. Unique in this layer.

    osm_id BIGINT (8 Bytes) OSM Id taken from the Id of this feature (node_id, way_id, or relation_id) in the OSM database.

    lastchange TIMESTAMP WITHOUT TIME ZONE (8 Bytes) Last change of this feature. Comes from the OSM last_changed attribute.

    code SMALLINT (2 Bytes) 4 digit code (between 1000 and 9999) defining the class of this feature. The first
    one or two digits define the layer, the last two or three digits the class inside a layer.

    fclass VARCHAR(40) Class name of this feature.

    name VARCHAR(100) Name of this feature, like a street or place name

    total length 4 + 8 + 8 + 2 + 40 + 100 = 162
    """


# read a single DBF file
def read_dbf(file: os.path):
    with codecs.open(file, "rb") as handle:
        schema: Schema = read_osm_header(handle)
        print(schema)
        for i in range(10):
            line: str = handle.read(schema.total_size + 1).decode("utf-8")
            print(line)

    return file


# read many DBF files in the same folder
def read_many_dbf(folder: os.path, files: list[str]):
    result = []
    for file in files:
        path = os.path.join(folder, file)
        single_result = read_dbf(path)
        result.append(single_result)
    return result
