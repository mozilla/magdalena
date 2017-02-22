# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/categories', methods=['GET'])
@cross_origin()
def categories():
    from magdalena import api
    return api.categories()


@app.route('/bytypes', methods=['GET'])
@cross_origin()
def bytypes():
    from magdalena import api
    return api.bytypes()


@app.route('/annotations', methods=['GET', 'POST'])
@cross_origin()
def annotations():
    from magdalena import api
    return api.annotations()


@app.route('/update', methods=['GET'])
@cross_origin()
def update():
    from magdalena import api
    return api.update()
