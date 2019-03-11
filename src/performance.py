import nltk
import spacy
from textblob import TextBlob
nltk.download('brown')
nltk.download('punkt')
import time

pronouns=['I','you','he','she','it','we','they','me','him','her','us','them','what','who','whom','mine','yours','his','hers','ours','theirs','this','that','these','those','who','whom','which','what','whose','whoever','whatever','whichever','whomever','myself','yourself','himself','herself','itself','ourselves','themselves','each other','one another','anything','everybody','another','each','few','many','none','some','all','any','anybody','anyone','everyone','everything','no one','nobody','nothing','none','other','others','several','somebody','someone','something','most','enough','little','more','both','either','neither','one','much','such']

nlp = spacy.load('en_core_web_sm', disable=['ner'])
nlp.max_length = 1500000

#simple all-pairs data generator

start = time.time()

filename = '/home/saulo/projects/all-pairs/data/AA/wiki_00'
#filename = '/home/saulo/projects/all-pairs/samples/queen.txt'

cp1 = time.time()

with open(filename, 'r') as myfile:
    data=myfile.read().replace('\n', ' ')
    
cp2 = time.time()
print('load time: '+str(cp2-cp1))
        
spacy_obj = nlp(data)
textblob_obj = TextBlob(data)

cp3 = time.time()
print('parser: '+str(cp3-cp2))

del data

nouns = [chunk.text.lower() for chunk in spacy_obj.noun_chunks]

cp4 = time.time()
print('get nouns: '+str(cp4-cp3))

clean_nouns = [n for n in nouns if n not in pronouns]  #remove pronouns

cp5 = time.time()
print('clean nouns: '+str(cp5-cp4))

del spacy_obj

everygrams = nltk.everygrams(textblob_obj.words,
                             min_len=3,
                             max_len=5)

cp6 = time.time()
print('build grams: '+str(cp6-cp5))

del textblob_obj

pairs = []

set_nouns = set(clean_nouns) 
for gram in everygrams:
#    set_grams = set([g.lower() for g in grams])
    
    
    explode_gram = nltk.everygrams(gram,
                                  min_len=1,
                                  max_len=len(gram)-2)  #avoid context patterns with a single word
    
    ctx_candidates = [' '.join(g).lower() for g in explode_gram]
    
    intersection = list(set(ctx_candidates).intersection(set_nouns))
    
    joined = ' '.join(gram).lower()
    for noun in intersection:
        if joined.startswith(noun+" ") or joined.endswith(" "+noun):
            pairs.append((noun, joined.replace(noun,'_',1)))
            
cp7 = time.time()
print('build pairs: '+str(cp7-cp6))

end = time.time()
print(end - start)

print(len(pairs))