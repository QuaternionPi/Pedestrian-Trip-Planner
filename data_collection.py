import os
import codecs
from util import info, warning
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


def read_dbf_body_line(text: str, schema: Schema) -> dict[str, int]:
    if len(text) < schema.total_size:
        raise Exception("Text must be one less than the total size of the schema")

    depth = 0
    data = {}
    for attribute in schema.attributes:
        size = attribute.size
        reader = attribute.datatype
        section = text[depth : depth + size]
        data[attribute.name] = reader(section)

        depth += size
    return data


def read_dbf_body(handle: codecs.StreamReaderWriter, schema: Schema):
    request_size: int = schema.total_size + 1
    while True:
        line: str = handle.read(request_size).decode("utf-8")
        if line.isascii() == False:
            warning(f'Removed non-ascii entry "{line}"')
            return None
        if len(line) + 1 < request_size:
            break
        read_dbf_body_line(line, schema)


# read a single DBF file
def read_dbf(file: str):
    with codecs.open(file, "rb") as handle:
        schema: Schema = read_dbf_header(handle)
        read_dbf_body(handle, schema)

    info(f"read file {os.path.basename(file)}")
    return file


# read many DBF files in the same folder
def read_many_dbf(folder: os.path, files: list[str]):
    result = []
    for file in files:
        path = os.path.join(folder, file)
        single_result = read_dbf(path)
        result.append(single_result)
    return result


def geometry(code: int) -> str:
    descrimanent = code // 100
    match descrimanent:
        # polygons
        case 12:
            return "polygon"
        case 15:
            return "polygon"
        case 72:
            return "polygon"
        case 82:
            return "polygon"
        # lines
        case 11:
            return "line"
        case 51:
            return "line"
        case 61:
            return "line"
        case 66:
            return "line"
        case 67:
            return "line"
        case 81:
            return "line"
        case 83:
            return "line"
        case 53:
            return "line"
        case 54:
            return "line"
        case 55:
            return "line"
        case 56:
            return "line"
        case 62:
            return "line"
        case 63:
            return "line"
        case 64:
            return "line"
        case 65:
            return "line"
        case 90:
            return "line"
        case 91:
            return "line"
        # points, otherwise
        case _:
            return "point"
