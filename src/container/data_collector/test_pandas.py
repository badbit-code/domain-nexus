

import json
import pandas as pd
import psycopg2
from io import StringIO


"""with psycopg2.connect(user="unicorn_user",
                        password="magical_password",
                        host="127.0.0.1",
                        port="57325",
                        database="rainbow_database") as conn:
    with conn.cursor() as cur:"""
with open('all_listings.json') as my_file:
    data = json.load(my_file)
    df = pd.DataFrame(data['data'], columns=['domainName', 'link', 'auctionType','auctionEndTime','price','numberOfBids','domainAge','description','pageviews','valuation','monthlyParkingRevenue','isAdult'])
    print(df.shape)
    df['domainAge'] = df['domainAge'].astype('Int64')
    df = df[df['domainName'] != ""]
    print(df.shape)
    df['isAdult'] = (df['isAdult'] == 'True').astype(bool)
    df = df.set_index('domainName')
    df.columns = df.columns.str.lower()
    print(df.iloc[0])
    buffer = StringIO()
    df.iloc[0].to_csv(buffer, index_label='domainName', header=False)
    buffer.seek(0)
    #print(str(buffer.read()))
    cur.copy_from(buffer, "domains", sep=",")
    conn.commit()

            #query_sql = """ insert into domains
            #    select * from json_populate_recordset(NULL::domains, %s) """
            #cur.execute(query_sql, (json.dumps(data['data']),))
    #conn.commit()
