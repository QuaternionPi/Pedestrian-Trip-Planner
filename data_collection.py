import os
import codecs
from collections import namedtuple


# parses acording to https://www.geofabrik.de/data/geofabrik-osm-gis-standard-0.7.pdf


Schema = namedtuple("Schema", ["attributes", "total_size"])
Attribute = namedtuple("Attribute", ["name", "datatype", "size"])


def read_dbf_header_line(line: str) -> Attribute:
    if len(line) != 32:
        raise Exception("Header lines must be 32 characters long")
    name: str = line[0:11].rstrip(b"\x00").decode("utf-8")
    datatype: str = line.decode("utf-8")[11]
    size: int = line[16]
    match datatype:
        case "C":
            datatype = str
        case "N":
            datatype = int
        case _:
            raise Exception(f"Attribute datatype type: '{datatype}' is unknown")
    output: Attribute = Attribute(name, datatype, size)
    return output


def read_dbf_header(handle: codecs.StreamReaderWriter) -> Schema:
    handle.read(32)
    attributes: list[Attribute] = []
    total_size = 0
    while True:
        start = handle.read(2)
        if start[0:2] == b"\r ":  # break if start of body
            break
        line: str = start + handle.read(30)
        attribute: Attribute = read_dbf_header_line(line)
        attributes.append(attribute)
        total_size += attribute.size

    output: Schema = Schema(attributes, total_size)
    return output


def read_dbf_element(text: str, schema: Schema):
    if len(text) - 1 != schema.total_size:
        raise Exception("text must be one less than the total size of the schema")

    depth = 0
    data = {}
    for attribute in schema.attributes:
        size = attribute.size
        reader = attribute.datatype
        section = text[depth : depth + size]
        data[attribute.name] = reader(section)

        depth += size


# read a single DBF file
def read_dbf(file: os.path):
    with codecs.open(file, "rb") as handle:
        schema: Schema = read_dbf_header(handle)
        for i in range(10):
            line: str = handle.read(schema.total_size + 1).decode("utf-8")
            read_dbf_element(line, schema)

    return file


# read many DBF files in the same folder
def read_many_dbf(folder: os.path, files: list[str]):
    result = []
    for file in files:
        path = os.path.join(folder, file)
        single_result = read_dbf(path)
        result.append(single_result)
    return result
