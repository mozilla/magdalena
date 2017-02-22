# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import dateutil.parser
from datetime import datetime, date, timedelta
from collections import defaultdict
from libmozdata import utils
from magdalena import utils as magutils
from magdalena import app, db, crashes_bytype, crashes_categories


class Categories(db.Model):
    __tablename__ = 'crashes_categories'

    product = db.Column(db.String(20), primary_key=True)
    channel = db.Column(db.String(20), primary_key=True)
    date = db.Column(db.Date(), primary_key=True)
    kind = db.Column(db.String(20), primary_key=True)
    content = db.Column(db.Integer, default=0)
    browser = db.Column(db.Integer, default=0)
    plugin = db.Column(db.Integer, default=0)

    def __init__(self, product, channel, date, kind, content, browser, plugin):
        self.product = product
        self.channel = channel
        self.date = dateutil.parser.parse(date)
        self.kind = kind
        self.content = content
        self.browser = browser
        self.plugin = plugin

    @staticmethod
    def put_data(product, channel, date, data, commit=True):
        if data:
            for kind, nums in data.items():
                if kind == 'shutdownhang':
                    content = 0
                    browser = nums
                    plugin = 0
                else:
                    content = int(nums.get('content', 0))
                    browser = int(nums.get('browser', 0))
                    plugin = int(nums.get('plugin', 0))

                Categories.put(product,
                               channel,
                               date,
                               kind,
                               content,
                               browser,
                               plugin,
                               update=True,
                               commit=False)
            if commit:
                db.session.commit()

            return True
        return False

    @staticmethod
    def update(product, channel, date):
        data = crashes_categories.get(product, channel, date=date)
        return Categories.put_data(product, channel, date, data)

    @staticmethod
    def check(product, channel):
        yesterday = date.today() - timedelta(days=1)
        cats = db.session.query(Categories).filter_by(product=product,
                                                      channel=channel,
                                                      date=yesterday)
        if not cats.first():
            Categories.update(product, channel, utils.get_date(yesterday))

    @staticmethod
    def get(product, channel, date):
        Categories.check(product, channel)
        date = magutils.get_date(date)
        if date:
            cats = db.session.query(Categories).filter_by(product=product,
                                                          channel=channel,
                                                          date=date)
        else:
            cats = db.session.query(Categories).filter_by(product=product,
                                                          channel=channel)
        r = defaultdict(lambda: dict())
        for cat in cats:
            kind = cat.kind
            date = utils.get_date_str(cat.date)
            if kind == 'shutdownhang':
                r[date]['shutdownhang'] = cat.browser
            else:
                r[date][kind] = {'content': cat.content,
                                 'browser': cat.browser,
                                 'plugin': cat.plugin}

        return dict(r)

    @staticmethod
    def put(product, channel, date, kind, content, browser, plugin,
            commit=True, update=False):
        cat = None
        if update:
            cats = db.session.query(Categories).filter_by(product=product,
                                                          channel=channel,
                                                          date=date,
                                                          kind=kind)
            if cats.first():
                cat = cats.first()
                cat.content = content
                cat.browser = browser
                cat.plugin = plugin
        if not cat:
            cat = Categories(product, channel, date,
                             kind, content, browser, plugin)

        db.session.add(cat)
        if commit:
            db.session.commit()

    @staticmethod
    def populate(product, channel, data):
        for date, info in data.items():
            Categories.put_data(product, channel, date, info, commit=False)

        db.session.commit()


class Bytype(db.Model):
    __tablename__ = 'crashes_bytype'

    product = db.Column(db.String(20), primary_key=True)
    channel = db.Column(db.String(20), primary_key=True)
    date = db.Column(db.Date(), primary_key=True)
    adi = db.Column(db.Integer, default=0)
    content = db.Column(db.Integer, default=0)
    browser = db.Column(db.Integer, default=0)
    hang_plugin = db.Column(db.Integer, default=0)
    oop_plugin = db.Column(db.Integer, default=0)
    gpu = db.Column(db.Integer, default=0)
    versions = db.Column(db.String(256))

    def __init__(self, product, channel, date, adi, content,
                 browser, hang_plugin, oop_plugin, gpu, versions):
        self.product = product
        self.channel = channel
        self.date = dateutil.parser.parse(date)
        self.adi = adi
        self.content = content
        self.browser = browser
        self.hang_plugin = hang_plugin
        self.oop_plugin = oop_plugin
        self.gpu = gpu
        self.versions = '|'.join(versions)

    @staticmethod
    def update(product, channel, date):
        data = crashes_bytype.get(product, channel, date=date)
        if data:
            data = (product, channel, date) + tuple(data)
            Bytype.put(*data, update=True)
            return True
        return False

    @staticmethod
    def check(product, channel):
        yesterday = date.today() - timedelta(days=1)
        bts = db.session.query(Bytype).filter_by(product=product,
                                                 channel=channel,
                                                 date=yesterday)
        if not bts.first():
            Bytype.update(product, channel, utils.get_date(yesterday))

    @staticmethod
    def get(product, channel, date):
        Bytype.check(product, channel)
        date = magutils.get_date(date)
        if date:
            bytype = db.session.query(Bytype).filter_by(product=product,
                                                        channel=channel,
                                                        date=date)
        else:
            bytype = db.session.query(Bytype).filter_by(product=product,
                                                        channel=channel)
        r = {}
        for bt in bytype:
            date = utils.get_date_str(bt.date)
            r[date] = {'adi': bt.adi,
                       'crashes': {'Content': bt.content,
                                   'OOP Plugin': bt.oop_plugin,
                                   'Hang Plugin': bt.hang_plugin,
                                   'Browser': bt.browser,
                                   'Gpu': bt.gpu},
                       'versions': bt.versions.split('|')}

        return r

    @staticmethod
    def put(product, channel, date, adi, content,
            browser, hang_plugin, oop_plugin, gpu,
            versions, commit=True, update=False):
        bt = None
        if update:
            bts = db.session.query(Bytype).filter_by(product=product,
                                                     channel=channel,
                                                     date=date)
            if bts.first():
                bt = bts.first()
                bt.adi = adi
                bt.content = content
                bt.browser = browser
                bt.hang_plugin = hang_plugin
                bt.oop_plugin = oop_plugin
                bt.gpu = gpu
                bt.versions = '|'.join(versions)
        if not bt:
            bt = Bytype(product, channel, date,
                        adi, content, browser,
                        hang_plugin, oop_plugin, gpu, versions)

        db.session.add(bt)
        if commit:
            db.session.commit()

    @staticmethod
    def lastdate(product, channel):
        lastdate = db.session.query(db.func.max(Bytype.date)).scalar()
        lastdate = utils.get_date_str(lastdate)
        return {"lastdate": lastdate}

    @staticmethod
    def populate(product, channel, data):
        for date, info in data.items():
            adi = int(info.get('adi', 0))
            versions = info.get('versions', list())
            crashes = info.get('crashes', dict())
            if isinstance(crashes, dict):
                content = int(crashes.get('Content', 0))
                browser = int(crashes.get('Browser', 0))
                hang_plugin = int(crashes.get('Hang Plugin', 0))
                oop_plugin = int(crashes.get('OOP Plugin', 0))
                gpu = int(crashes.get('Gpu', 0))
            else:
                content = 0
                browser = 0
                hang_plugin = 0
                oop_plugin = 0
                gpu = 0

            Bytype.put(product, channel, date, adi,
                       content, browser, hang_plugin,
                       oop_plugin, gpu, versions, commit=False)

        db.session.commit()


class Annotations(db.Model):
    __tablename__ = 'annotations'

    product = db.Column(db.String(20), primary_key=True)
    channel = db.Column(db.String(20), primary_key=True)
    series = db.Column(db.String(64), primary_key=True)
    x = db.Column(db.String(20), primary_key=True)
    shortText = db.Column(db.String(20))
    text = db.Column(db.String(256))
    created_date = db.Column(db.DateTime(timezone=True),
                             default=datetime.utcnow)

    def __init__(self, product, channel, series, x, shortText, text):
        self.product = product
        self.channel = channel
        self.series = series
        self.x = x
        self.shortText = shortText
        self.text = text

    @staticmethod
    def get(product, channel):
        annotations = db.session.query(Annotations).filter_by(product=product,
                                                              channel=channel)
        r = []
        for annotation in annotations:
            r.append({'series': annotation.series,
                      'x': annotation.x,
                      'shortText': annotation.shortText,
                      'text': annotation.text})

        return r

    @staticmethod
    def put(product, channel, series, x, shortText, text, commit=True):
        annotation = Annotations(product, channel, series, x, shortText, text)
        db.session.add(annotation)
        if commit:
            db.session.commit()

    @staticmethod
    def post(data):
        product = data.get('product', '')
        channel = data.get('channel', '')
        series = data.get('series', '')
        x = data.get('x', '')
        shortText = data.get('shortText', '')
        text = data.get('text', '')
        if magutils.check_product(product) and \
           magutils.check_channel(channel) and \
           series and magutils.check_date(x) and \
           shortText:
            anns = db.session.query(Annotations).filter_by(product=product,
                                                           channel=channel,
                                                           series=series,
                                                           x=x)
            if anns.first():
                annotation = anns.first()
                annotation.shortText = shortText
                annotation.text = text
            else:
                annotation = Annotations(product,
                                         channel,
                                         series,
                                         x,
                                         shortText,
                                         text)

            db.session.add(annotation)
            db.session.commit()
            return 'ok'
        else:
            return 'error'

    @staticmethod
    def populate(product, channel, data):
        for info in data:
            series = info.get('series', '')
            x = info.get('x', '')
            shortText = info.get('shortText', '')
            text = info.get('text', '')
            if series and x and shortText:
                Annotations.put(product,
                                channel,
                                series,
                                x,
                                shortText,
                                text,
                                commit=False)

        db.session.commit()


def fill_tables():
    engine = db.get_engine(app)
    if not engine.dialect.has_table(engine, 'crashes_bytype'):
        import requests

        print('Generate tables')
        products = ['Firefox', 'FennecAndroid']
        channels = ['nightly', 'aurora', 'beta', 'release']
        types = {'crashes-bytype': Bytype,
                 'crashes-categories': Categories,
                 'annotations': Annotations}

        db.create_all()

        base_url = 'https://crash-analysis.mozilla.com/rkaiser/{}-{}-{}.json'
        for product in products:
            for channel in channels:
                for typ, obj in types.items():
                    url = base_url.format(product, channel, typ)
                    print('Get data from {}'.format(url))
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        obj.populate(product, channel, data)
