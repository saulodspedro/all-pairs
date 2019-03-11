import nltk
import spacy
from dask.distributed import Client
from textblob import TextBlob

from utils import insert_pairs
from metadata import pronouns, ignored_words, ignored_contexts
from allpairsconfig import ConfigAllPairs

import datetime
import time
import os
from pathlib import Path

def build_pairs(filename):
    
    start_time = time.time()
    
    print('{}: started building pairs for {}'.format(datetime.datetime.now(), filename))
    
    #spacy settings
    nlp = spacy.load('en_core_web_sm', disable=['ner'])
    nlp.max_length = 1500000
    
    #load data
    with open(filename, 'r') as myfile:
        data=myfile.read().replace('\n', ' ')
    
    #get noun phrases
    spacy_obj = nlp(data)
    
    del nlp
    
    nouns = [chunk.text.lower() for chunk in spacy_obj.noun_chunks]
    set_nouns = set([n for n in nouns if n not in pronouns + ignored_words])  #remove pronouns
    
    del nouns
    del spacy_obj
    
    #get candidate contexts
    textblob_obj = TextBlob(data)
    everygrams = nltk.everygrams(textblob_obj.words,
                                 min_len=3,
                                 max_len=5)
    
    del textblob_obj
    
    #build pairs
    pairs = []
    for gram in everygrams:
        explode_gram = nltk.everygrams(gram,
                                       min_len=1,
                                       max_len=len(gram)-2)  #avoid context patterns with a single word
        
        ctx_candidates = [' '.join(g).lower() for g in explode_gram]
        intersection = list(set(ctx_candidates).intersection(set_nouns))
        
        joined = ' '.join(gram).lower()
        
        for noun in intersection:
            if joined.startswith(noun+" ") or joined.endswith(" "+noun):
                pairs.append((noun, joined.replace(noun,'_',1)))
    
    del set_nouns
    
    #save to database
    print('{}: saving pairs for {}'.format(datetime.datetime.now(), filename))
    res = insert_pairs(pairs)
    
    end_time = time.time()
    
    #print results
    print('{}: finished building pairs for {} in {}s'.format(datetime.datetime.now(), filename, end_time - start_time))
    print('{} created {} instances:'.format(filename, len(pairs)))
    print('from {}, {} instances were upserted'.format(filename, res.upserted_count))
    print('from {}, {} instances were modified'.format(filename, res.modified_count))

def main():
    
    #get configuration parameters
    ap_conf = ConfigAllPairs()

    #get database address from configuration
    data_path = ap_conf.data_path
    
    #files are also keys to dask graph
    file_list = Path(data_path).rglob('*')
    file_list = [str(f) for f in file_list if f.is_file()]
    
    #build dask graph
    dsk_params = []
    for f in file_list:
        dsk_params.append((f, (build_pairs, f)))
        
    dsk = dict(dsk_params)
    
    #set dask params
    client_opt = {'n_workers': os.cpu_count()-1,
                  'memory_limit': 'auto',
                  'processes': True,
                  'diagnostics_port': 8787}

    client = Client(**client_opt)

    res = client.get(dsk, file_list)

if __name__ == '__main__':
    start = time.time()
    print('{}: started main execution'.format(datetime.datetime.now()))
    main()
    end = time.time()

    print('{}: finished main execution in {}s'.format(datetime.datetime.now(), end - start))