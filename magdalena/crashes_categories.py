# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import functools
from collections import defaultdict
from datetime import timedelta
from libmozdata import socorro
from libmozdata import utils
from libmozdata.connection import Query
from magdalena import utils as magutils


# reports to process
reports = {
    'startup': {
        'params': {
            'uptime': '<60'
        },
        'process_split': True,
        'desktoponly': False
    },
    'oom': {
        'params': {
            'signature': ['^js::AutoEnterOOMUnsafeRegion::crash', '^OOM |']
        },
        'process_split': True,
        'desktoponly': False
    },
    'oom:small': {
        'params': {
            'signature': '=OOM | small'
        },
        'process_split': True,
        'desktoponly': False
    },
    'oom:large': {
        'params': {
            'signature': '^OOM | large |'
        },
        'process_split': True,
        'desktoponly': False
    },
    'shutdownhang': {
        'params': {
            'signature': '^shutdownhang |'
        },
        'process_split': False,
        'desktoponly': True
    },
    'address:pure': {
        # The signature starts with a "pure" @0xFOOBAR address
        # but not with a prepended "@0x0 |".
        'params': {
            # This doesn't work, see bug 1257376
            # 'signature': ['^@0x', '!^@0x0 |'],
            # For now, take advantage of a leading 0 in addresses
            # is not displayed and include the exact bare @0x0.
            'signature': ['=@0x0',
                          '^@0x1',
                          '^@0x2',
                          '^@0x3',
                          '^@0x4',
                          '^@0x5',
                          '^@0x6',
                          '^@0x7',
                          '^@0x8',
                          '^@0x9',
                          '^@0xa',
                          '^@0xb',
                          '^@0xc',
                          '^@0xd',
                          '^@0xe',
                          '^@0xf']
        },
        'process_split': True,
        'desktoponly': True
    },
    'address:file': {
        # The signature starts with a non-symbolized file@0xFOOBAR
        # piece (potentially after a @0x0 frame).
        'params': {
            # See bug 1257382 for how this drove regex support in Super Search
            # ES regex syntax is documented in
            # https://www.elastic.co/guide/en/elasticsearch/reference/1.4/query-dsl-regexp-query.html#regexp-syntax
            'signature': '@("@0x0 | ")?[^\@\|]+"@0x".*'
            },
        'process_split': True,
        'desktoponly': True
    }
}


def get(product, channel, date='yesterday'):
    yesterday = utils.get_date_ymd(date)
    versions, throttle = magutils.get_versions(yesterday, product, channel)

    def handler(rep, catname, json, data):
        if json['errors'] or not json['facets']['histogram_date']:
            return {}
        else:
            for facets in json['facets']['histogram_date']:
                total = facets['count']
                dt = facets['term']
                if rep['process_split']:
                    nonbrowser = 0
                    pt = facets['facets']['process_type']
                    d = defaultdict(lambda: 0)
                    for pt in facets['facets']['process_type']:
                        ty = pt['term']
                        N = pt['count']
                        d[ty] += int(N * throttle)
                        nonbrowser += N
                    d['browser'] += int((total - nonbrowser) * throttle)
                    data[dt][catname] = dict(d)
                else:
                    data[dt][catname] = int(total * throttle)

    queries = []
    data = defaultdict(lambda: dict())
    today = yesterday + timedelta(days=1)
    search_date = socorro.SuperSearch.get_search_date(yesterday, today)
    for catname, rep in reports.items():
        if rep['desktoponly'] and product != 'Firefox':
            continue
        params = {'product': product,
                  'version': versions,
                  'date': search_date,
                  'release_channel': channel,
                  '_histogram.date': 'process_type',
                  '_facets_size': 5,
                  '_results_number': 0}
        params.update(rep['params'])
        queries.append(Query(socorro.SuperSearch.URL,
                             params,
                             handler=functools.partial(handler, rep, catname),
                             handlerdata=data))

    socorro.SuperSearch(queries=queries).wait()

    return dict(data)
