import pymongo
from allpairsconfig import ConfigAllPairs

def insert_pairs(pairs):
    
    #get configuration parameters
    ap_conf = ConfigAllPairs()

    #get database address from configuration
    db_address = ap_conf.db_address

    #connection to mongo database
    conn = pymongo.MongoClient(db_address)

    db_ap = conn['db_allpairs']
    
    #create index
    db_ap.allpairs_raw.create_index([('noun_phrase', pymongo.ASCENDING) ,
                                    ('ctx_pattern', pymongo.ASCENDING)])

    #update statement
#    update = {'$inc': {'counter': 1}}

    result = db_ap.allpairs_raw.insert_many([
        {'noun_phrase': pair[0],
         'ctx_pattern': pair[1],
         'counter': 1}
        for pair in pairs])
    
    #build batch operations
#    requests = []
#    for pair in pairs:
        
        #set update values
#        filter_ = {'noun_phrase': pair[0],
#                   'ctx_pattern': pair[1],
#                   'counter': 1}
        
#        requests.append(pymongo.UpdateOne(filter_, update, upsert=True))
        
    #execute batch updates
#    result = db_ap.allpairs_v2.bulk_write(requests, ordered=False)
    
    #close connection
    conn.close()
    
    return result