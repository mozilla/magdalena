# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
import six
import sys
from libmozdata import utils
from libmozdata import socorro


def get_products():
    return ['Firefox', 'FennecAndroid']


def check_product(p):
    return p in get_products()


def get_channels():
    return ['nightly', 'aurora', 'beta', 'release']


def check_channel(c):
    return c in get_channels()


def disp(*args):
    print(args)
    sys.stdout.flush()


def check_date(d):
    d = get_date(d)
    today = get_date('today')

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


def get_versions(date, product, channel):
    earliest_mindate = utils.get_date_str(date - datetime.timedelta(days=365))
    all_versions = get_all_versions(product, earliest_mindate)
    delta = datetime.timedelta(weeks=getMaxBuildAge()[channel])
    min_version_date = utils.get_date_ymd(date) - delta
    versions = []
    throttle = 0
    last_versions = None
    last_throttle = 0
    last_date = utils.get_guttenberg_death()
    for v in all_versions:
        if v['product'] == product and v['build_type'] == channel:
            sd = utils.get_date_ymd(v['start_date'])
            if sd > last_date:
                last_date = sd
                last_versions = v['version']
                last_throttle = 100. / float(v['throttle'])

            if sd > min_version_date:
                versions.append(v['version'])
                if throttle == 0:
                    throttle = 100. / float(v['throttle'])

    if not versions:
        versions = last_versions
        throttle = last_throttle

    return versions, throttle


def get_date(date):
    if date:
        try:
            if isinstance(date, six.string_types):
                date = utils.get_date_ymd(date)
                return datetime.date(date.year, date.month, date.day)
            elif isinstance(date, datetime.date):
                return date
            elif isinstance(date, datetime.datetime):
                return datetime.date(date.year, date.month, date.day)
        except:
            pass
    return None
