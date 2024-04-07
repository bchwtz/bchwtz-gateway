"""
This demo shows how to connect to a mongodb database and collection as well as inserting the acceleration log data.
Acceleration data logging has two different modes, 'advertisement' and 'logging', which are stored in the key 'KEYNAME'.
The actual timestamp is stored in the 'advertisement' part of the data, while all other 
We only want to view the 'logging' data.
"""

import pymongo
import json
import pandas as pd
import urllib.parse
import numpy as np
import datetime
import time
import argparse
import sys
import os

def get_sequence_gap_indices(dict_keys:dict,gap:int=1):
    diffs = np.diff(list(dict_keys))
    return np.where(diffs > gap)[0]

def get_sample_rate(dict_keys,min_key:int,df: pd.DataFrame):
    gap_indices = get_sequence_gap_indices(dict_keys)
    sample_rate = 0

    if len(gap_indices) == 0:
        dt = df[0][min_key+3-1]["measurement.recorded_time"]-df[0][min_key+3-2]["measurement.recorded_time"]
    else:
        for gap_ind in gap_indices:
            if gap_ind > 3:
                dt = df[0][min_key+gap_ind-1]["measurement.recorded_time"]-df[0][min_key+gap_ind-2]["measurement.recorded_time"]
                break
    
    return 1000/dt

# taken from "advertisement" part of dataframe
def get_logging_starttime(dict_keys,df: pd.DataFrame):
    gaps = get_sequence_gap_indices(dict_keys)
    print(gaps)

    if len(gaps) == 0:
        return df[0][max(list(dict_keys))]["measurement.recorded_time"]
    else:
        return df[0][min(gaps)]["measurement.recorded_time"]
    
def connect_to_mongodb(user: str, pw: str, db_name: str = "gateway", coll_name: str = "accel_meas",
                       ip: str= "localhost", port: int=27017, auth_source: str ="admin"):
    """
    Connecting to mongodb server and retrieving the connection object ('client'), the database ('db') and 
    collection reference ('coll').
    """

    # https://stackoverflow.com/questions/40346767/pymongo-auth-failed-in-python-script
    user = urllib.parse.quote_plus(user)
    pw = urllib.parse.quote_plus(pw)

    # Connect to the MongoDB database
    client = pymongo.MongoClient(f"mongodb://{user}:{pw}@{ip}:{port}/{db_name}",authSource=auth_source)
    db = client[db_name]

    coll = db[coll_name]

    return client,db,coll

def main():
    """
    Argument parsing, dataframe reformatting and inserting additional data like timestamp, session_name and correcting sequence_id.
    Afterwards parse the dataframe as dict and insert it via collection.insert_many() directly into mongodb and close the session.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--user", help="mongodb user name", default="mongo")
    parser.add_argument("-p","--password", help="mongodb password")
    parser.add_argument("-i","--ip", help="mongodb ip", default="localhost")
    parser.add_argument("-po","--port", help="mongodb port", default=27017)
    parser.add_argument("-d","--database", help="mongodb database name", default="gateway")
    parser.add_argument("-c","--collection", help="mongodb collection name", default="accel_meas")
    parser.add_argument("-jp","--json_path", help="path to acceleration log in JSON format")
    parser.add_argument("-sn","--session_name", help="entry for 'session_name' field in mongodb. Default: json_path (- ending) as text.")
    args = parser.parse_args()

    if args.password == None:
        args.password= os.environ["MONGO_PASSWORD"]

    if args.json_path == None:
        print("Argument '--json_path' required. exiting...")
        exit()

    client,db,collection = connect_to_mongodb(args.user,args.password,args.database,args.collection,args.ip,args.port)

    print("dbs:")
    for database_name in client.list_database_names():
        print(database_name)

    print("collections:")
    for coll in db.list_collection_names():
        print(coll)

    if args.session_name is None:
        session_name = args.json_path.split(".json")[0]
    else:
        session_name = args.session_name
    
    with open(args.json_path) as file:
        data = json.load(file)

    df = pd.DataFrame.from_dict(pd.json_normalize(data), orient="columns")

    del df[0]
    dft = df.transpose()

    # split dataframe into "advertisement" and "logging" part (sampling of sensor data takes part in 'logging' mode)
    dft_adv = dft[dft[0].astype(str).str.contains("advertisement")]
    dft_logging = dft[dft[0].astype(str).str.contains("logging")]

    # convert indices to sequence_number
    d = {}

    logging_keys = dft_logging[0].to_dict().keys()
    adv_keys = dft_adv[0].to_dict().keys()
    min_key_logging = min(list(logging_keys))

    sample_rate = get_sample_rate(logging_keys, min_key_logging, dft_logging)
    logging_starttime = get_logging_starttime(adv_keys, dft_adv)

    for i,key in enumerate(logging_keys):
        d[key] = dft_logging[0][key]
        d[key]["measurement.sequence_number"] = int(key)-min_key_logging
        d[key]["session_name"] = session_name
        d[key]["measurement.sample_rate"] = sample_rate
        
        d[key]["measurement.recorded_time"] = (i*1/sample_rate)+logging_starttime
         
    modified_df_dict = pd.DataFrame.from_dict(d).T.to_dict("records")

    # Insert entries into the database
    collection.insert_many(modified_df_dict)

    print("data inserted into mongo db")

    # retrieve data from mongodb
    query = {"session_name":{"$in":[f"{session_name}"]}}
    df = pd.DataFrame(list(collection.find(query)))

    print(df)
    
    # Close the database connection
    client.close()

if __name__ == "__main__": 
    main()
