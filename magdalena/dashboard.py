# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import render_template, request
from datetime import timedelta
from . import utils, models


def render():
    date = utils.get_date(request.args.get('date', 'yesterday'))
    channels = utils.get_channels()

    # Firefox
    adis = []
    versions = []
    browser = []
    content = []
    pluginc = []
    pluginh = []
    b_c = []
    startup = []

    # FennecAndroid
    adis_a = []
    versions_a = []
    b_c_a = []
    startup_a = []

    for chan in channels:
        # Firefox
        data = list(models.Bytype.get('Firefox', chan, date).values())[0]
        adis.append(data['adi'])
        versions.append(data['versions'])
        crashes = data['crashes']
        b = crashes['Browser']
        c = crashes['Content']
        browser.append(b)
        content.append(c)
        pluginc.append(crashes['OOP Plugin'])
        pluginh.append(crashes['Hang Plugin'])
        b_c.append(b + c)

        s = list(models.Categories.get_browser_startup('Firefox',
                                                       chan,
                                                       date).values())[0]
        startup.append(s)

        # FennecAndroid
        data = list(models.Bytype.get('FennecAndroid', chan, date).values())[0]
        adis_a.append(data['adi'])
        versions_a.append(data['versions'])
        crashes = data['crashes']
        b = crashes['Browser']
        c = crashes['Content']
        b_c_a.append(b + c)

        s = list(models.Categories.get_browser_startup('FennecAndroid',
                                                       chan,
                                                       date).values())[0]
        startup_a.append(s)

    table = {'Firefox': {'channel': channels,
                         'adi': adis,
                         'versions': versions,
                         'browser': browser,
                         'content': content,
                         'plugincrash': pluginc,
                         'pluginhang': pluginh,
                         'rateBrCo': b_c,
                         'startup': startup},
             'FennecAndroid': {'channel': channels,
                               'adi': adis_a,
                               'versions': versions_a,
                               'rateBrCo': b_c_a,
                               'startup': startup_a}}

    start = utils.get_date('2016-12-08')
    end = utils.get_date('yesterday')
    duration = (end - start).days
    dates = [(start + timedelta(days=i)).strftime('%Y-%m-%d')
             for i in range(duration, -1, -1)]

    return render_template('dashboard.html',
                           date=date,
                           dates=dates,
                           table=table)
