#!/usr/bin/env python3
from nlptools.text.tokenizer import Tokenizer_BERT
from nlptools.utils import zload
import sys

s = Tokenizer_BERT(bert_model_name='/home/pzhu/.pytorch_pretrained_bert/bert-base-uncased')

txt = 'Who was Jim Henson ? Jim Henson was a puppeteer'

print(s.seg(txt))

print(s.vocab)
