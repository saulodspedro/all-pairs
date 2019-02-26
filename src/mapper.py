#!/usr/bin/env python
# coding: utf-8

import nltk
import sys
from textblob import TextBlob

blob = TextBlob(sys.stdin)

nouns = list(set(blob.noun_phrases))

everygrams = nltk.everygrams(blob.words,
                             min_len=3,
                             max_len=5)

for grams in everygrams:
    for noun in nouns:
        joined = ' '.join(grams).lower()
        if (joined.startswith(noun) or (joined.endswith(noun))):
            print('%s:%s\t%s' % (noun, joined.replace(noun,'_',1), 1))

