import os

def getRootPath():
    rootPath = os.path.dirname(os.path.abspath(__file__))
    return rootPath
