import os

from flask import Flask, request

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    @app.errorhandler(404)
    def page_not_found(e):
        return "<h1>404</h1><p>The resource could not be found.</p>", 404


    @app.route('/api/domains')
    def api_domains():
        """
        term : Search term to use to lookup domains using fuzzy matching
        limit: Limit the number of result that are returned. between 1-499
        page: Return the nth page of results that match this query
        """

        term = request.args.get("term")
        limit = request.args.get("limit")
        page = request.args.get("page")

        if term is not None:
            return {
                "results":[
                    {"name":"tacojohns"}
                ],
                "current_offset":0,
                "pages":7000,
                "next_page":"x",
                "prev_page":"x"
            }
        else:
            return {
                "results":[
                    {"name":"boston"}
                ],
                "current_offset":0,
                "pages":7000,
                "next_page":"x",
                "prev_page":"x"
            }

    return app

