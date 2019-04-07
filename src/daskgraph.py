import nltk
import spacy
from dask.distributed import Client

from utils import insert_pairs
from metadata import pronouns, ignored_words, left_noun_pattern, right_noun_pattern
from allpairsconfig import ConfigAllPairs

import datetime
import time
import os
import re
from pathlib import Path

def build_pairs(filename, nlp_remote):
    
    start_time = time.time()
    
    #load data
    with open(filename, 'r') as myfile:
        data=myfile.read().replace('\n', ' ')
    
    #get noun phrases
    spacy_obj = nlp_remote(data)
    
    #remove puctuation
    tokens = [t for t in spacy_obj.doc if t.pos_ != 'PUNCT']
    
    nouns = [chunk.text.lower() for chunk in spacy_obj.noun_chunks]
    set_nouns = set([n for n in nouns if n not in pronouns + ignored_words])  #remove pronouns
    
    del nouns
    del spacy_obj

    #get candidate contexts
    everygrams = nltk.everygrams(tokens,
                                 min_len=3,
                                 max_len=5)
    
    #build pairs
    pairs = []
    
    for gram in everygrams:
        first_word = gram[0]
        last_word = gram[-1]
        
        explode_gram = list(nltk.everygrams(gram, min_len=1))
        
        for eg in explode_gram:
            if(len(eg) <= len(gram)-2):  #noun phrase must be small enough, so context is of size 2 or greater
                
                eg_string = ' '.join([g.text for g in eg]).lower()  #  possible noun phrase
                
                if(eg_string in set_nouns):  #  possible noun phrase actually is a noun phrase
                    
                    #the noun phrase is on the left side of context pattern
                    if(eg[0] == first_word):
                        context = [gr for gr in explode_gram if len(gr) == len(gram)-len(eg) and gr[-1] == last_word]
                        ctx_pos_pattern = ''.join([c.pos_ for c in context[0]])
                            
                        if(re.search(left_noun_pattern, ctx_pos_pattern)):
                            ctx_string = ' '.join([c.text for c in context[0]])
                            pairs.append((eg_string, "_ "+ctx_string))
                
                    #the noun phrase is on the right side of context pattern
                    if(eg[-1] == last_word):
                        context = [gr for gr in explode_gram if len(gr) == len(gram)-len(eg) and gr[0] == first_word]
                        ctx_pos_pattern = ''.join([c.pos_ for c in context[0]])
                        
                        if(re.search(right_noun_pattern, ctx_pos_pattern)):
                            ctx_string = ' '.join([c.text for c in context[0]])
                            pairs.append((eg_string, ctx_string+" _"))
    
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