# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import Flask, send_from_directory
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import flask
import logging
import os
import httplib2
from oauth2client import client, clientsecrets
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = os.environ.get('SESSION_KEY')
log = logging.getLogger(__name__)
mod_path = os.path.dirname(__file__)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    return r

def check_credentials():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
 
    credentials = flask.session['credentials']
    credentials = client.OAuth2Credentials.from_json(credentials)
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))


@app.route('/categories', methods=['GET'])
@cross_origin()
def categories():
    r = check_credentials()
    if r:
        return r
    from magdalena import api
    return api.categories()


@app.route('/bytypes', methods=['GET'])
@cross_origin()
def bytypes():
    r = check_credentials()
    if r:
        return r
    from magdalena import api
    return api.bytypes()


@app.route('/annotations', methods=['GET', 'POST'])
@cross_origin()
def annotations():
    r = check_credentials()
    if r:
        return r
    from magdalena import api
    return api.annotations()


@app.route('/lastdate', methods=['GET'])
@cross_origin()
def lastdate():
    r = check_credentials()
    if r:
        return r
    from magdalena import api
    return api.lastdate()


@app.route('/longtermgraph/<path:file>')
def longtermgraph(file):
    r = check_credentials()
    if r:
        return r
    return send_from_directory('../static/longtermgraph', file)


@app.route('/dashboard/<path:file>')
@app.route('/dashboard/')
def dashboard_static(file=''):
    r = check_credentials()
    if r:
        return r
    for f in ['dashboard.js', 'dashboard.css']:
        if file.endswith(f):
            return send_from_directory('../static/dashboard', f)
    return dashboard_dyn()


@app.route('/')
@app.route('/dashboard')
def dashboard_dyn():
    r = check_credentials()
    if r:
        return r
    from magdalena import dashboard
    return dashboard.render()


@app.errorhandler(401)
def custom_401(error):
    return flask.Response('You\'re not allowed to access to this page.',
                          401,
                          {'WWWAuthenticate': 'Basic realm="Login Required"'})


@app.route('/logout')
def logout():
    # Delete the user's profile and the credentials stored by oauth2.
    credentials = flask.session.pop('credentials', None)
    if credentials:
        credentials = client.OAuth2Credentials.from_json(credentials)
        try:
            credentials.revoke(httplib2.Http())
        except TokenRevokeError:
            pass
        flask.session.modified = True

    return send_from_directory('../static/dashboard', 'logout.html')


@app.route('/oauth2callback')
def oauth2callback():
    # client_secrets.json is got from https://console.developers.google.com

    class AuthCache(object):

        def get(self, filename, namespace=''):
            CSJ = 'client_secrets.json'
            OSNS = 'oauth2client:secrets#ns'
            if filename == CSJ and namespace == OSNS:
                c_secrets = os.environ.get('CLIENT_SECRETS', '')
                if c_secrets:
                    c_type, c_info = clientsecrets.loads(c_secrets)
                    return {c_type: c_info}
            return None

    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='email',
        cache=AuthCache(),
        redirect_uri=flask.url_for('oauth2callback', _external=True))

    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)

    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    email = credentials.id_token['email']
    pats = os.environ.get('AUTHORIZED_USERS', '')
    if pats:
        pats = pats.split(';')
        pats = map(lambda p: p.strip(' '), pats)
        pats = filter(lambda p: p is not '', pats)
        if any(re.match(pat, email) for pat in pats):
            flask.session['credentials'] = credentials.to_json()
            return flask.redirect(flask.url_for('dashboard_dyn'))

    flask.abort(401)
