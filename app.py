# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import jsonify
from magdalena import api
from magdalena import app
from magdalena import db


@app.route('/categories', methods=['GET'])
def categories():
    return jsonify(api.categories())


@app.route('/bytype', methods=['GET'])
def bytype():
    return jsonify(api.bytype())


@app.route('/annotations', methods=['GET', 'POST'])
def annotations():
    return jsonify(api.annotations())


@app.route('/update', methods=['GET'])
def update():
    return jsonify(api.update())


engine = db.get_engine(app)
if not engine.dialect.has_table(engine, 'crashes_bytype'):
    import requests
    from magdalena import models

    print('Generate tables')
    products = ['Firefox', 'FennecAndroid']
    channels = ['nightly', 'aurora', 'beta', 'release']
    types = {'crashes-bytype': models.Bytype,
             'crashes-categories': models.Categories,
             'annotations': models.Annotations}

    db.create_all()

    base_url = 'https://crash-analysis.mozilla.com/rkaiser/{}-{}-{}.json'
    for product in products:
        for channel in channels:
            for typ, obj in types.items():
                url = base_url.format(product, channel, typ)
                print('Get data from {}'.format(url))
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    obj.populate(product, channel, data)
