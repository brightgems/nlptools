#!/usr/bin/env python
# -*- coding: utf-8 -*-
#word2vec

import time, base64, os
import numpy as np
from scipy.spatial.distance import cosine
from ..utils import zload, zdump, restpost


'''
    Author: Pengjia Zhu (zhupengjia@gmail.com)
'''

class Embedding_Base(object):
    '''
        Parent class for other embedding classes to read the word vectors, please don't use this class directly

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys:
                    - vec_len: int, vector length, default is 300
                    - vec_type: type of saved vector, default is float64
                    - cached_w2v: the cache path in local, default is ''
                    - outofvocab: 0 for random, 1 for random but with additional dim, default is 0
                
    '''
    def __init__(self, cfg):
        self.cfg = {'vec_len':300, 'vec_type':'float64', 'cached_w2v':'', 'outofvocab': 0}
        for k in cfg:self.cfg[k] = cfg[k]
        self.__get_cached_vec()
        if self.cfg['outofvocab']:
            self.vec_len = int(self.cfg['vec_len']) + 1
   

    def distance(self, word1, word2):
        '''
            Calculate the cosine distance for two words

            Input:
                - word1: string
                - word2: string
        '''
        vec1 = self.__getitem__(word1)
        vec2 = self.__getitem__(word2)
        return cosine(vec1, vec2)

    def __get_cached_vec(self):
        if 'cached_w2v' in self.cfg and  os.path.exists(self.cfg['cached_w2v']):
            self.cached_vec = zload(self.cfg['cached_w2v'])
        else:
            self.cached_vec = {}
   
    
    def _postdeal(self, v = None, returnbase64 = False):
        if self.cfg['outofvocab']:
            if v:
                v = np.concatenate((v, np.zeros(1)))
            else:
                v = np.concatenate((np.random.randn(self.vec_len - 1), np.ones(1)))
        else:
            if not v:
                v = np.random.randn(self.vec_len)
        if returnbase64:
            v = base64.b64encode(v.tostring()).decode()
        return v
    

    def save(self):
        '''
            Save the word vectors in memory to *cached_w2v*
        '''
        if len(self.cfg['cached_w2v']) > 0:
            zdump(self.cached_vec, self.cfg['cached_w2v'])


class Embedding_File(Embedding_Base):
    '''
        Read the word vectors from local files

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys:
                    - all keys mentioned in Embedding_Base
                    - w2v_word2idx: pickle filepath for word-idx mapping
                    - w2v_idx2vec: numpy dump for idx-vector mapping
                    - RETURNBASE64: if this config exists, will return BASE64 instead of vector

        Usage:
            - emb_ins[word]: return the vector or BASE64 format vector
            - word in emb_ins: check if word existed in file
    '''
    def __init__(self, cfg):
        Embedding_Base.__init__(self, cfg)
        self.word2idx = None

    def _load_vec(self):
        if self.word2idx is None:
            self.word2idx = zload(self.cfg['w2v_word2idx'])
            self.idx2vec = np.load(self.cfg['w2v_idx2vec']).astype('float')

    def __getitem__(self, word):
        if word in self.cached_vec:
            return self.cached_vec[word]
        self._load_vec()
        v = self.idx2vec[self.word2idx[word]] if word in self.word2idx else None
        v = self._postdeal(v, 'RETURNBASE64' in self.cfg)
        self.cached_vec[word] = v
        return v

    def __contains__(self, word):
        self._load_vec()
        return word in self.word2idx


class Embedding_Redis(Embedding_Base):
    '''
        Read the word vectors from redis

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys:
                    - all keys mentioned in Embedding_Base
                    - redis_host: redis host
                    - redis port: redis port
                    - redis_db: database in redis
                    - RETURNBASE64: if this config exists, will return BASE64 instead of vector

        Usage:
            - emb_ins[word]: return the vector or BASE64 format vector
            - word in emb_ins: check if word existed in database
    '''
    def __init__(self, cfg):
        import redis
        Embedding_Base.__init__(self, cfg)
        self.redis_ins = redis.Redis(connection_pool = redis.ConnectionPool(host=cfg["redis_host"], port=cfg["redis_port"], db=cfg["redis_db"]))

    def __getitem__(self, word):
        if word in self.cached_vec:
            return self.cached_vec[word]
        v = self.redis_ins.get(word)
        if not v:
            v = self._postdeal(v, 'RETURNBASE64' in self.cfg)
        else:
            if not 'RETURNBASE64' in self.cfg:
                v = self._postdeal(np.fromstring(base64.b64decode(v)), 'RETURNBASE64' in self.cfg)
        self.cached_vec[word] = v
        return v

    def __contains__(self, word):
        v = self.redis_ins.get(word)
        return v is not None


class Embedding_Random(Embedding_Base):
    '''
        Randomly generate the vector for word

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys:
                    - all keys mentioned in Embedding_Base
                    - redis_host: redis host
                    - redis port: redis port
                    - redis_db: database in redis
                    - RETURNBASE64: if this config exists, will return BASE64 instead of vector

        Usage:
            - emb_ins[word]: return the vector or BASE64 format vector
            - word in emb_ins: check if word existed in cache
    '''
    def __init__(self, cfg):
        Embedding_Base.__init__(self, cfg)
        self.vec_len = int(self.cfg['vec_len'])

    def __getitem__(self, word):
        if word in self.cached_vec:
            return self.cached_vec[word]
        v = self._postdeal(None, 'RETURNBASE64' in self.cfg)
        self.cached_vec[word] = v
        return v

    def __contains__(self, word):
        return word in self.cached_vec


class Embedding_Dynamodb(Embedding_Base):
    '''
        Read the word vectors from aws dynamodb, please make sure you have related credential files for enviroments.

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys:
                    - all keys mentioned in Embedding_Base
                    - dynamodb: dynamodb database name
                    - RETURNBASE64: if this config exists, will return BASE64 instead of vector

        Usage:
            - emb_ins[word]: return the vector or BASE64 format vector
            - word in emb_ins: check if word existed in database
    '''
    def __init__(self, cfg):
        import boto3
        Embedding_Base.__init__(self, cfg)
        self.client = boto3.resource('dynamodb')
        self.table = self.client.Table(cfg['dynamodb'])

    def __getitem__(self, word):
        import boto3
        if word in self.cached_vec:
            return self.cached_vec[word]
        v = self.table.get_item(Key={"word":word})
        if not "Item" in v:
            v = self._postdeal(None, 'RETURNBASE64' in self.cfg)
        else:
            vector_binary = v['Item']['vector']
            if isinstance(vector_binary, boto3.dynamodb.types.Binary):
                vector_binary = vector_binary.value
            if 'RETURNBASE64' in self.cfg:
                v = vector_binary
            else:
                vector = np.fromstring(base64.b64decode(vector_binary), dtype=self.cfg['vec_type'])
                v = self._postdeal(vector)
        self.cached_vec[word] = v
        return v

    def __contains__(self, word):
        v = self.table.get_item(Key={"word":word})
        return "Item" in v


class Embedding_Rest(Embedding_Base):
    '''
        Read the word vectors from restapi

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys:
                    - vec_type: the type of vector used in restapi, float64, float32, float
                    - embedding_restapi: string, restapi url 
         
        Usage:
            - emb_ins[word]: return the vector or BASE64 format vector
            - word in emb_ins: check if word existed in database
    '''
    def __init__(self, cfg):
        Embedding_Base.__init__(self, cfg)
        self.rest_url = cfg['embedding_restapi']
    
    def __getitem__(self, word):
        if word in self.cached_vec:
            return self.cached_vec[word]
        vector = restpost(self.rest_url, {'text':word})
        if not 'RETURNBASE64' in self.cfg:
            vector = np.fromstring(base64.b64decode(vector), dtype=self.cfg['vec_type'])
            vector = self._postdeal(vector)
        self.cached_vec[word] = vector
        return vector

    def __contains(self, word):
        return True


class Embedding(object):
    '''
        Read the word vectors from different database sources

        Input:
            - cfg: dictionary or ailab.utils.config object
                - needed keys: Please check other Embedding_* classes for detailed needed keys for different sources. The choice of  source will look for the config key in sequential order below:
                    1. *w2v_word2idx* *w2v_idx2vec* read the wordvec from file
                    2. *dynamodb* read the wordvec from amazon's dynamodb
                    3. *redis_host* read from redis
                    4. *embedding_restapi* read from restapi
                    5. default: random generated

        Example usage:
            - emb = Embedding(cfg); embedding[word]
    '''
    def __new__(cls, cfg):
        if 'w2v_word2idx' in cfg and 'w2v_idx2vec' in cfg:
            return Embedding_File(cfg)
        elif 'dynamodb' in cfg:
            return Embedding_Dynamodb(cfg)
        elif 'redis_host' in cfg:
            return Embedding_Redis(cfg)
        elif 'embedding_restapi' in cfg:
            return Embedding_Rest(cfg)
        else:
            return Embedding_Random(cfg)

            


