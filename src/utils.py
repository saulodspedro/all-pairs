import pymongo
from allpairsconfig import ConfigAllPairs

def db_conn():
    #get configuration parameters
    ap_conf = ConfigAllPairs()

    #get database address from configuration
    db_address = ap_conf.db_address

    #connection to mongo database
    conn = pymongo.MongoClient(db_address)

    db_ap = conn['db_allpairs']
 
    #id_tweet should be unique in the database
    db_ap.allpairs.create_index([('noun_phrase', pymongo.ASCENDING) ,
                                 ('ctx_pattern', pymongo.ASCENDING)], unique=True)

    return db_ap

def insert_pairs(pairs):
    #get database connection
    db_ap = db_conn()

    update = {'$inc': {'counter': 1}}
    
    requests = []
    
    #build batch operations
    for pair in pairs:
        
        #set update values
        filter_ = {'noun_phrase': pair[0],
                   'ctx_pattern': pair[1]}
        
        requests.append(pymongo.UpdateOne(filter_, update, upsert=True))
        
    #execute batch updates
    result = db_ap.allpairs.bulk_write(requests, ordered=False)
    
    #close connection
    db_ap.close()
    
    return result