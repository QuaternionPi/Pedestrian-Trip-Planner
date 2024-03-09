import os
import codecs
from util import info, warning
from collections import namedtuple


# Parses acording to https://www.geofabrik.de/data/geofabrik-osm-gis-standard-0.7.pdf

# Schema of a DBF
Schema = namedtuple("Schema", ["attributes", "total_size"])
# Attribute of a DBF
Attribute = namedtuple("Attribute", ["name", "datatype", "parser", "size"])
# Read-in DBF
DBase = namedtuple("DBF", ["filename", "elements", "schema"])


# Read a single 32 byte block in the header of a DBF file
def read_header_line(line: str) -> Attribute:
    if len(line) != 32:
        raise Exception("Header lines must be 32 characters long")
    name: str = line[0:11].rstrip(b"\x00").decode("utf-8")
    datatype: str = line.decode("utf-8")[11]
    parser: lambda x: x = None
    size: int = line[16]
    match datatype:
        case "C":
            datatype = "str"
            parser = lambda x: str(x).strip()
        case "N":
            datatype = "int"
            parser = lambda x: int(x)
        case _:
            raise Exception(f"Attribute datatype type: '{datatype}' is unknown")
    output: Attribute = Attribute(name, datatype, parser, size)
    return output


# Read the header of a DBF file
def read_header(handle: codecs.StreamReaderWriter) -> Schema:
    handle.read(32)
    attributes: list[Attribute] = []
    total_size: int = 0
    while True:
        start = handle.read(2)
        if start[0:2] == b"\r ":  # break if start of body
            break
        line: str = start + handle.read(30)
        attribute: Attribute = read_header_line(line)
        attributes.append(attribute)
        total_size += attribute.size

    output: Schema = Schema(attributes, total_size)
    return output


# Read a single entry in the body of a DBF file
def read_body_line(text: str, schema: Schema) -> dict[str, int]:
    if len(text) < schema.total_size:
        raise Exception("Text must be one less than the total size of the schema")

    depth: int = 0
    data: dict[str, int] = {}
    for attribute in schema.attributes:
        size: int = attribute.size
        parser = attribute.parser
        section: str = text[depth : depth + size]
        name: str = attribute.name

        data[name] = parser(section)

        depth += size
    return data


# Read the body of a DBF file
def read_body(
    handle: codecs.StreamReaderWriter, schema: Schema
) -> list[dict[str, int]]:
    request_size: int = schema.total_size + 1
    result: list[dict[str, int]] = []
    total_read: int = 0
    while True:
        line: str = handle.read(request_size).decode("utf-8")
        total_read += request_size
        if line.isascii() == False:
            warning(f'Removed non-ascii entry "{line}"')
            continue
        if len(line) + 1 < request_size:
            break
        result.append(read_body_line(line, schema))
    return result


# Read a single DBF file
def read(file: str) -> DBase:
    elements: list[dict[str, int]] = []
    with codecs.open(file, "rb") as handle:
        schema: Schema = read_header(handle)
        elements: list[dict[str, int]] = read_body(handle, schema)

    filename = os.path.basename(file)
    info(f"read file {filename}")
    return DBase(filename, elements, schema)


# Read many DBF files in the same folder
def read_many(folder: os.path, files: list[str]) -> list[DBase]:
    result = []
    for file in files:
        path: str = os.path.join(folder, file)
        single_result: DBase = read(path)
        result.append(single_result)
    return result


# Get the geometry type of a DBF file's code
# This may break with newer editions of the Geofabik file schema
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
