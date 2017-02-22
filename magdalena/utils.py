# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import dateutil.parser
from libmozdata import utils
from libmozdata import socorro


def check_product(p):
    return p in ['Firefox', 'FennecAndroid']


def check_channel(c):
    return c in ['nightly', 'aurora', 'beta', 'release', 'esr']


def check_date(d):
    d = utils.get_date_ymd(d)
    today = utils.get_date_ymd('today')

    return d <= today


def getMaxBuildAge():
    return {'release': 12,
            'beta': 4,
            'aurora': 9,
            'nightly': 9}


def get_all_versions(product, mindate):
    all_versions = []

    def handler(json):
        all_versions.extend(json['hits'])

    socorro.ProductVersions(params={'product': product,
                                    'start_date': '>' + mindate,
                                    'is_rapid_beta': False},
                            handler=handler).wait()

    return all_versions


def get_date(date):
    if date:
        try:
            return dateutil.parser.parse(date)
        except:
            pass
    return None
