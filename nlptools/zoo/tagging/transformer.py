#!/usr/bin/env python

import torch
import torch.nn as nn
import torch.nn.functional as F

from .seq2seq_base import Seq2SeqBase
from ..encoders.transformer_encoder import TransformerEncoder
from ..encoders.transformer_decoder import TransformerDecoder


class Transformer(Seq2SeqBase):
    def __init__(self, encoder_vocab, decoder_vocab=None, pretrained_embed=True, encoder_layers=3, decoder_layers=6, encoder_learned_pos=False, decoder_learned_pos=False, encoder_attention_heads=4, decoder_attention_heads=8, encoder_ffn_embed_dim=512, decoder_ffn_embed_dim=1024, normalize_before=False, share_embed=False, decoder_share_embed=True, dropout=0.1, attention_dropout=0.1, relu_dropout=0.1, device='cpu'):
        
        super().__init__(encoder_vocab, decoder_vocab, pretrained_embed, share_embed, decoder_share_embed, device)

        self.encoder = TransformerEncoder(
                    vocab = self.encoder_vocab,
                    pretrained_embed = pretrained_embed,
                    layers = encoder_layers,
                    learned_pos = encoder_learned_pos,
                    attention_heads = encoder_attention_heads,
                    ffn_embed_dim = encoder_ffn_embed_dim,
                    normalize_before = normalize_before,
                    dropout = dropout,
                    attention_dropout = attention_dropout,
                    relu_dropout = relu_dropout
                ) 
        
        self.decoder = TransformerDecoder(
                    vocab = self.decoder_vocab,
                    pretrained_embed = self.decoder_pretrained_embed,
                    layers = decoder_layers,
                    learned_pos = decoder_learned_pos,
                    attention_heads = decoder_attention_heads,
                    ffn_embed_dim = decoder_ffn_embed_dim,
                    share_embed = decoder_share_embed,
                    normalize_before = normalize_before,
                    dropout = dropout,
                    attention_dropout = attention_dropout,
                    relu_dropout = relu_dropout
                )
        
        if self.share_embed:
            self.decoder.embed_tokens.weight = self.encoder.embed_tokens.weight

