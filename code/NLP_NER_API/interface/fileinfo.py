import datetime
from pathlib import Path


def createDate(filepath):
    fname = Path(filepath)
    mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime).replace(microsecond=0)
    return mtime

def compare_file_date(filepath_1,filepath_2):
    latest_file = filepath_1 if createDate(filepath_1) > createDate(filepath_2) else filepath_2
    return latest_file

def createDateList(filefullpath):
    datelist = []
    for i in filefullpath:
        datelist.append(createDate(i))
    return datelist

def size(filepath):
    msize = Path(filepath).stat().st_size
    return msize

def sizeList(filefullpath):
    sizeList = []
    for i in filefullpath:
        sizeList.append(size(i))
    return sizeList
