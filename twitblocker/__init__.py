""" A small flask Hello World """

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean

import os
import subprocess
import logging
import tweepy
import json


from flask import Flask, jsonify, render_template, send_from_directory
from flask import session, render_template, redirect, url_for
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Load default configuration and any environment variable overrides
_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app.config.from_pyfile(os.path.join(_root_dir, 'config.env.py'))
# Load file based configuration overrides if present
_pyfile_config = os.path.join(_root_dir, 'config.py')
if os.path.exists(_pyfile_config):
    app.config.from_pyfile(_pyfile_config)

logging.getLogger().setLevel('DEBUG')

oauth = OAuth(app)
oauth.register(
    name='twitter',
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
)

db = SQLAlchemy(app)
app.logger.info('SQLAlchemy pointed at ' + repr(db.engine.url))
from .models import *
db.create_all()

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
    if 'token' in session:
        auth_user = AuthUser.by_token(session['token'])
        user_auth = tweepy.auth.OAuthHandler(app.config['TWITTER_CLIENT_ID'], app.config['TWITTER_CLIENT_SECRET'])
        user_auth.set_access_token(auth_user.get_oauth_token(), auth_user.get_oauth_token_secret())
        api = tweepy.API(user_auth)
        user = api.me()
    else:
        user = None
    return render_template('home.html', commit_hash=commit_hash, user=user)


from .routes import auth
