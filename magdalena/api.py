# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import request, jsonify
from magdalena import models, log


def categories():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    date = request.args.get('date', '')
    log.info('Get categories for {}::{}::{}'.format(product, channel, date))
    return jsonify(models.Categories.get(product, channel, date))


def bytypes():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    date = request.args.get('date', '')
    log.info('Get bytypes for {}::{}::{}'.format(product, channel, date))
    return jsonify(models.Bytype.get(product, channel, date))


def annotations():
    if request.method == 'GET':
        product = request.args.get('product', 'Firefox')
        channel = request.args.get('channel', 'nightly')
        log.info('Get annotations for {}::{}'.format(product, channel))
        return jsonify(models.Annotations.get(product, channel))
    elif request.method == 'POST':
        log.info('Post annotations')
        return jsonify(models.Annotations.post(request.get_json()))


def lastdate():
    return jsonify(models.Lastdate.get())
