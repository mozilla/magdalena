# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import json


url = 'http://foo.bar.com/{}?product={}&channel={}'
products = ['Firefox', 'FennecAndroid']
channels = ['nightly', 'beta', 'release']
meths = ['categories', 'bytypes', 'annotations']

for p in products:
    for c in channels:
        for m in meths:
            response = requests.get(url.format(m, p, c))
            with open('{}-{}-{}.json'.format(p, c, m), 'w') as Out:
                json.dump(response.json(), Out)
