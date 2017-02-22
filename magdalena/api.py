# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import request, jsonify
from magdalena import models


def categories():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    date = request.args.get('date', '')
    return jsonify(models.Categories.get(product, channel, date))


def bytypes():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    date = request.args.get('date', '')
    return jsonify(models.Bytype.get(product, channel, date))


def annotations():
    if request.method == 'GET':
        product = request.args.get('product', 'Firefox')
        channel = request.args.get('channel', 'nightly')
        return jsonify(models.Annotations.get(product, channel))
    elif request.method == 'POST':
        return jsonify(models.Annotations.post(request.get_json()))


def update():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    date = request.args.get('date', 'yesterday')
    r1 = models.Bytype.update(product, channel, date)
    r2 = models.Categories.update(product, channel, date)

    return jsonify('ok' if r1 and r2 else 'error')


def lastdate():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    return jsonify(models.Bytype.lastdate(product, channel))
