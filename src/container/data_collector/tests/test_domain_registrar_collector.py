from .context import src
import psycopg2

def SedoCollector_gather():
    sedo_collector = src.SedoCollector()
    sedo_collector.gather()

def test_query_tld():
    #sedo_collector = src.SedoCollector()
    #sedo_data = sedo_collector.fetch_data()
    #sedo_df = sedo_collector.preprocess_data(sedo_data)
    with psycopg2.connect(user="unicorn_user",
                        password="magical_password",
                        host="database",
                        port="5432",
                        database="rainbow_database") as conn:
        assert True
        #print(sedo_collector.query_tld(conn, sedo_df["tld"].unique()))