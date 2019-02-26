#dask graph

import nltk
from dask.distributed import Client
from dask import delayed
from textblob import TextBlob
from os import cpu_count

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

def main():

    dsk = {'load-1': (load, '../samples/acdc_10'),
           'load-2': (load, '../samples/queen_10'),
           'load-3': (load, '../samples/rolling_10'),
           'build_pairs-1': (build_pairs, 'load-1'),
           'build_pairs-2': (build_pairs, 'load-2'),
           'build_pairs-3': (build_pairs, 'load-3'),
           'store': (store, ['build_pairs-%d' % i for i in [1,2,3]])}

    client_opt = {'n_workers': cpu_count(),
                  'memory_limit': 0,
                  'processes': True,
                  'diagnostics_port': 8787}

    client = Client(**client_opt)

    res = client.get(dsk, 'store')

if __name__ == '__main__':
    main()
