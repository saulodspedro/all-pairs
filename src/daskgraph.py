#dask graph

import nltk
from dask.multiprocessing import get
from textblob import TextBlob

def load(filename):
    with open(filename, 'r') as myfile:
        data=myfile.read().replace('\n', ' ')

    return data

def build_pairs(data):
    blob = TextBlob(data)

    nouns = list(set(blob.noun_phrases))

    everygrams = nltk.everygrams(blob.words,
                                 min_len=3,
                                 max_len=5)

    pairs = []

    for grams in everygrams:
        for noun in nouns:
            joined = ' '.join(grams).lower()
            if (joined.startswith(noun) or (joined.endswith(noun))):
                pairs.append((noun, joined.replace(noun,'_',1)))
     
    return pairs    

def store(pairs):
    print(pairs)
    
dsk = {'load-1': (load, 'samples/acdc.txt'),
       'load-2': (load, 'samples/queen.txt'),
       'load-3': (load, 'samples/rolling.txt'),
       'build_pairs-1': (build_pairs, 'load-1'),
       'build_pairs-2': (build_pairs, 'load-2'),
       'build_pairs-3': (build_pairs, 'load-3'),
       'store': (store, ['build_pairs-%d' % i for i in [1,2,3]])}

res = get(dsk, 'store')
