import os

from flask import Flask


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/api/domains')
    def api_domains():
        return {
            "results":[],
            "pages":7000
        }

    return app

