# ！/usr/bin/env python
# _*_ coding:utf-8 _*_

'''

@author: yerik

@contact: xiangzz159@qq.com

@time: 2018/4/18 11:06

@desc: python启动入口

'''

import numpy as np
import json
import flask
import flask_graphql
from flask_cors import CORS
import api
import config
import mutations
import jsonify
from auths import Auth
from flask_httpauth import HTTPTokenAuth


# NumpyEncoder: useful for JSON serializing
# Dictionaries that contain Numpy Arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)


app = flask.Flask(__name__)
app.debug = True
app.json_encoder = NumpyEncoder

cors = CORS(app)

auth = HTTPTokenAuth()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    if flask.request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = flask.request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


# 请求前拦截
@app.before_request
def befor_request():
    if config.BEFOR_REQUEST:
        if '/graphql' in flask.request.url:
            result = Auth.identify(Auth, flask.request)
            if result['status'] == False:
                return str(result)


@app.route('/')
def index():
    return flask.redirect("/graphql", code=302)


@app.route('/apps/')
def apps():
    return "Apps: flask_graphql_example"


@app.route('/login', methods=['POST'])
def login():
    email = flask.request.form.get('email')
    password = mutations.encryption_md5(flask.request.form.get('password'))
    if (not email or not password):
        return jsonify(config.falseReturn('', '用户名和密码不能为空'))
    else:
        return Auth.authenticate(Auth, email, password)


def graphql_view():
    view = flask_graphql.GraphQLView.as_view(
        'graphql',
        schema=api.schema,
        graphiql=True,
        context={
            'session': config.db_session,
        }
    )
    return view


# Graphql view
app.add_url_rule('/graphql',
                 view_func=graphql_view()
                 )

if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-s',
                      '--debug-sql',
                      help="Print executed SQL statement to commandline",
                      dest="debug_sql",
                      action="store_true",
                      default=False)

    options, args = parser.parse_args()

    import logging

    logging.basicConfig()

    if options.debug_sql:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    #    else:
    #        from raven.contrib.flask import Sentry
    #        sentry = Sentry(app, logging=True, level=logging.WARN)

    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT)
