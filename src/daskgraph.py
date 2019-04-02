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

def build_pairs(filename, nlp_remote):
    
    start_time = time.time()
    
    #load data
    with open(filename, 'r') as myfile:
        data=myfile.read().replace('\n', ' ')
    
    #get noun phrases
    spacy_obj = nlp_remote(data)
 
  #  del nlp_remote
    
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
    res = insert_pairs(pairs)
    
    end_time = time.time()
    
    #print results
    print('{}: {} {} {}s'.format(datetime.datetime.now(),
                                 filename,
                                 len(res.inserted_ids),
                                 end_time - start_time))

def main():
    
    #get configuration parameters
    ap_conf = ConfigAllPairs()

    #get database address from configuration
    data_path = ap_conf.data_path
    
    #files are also keys to dask graph
    file_list = Path(data_path).rglob('*')    
    file_list = [str(f) for f in file_list if f.is_file()]
    
    #use a third of the data
    file_list = file_list[0::3]
    
    #spacy settings
    nlp = spacy.load('en_core_web_sm', disable=['ner'])
    nlp.max_length = 1500000
    
    #set dask params
    client_opt = {'n_workers': os.cpu_count()-1,
                  'memory_limit': 'auto',
                  'processes': True,
                  'diagnostics_port': 8787}

    client = Client(**client_opt)
    
    nlp_remote = client.scatter(nlp, broadcast=True)
    
    #build dask graph
    dsk_params = []
    for f in file_list:
        dsk_params.append((f, (build_pairs, f, nlp_remote)))
        
    dsk = dict(dsk_params)
    
    res = client.get(dsk, file_list)

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()

    print('{}: finished main execution in {}s'.format(datetime.datetime.now(), end - start))