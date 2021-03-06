#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from itertools import groupby
from operator import itemgetter


class AcoraSearch:
    '''
        search keyword using acora, please check `Acora <https://pypi.python.org/pypi/acora/>`_ for more details

        Input:
            - keywords: a keywords list to build an index
            - vocab: text.vocab object, used to convert word to id, default is None(avoid converting word to id)
    '''
    def __init__(self, keywords, vocab=None):
        from acora import AcoraBuilder
        builder = AcoraBuilder()
        #assert isinstance(keywords, (list,tuple))
        self.vocab = vocab
        for i in keywords:
            builder.add(i)

        #Generate the Acora search engine for the current keyword set:
        self.engine = builder.build()


    def find(self, input):
        '''
        Find keywords from input, search for all occurrences
        
        Input:
            - input: string
        
        Output:
            - list, if vocab=None format like [(word, wordpos), ...], if vocab existed, format like [(word, wordid and word position), ...]
        '''
        result =  self.engine.findall(input)
        if self.vocab is None:
            return result
        else:
            word, pos = zip(*result)
            wordid = [self.vocab.word2id(w) for w in word]
            
            return list(zip(word, wordid, pos))


    def find_longest(self, input):
        '''
        Find the longest match from input


        Input:
            - input: string
        
        Output:
            - list, if vocab=None format like (word, wordpos), if vocab existed, format like (word, wordid and word position)
        '''
        def longest_match(matches):
            for pos, match_set in groupby(matches, itemgetter(1)):
                yield max(match_set)

        return longest_match(self.find(input))


    def find_max_match(self, input):
        '''
        Find the max match from input

        Input:
            - input: string
        
        Output:
            - list, if vocab=None format like (word, wordpos), if vocab existed, format like (word, wordid and word position)
        '''
        def subset(a, b):
            if (a[1] >= b[1]) and ((a[1] + len(a[0])) <= (b[1] + len(b[0]))):
                return True
            else:
                return False

        def max_match(matches):
            if len(matches) <= 1:
                return matches

            maxmatch = []
            for i in matches:
                for j in matches:
                    if i == j:
                        continue
                    elif subset(i, j):  # or subset(j,i):
                        break
                else:
                    maxmatch.append(i)
            return maxmatch

        return max_match(self.find(input))


if __name__ == '__main__':
    from acora import AcoraBuilder
    bc = AcoraSearch(['死亡','death', '内服全般が難しくなってきた為内服を中止した'])
    #bc2 = AcoraSearch(['Vaccination site pruritus','staphylococcus aureus','cataract'], [1,2,3])
    for i in bc.find_max_match(
            'cataract,からstaphylococcus aureus同定,尿培養検査よりklebsiella pneumoniae staphylococcus aureus 同定\
death高令の患者、Vaccination site pruritus故に嚥下能力が徐々に低下し、その他、内服全般が難しくなってきた為内服を中止した。その後、少しずつ全身状態の悪化がすすみ、死亡に至った。よって、ネキシウムカプセルとの直接的な因果関係はないと考えられる。'):
        #print(i[0], i[1], i[2])
        print(i)
    #print('-'*100)
    #for i in bc2.find(
    #            'cataract,からstaphylococcus aureus同定,尿培養検査よりklebsiella pneumoniae staphylococcus aureus 同定\
    #death高令の患者、Vaccination site pruritus故に嚥下能力が徐々に低下し、その他、内服全般が難しくなってきた為内服を中止した。その後、少しずつ全身状態の悪化がすすみ、死亡に至った。よって、ネキシウムカプセルとの直接的な因果関係はないと考えられる。'):
    #        print(i[0], i[1])
