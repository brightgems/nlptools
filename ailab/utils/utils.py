#!/usr/bin/env python
import os, zlib
import pickle

#compress pickle file by using zlib and cpickle
def zdump(value,filename):
    with open(filename,"wb",-1) as fpz:
        fpz.write(zlib.compress(pickle.dumps(value,-1),9))


#load compressed pkl file from zdump
def zload(filename):
    with open(filename,"rb") as fpz:
        value=fpz.read()
        try:return pickle.loads(zlib.decompress(value))
        except:return pickle.loads(value)


#compress pickle string by using zlib and cpickle
def zdumps(value):
    return zlib.compress(pickle.dumps(value,-1),9)


#load compressed pkl string from zdump
def zloads(value):
    try:return pickle.loads(zlib.decompress(value))
    except:return pickle.loads(value)

#compress pickle string by using lzo and cpickle
def ldumps(value):
    import lzo
    return lzo.compress(pickle.dumps(value,-1),9)

#load compressed pkl string from ldump
def lloads(value):
    import lzo
    try:return pickle.loads(lzo.decompress(value))
    except:return pickle.loads(value)



