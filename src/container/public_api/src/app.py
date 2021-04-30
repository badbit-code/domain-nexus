import os

from flask import Flask, request

from psycopg2 import connect
from psycopg2.extras import RealDictCursor

conn = connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_DB"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    sslmode='verify-ca',
    sslrootcert="./root.crt"
)

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    print("RUNNING")

    @app.errorhandler(404)
    def page_not_found(e):
        return "<h1>404</h1><p>The resource could not be found.</p>", 404


    @app.route('/api/domains')
    def api_domains():
        """
        term: Search term to use to lookup domains using fuzzy matching
        limit: Limit the number of result that are returned. between 1-499
        page: Return the nth page of results that match this query
        """
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT name,tld from public.domains LIMIT 500")
        rows = cursor.fetchall()

        term = request.args.get("term")
        limit = request.args.get("limit")
        page = request.args.get("page")


        if term is not None:
            return {
                "results":[
                    {"domain_name": f"{row['name']}.{row['tld']}"}
                    for row in rows
                ],
                "current_offset":0,
                "pages":7000,
                "next_page":"x",
                "prev_page":"x"
            }
        else:
            return {
                "results":[
                    {"domain_name": f"{row['name']}.{row['tld']}"}
                    for row in rows
                ],
                "current_offset":0,
                "pages":7000,
                "next_page":"x",
                "prev_page":"x"
            }

    return app

app = create_app()
