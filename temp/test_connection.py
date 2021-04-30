import json
import psycopg2


with psycopg2.connect(user="unicorn_user",
                        password="magical_password",
                        host="127.0.0.1",
                        port="56105",
                        database="rainbow_database") as conn:
    with conn.cursor() as cur:
        with open('all_listings.json') as my_file:
            data = json.load(my_file)
            cur.execute(""" create table if not exists json_table(
                p_id integer, first_name text, last_name text, p_attribute jsonb,
                quote_content text) """)
            query_sql = """ insert into json_table
                select * from json_populate_recordset(NULL::json_table, %s) """
            cur.execute(query_sql, (json.dumps(data),))
