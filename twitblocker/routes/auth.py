from twitblocker import app, db, oauth
from twitblocker.models import AuthUser
from flask import url_for, redirect, session

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.twitter.authorize_access_token()
    url = 'account/verify_credentials.json'
    resp = oauth.twitter.get(url, params={'skip_status': True}).json()
    user = AuthUser()
    user.oauth_token = token['oauth_token']
    user.oauth_token_secret = token['oauth_token_secret']
    user.screen_name = resp['screen_name']
    user.name = resp['name']
    user.user_id = resp['id']
    db_user = AuthUser.by_token(token['oauth_token'])
    if db_user is None:
        db.session.add(user)
    else:
        db_user = user
    db.session.commit()
    session['token'] = token['oauth_token']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
