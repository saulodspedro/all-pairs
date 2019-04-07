pronouns=['I','you','he','she','it','we','they','me','him','her','us','them','what','who','whom','mine','yours','his','hers','ours','theirs','this','that','these','those','who','whom','which','what','whose','whoever','whatever','whichever','whomever','myself','yourself','himself','herself','itself','ourselves','themselves','each other','one another','anything','everybody','another','each','few','many','none','some','all','any','anybody','anyone','everyone','everything','no one','nobody','nothing','none','other','others','several','somebody','someone','something','most','enough','little','more','both','either','neither','one','much','such']

ignored_words = ['part','and','a','the end','end','parts','use','s']

right_noun_pattern = '^(NOUN|PROPN)*(VERB)+(ADJ|ADP|DT)+$|^(((NOUN)+(ADJ)+|(ADJ)+(NOUN)+)(ADJ|NOUN)*(ADJ|ADP|DET)+)$'
left_noun_pattern = '^VERB\w*NOUN$|^(VERB)+ADP$'
