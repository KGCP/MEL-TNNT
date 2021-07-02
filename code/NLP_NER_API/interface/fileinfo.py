import datetime
import pathlib


def createDate(filepath):
    fname = pathlib.Path(filepath)
    mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime).replace(microsecond=0)
    return mtime

def createDateList(filefullpath):
    datelist = []
    for i in filefullpath:
        datelist.append(createDate(i))
    return datelist

def size(filepath):
    msize = pathlib.Path(filepath).stat().st_size
    return msize

def sizeList(filefullpath):
    sizeList = []
    for i in filefullpath:
        sizeList.append(size(i))
    return sizeList
