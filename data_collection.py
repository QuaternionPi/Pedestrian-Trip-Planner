import os
import codecs


# read a single DBF file
def read_dbf(file: os.path):
    with codecs.open(file, "rb") as handle:
        handle.seek(1000)
        byte = handle.read(1000)
        print(byte)

    return file


# read many DBF files in the same folder
def read_dbf(folder: os.path, files: list[str]):
    result = []
    for file in files:
        path = os.path.join(folder, file)
        single_result = read_dbf(path)
        result.append(single_result)
    return result
