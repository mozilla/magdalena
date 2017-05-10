# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta
from libmozdata import socorro
from libmozdata import utils
from magdalena import utils as magutils
from magdalena import log


def get(product, channel, date='yesterday'):
    platforms = socorro.Platforms.get_all()
    yesterday = utils.get_date_ymd(date)
    versions, throttle = magutils.get_versions(yesterday, product, channel)

    adi = socorro.ADI.get(version=versions,
                          channel=channel,
                          duration=1,
                          end_date=yesterday,
                          product=product,
                          platforms=platforms)
    adi = list(adi.values())[0]

    if not adi:
        m = 'No ADI for {}::{}::{}, v: {}, p: {}'.format(product,
                                                         channel,
                                                         yesterday,
                                                         ','.join(versions),
                                                         ','.join(platforms))
        log.info(m)
        return []

    def handler(json, data):
        if json['errors'] or not json['facets']['histogram_date']:
            log.info('Error with Supersearch query')
            return []
        else:
            for facets in json['facets']['histogram_date']:
                total = facets['count']
                content = 0
                browser = 0
                oop_plugin = 0
                gpu = 0
                hang_plugin = 0

                for pt in facets['facets']['process_type']:
                    N = pt['count']
                    ty = pt['term']
                    if ty == 'content':
                        content += N
                    elif ty == 'plugin':
                        oop_plugin += N
                    elif ty == 'gpu':
                        gpu += N

                for ph in facets['facets']['plugin_hang']:
                    N = ph['count']
                    ty = ph['term']
                    if ty == 'T':
                        hang_plugin += N

                browser = total - (content + oop_plugin + gpu)
                oop_plugin -= hang_plugin

                browser = int(browser * throttle)
                content = int(content * throttle)
                oop_plugin = int(oop_plugin * throttle)
                gpu = int(gpu * throttle)
                hang_plugin = int(hang_plugin * throttle)
                data.extend([content, browser, hang_plugin, oop_plugin, gpu])

    data = [adi]
    today = yesterday + timedelta(days=1)
    search_date = socorro.SuperSearch.get_search_date(yesterday, today)
    socorro.SuperSearch(params={'product': product,
                                'version': versions,
                                'date': search_date,
                                'release_channel': channel,
                                'submitted_from_infobar': '!__true__',
                                '_histogram.date': ['process_type',
                                                    'plugin_hang'],
                                '_results_number': 0},
                        handler=handler, handlerdata=data).wait()
    data.append(versions)

    return data
