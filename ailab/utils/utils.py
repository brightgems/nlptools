#!/usr/bin/env python
import os, zlib, numpy
import pickle, unicodedata
from collections import Counter
from sklearn.utils import murmurhash3_32


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


def hashword(word, hashsize=16777216):
    return murmurhash3_32(word, positive=True) % (hashsize)


#resolve different type of unicode encodings
def normalize(text):
    try:
        return unicodedata.normalize('NFD', text)
    except Exception as err:
        print(err)
        raise(err)


#rest client post
def restpost(url, data):
    import requests, json
    return requests.post(url=url, data=json.dumps(data)).json()


#use environment variables to cover original environment
def envread(keys):
    cfg = {}
    for k in keys:
        if k in os.environ:
            cfg[k] = os.environ[k]
    return cfg

