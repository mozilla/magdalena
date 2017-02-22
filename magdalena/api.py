# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import request, jsonify
from magdalena import models
from magdalena import crashes_bytype
from magdalena import crashes_categories


def categories():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    return jsonify(models.Categories.get(product, channel))


def bytypes():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    return jsonify(models.Bytype.get(product, channel))


def annotations():
    if request.method == 'GET':
        product = request.args.get('product', 'Firefox')
        channel = request.args.get('channel', 'nightly')
        return jsonify(models.Annotations.get(product, channel))
    elif request.method == 'POST':
        return jsonify(models.Annotations.post(request.get_json()))


def update():
    product = request.args.get('product', None)
    channel = request.args.get('channel', None)
    date = request.args.get('date', 'yesterday')
    if not product or not channel:
        for p in ['Firefox', 'FennecAndroid']:
            for c in ['nightly', 'aurora', 'beta', 'release']:
                r1 = crashes_bytype.update(p, c, date)
                r2 = crashes_categories.update(p, c, date)

    return jsonify(r1 if r1 == r2 else 'error')


def lastdate():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    return jsonify(models.Bytype.lastdate(product, channel))
