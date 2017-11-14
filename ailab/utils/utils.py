#!/usr/bin/env python
import os, zlib, numpy
import pickle
from collections import Counter

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

def status_save(fn, status):
    with open(fn, 'w') as f:
        f.write(str(status))

def status_check(fn):
    if not os.path.exists(fn):
        return 0
    with open(fn, 'r') as f:
        return f.readlines()[0].strip()

def flat_list(l):
    return [item for sublist in l for item in sublist]

#def n_count(ids):
#    ids, doc_id = ids
#    counts = Counter(ids)
#    row = list(counts.keys())
#    data = list(counts.values())
#    col = [doc_id] * len(row)
#    return row, col, data

def n_count(i, ids):
    return numpy.sum(numpy.array(ids) == i)

