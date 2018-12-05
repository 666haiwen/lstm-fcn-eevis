"""
    Copyright 2018-2019 VAG (Visual Analytics Group), Zhejiang Univ.

    Provide useful function for other python file
"""
import os
from enum import Enum
# 3rd party imports
import json
import sys
sys.path.append(os.path.join(os.getcwd()))
from data_parse.const import FILE_PATH


class Lists(Enum):
    busId = 0
    data = 1
    interval = 2


class DataLists(Enum):
    origin = 0
    diff = 1


class IntervalLists(Enum):
    above = 0
    below = 1


def get_file_list():
    files = []
    for file_name in os.listdir(FILE_PATH):
        if '.' not in file_name:
            files.append(file_name)
    return files


def get_json_file(filePath, fileName, defaultRes={}):
    if os.path.exists(filePath + fileName):
        f = open(filePath + fileName, encoding='utf-8')
        fileRes = json.load(f)
        return fileRes
    return defaultRes

