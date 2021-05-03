from .context import src
import psycopg2
import os

def SedoCollector_gather():
    sedo_collector = src.SedoCollector()
    sedo_collector.gather()

def test_query_tld():
    sedo_collector = src.SedoCollector()
    sedo_data = sedo_collector.fetch_data()
    sedo_df = sedo_collector.preprocess_data(sedo_data)
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "0.0.0.0"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT", 65056),
    )
    sedo_collector.update_tld(conn, sedo_df["tld"].unique())