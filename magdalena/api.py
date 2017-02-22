# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import request
from . import models
from . import crashes_bytype
from . import crashes_categories


def categories():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    return models.Categories.get(product, channel)


def bytype():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    return models.Bytype.get(product, channel)


def annotations():
    if request.method == 'GET':
        product = request.args.get('product', 'Firefox')
        channel = request.args.get('channel', 'nightly')
        return models.Annotations.get(product, channel)
    elif request.method == 'POST':
        return models.Annotations.post(request.get_json())


def update():
    product = request.args.get('product', 'Firefox')
    channel = request.args.get('channel', 'nightly')
    date = request.args.get('date', 'yesterday')
    r1 = crashes_bytype.update(product, channel, date)
    r2 = crashes_categories.update(product, channel, date)

    return r1 if r1 == r2 else 'error'
