""" A small flask Hello World """

import os
import subprocess

from flask import Flask, jsonify, render_template, send_from_directory
from flask import session, render_template, redirect, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)

# Load default configuration and any environment variable overrides
_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app.config.from_pyfile(os.path.join(_root_dir, 'config.env.py'))
# Load file based configuration overrides if present
_pyfile_config = os.path.join(_root_dir, 'config.py')
if os.path.exists(_pyfile_config):
    app.config.from_pyfile(_pyfile_config)

oauth = OAuth(app)
oauth.register(
    name='twitter',
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
)

# grab the commit hash once on startup, if possible
commit_hash = None
try:
    commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']) \
        .strip() \
        .decode('utf-8')
# pylint: disable=bare-except
except:
    pass


@app.route('/static/<path:path>', methods=['GET'])
def _send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def _index():
    if 'user' in session:
        user = session['user']
    else:
        user = None
    return render_template('home.html', commit_hash=commit_hash, user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.twitter.authorize_access_token()
    url = 'account/verify_credentials.json'
    resp = oauth.twitter.get(url, params={'skip_status': True})
    user = resp.json()
    session['user'] = user
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
