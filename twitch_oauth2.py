from requests_oauthlib import OAuth2Session
from flask import Flask, request, session
import os

# When running locally, disable OAuthlib's HTTPs verification.
# ACTION ITEM for developers:
#     When running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Settings for your app
base_twitch_api_url = 'https://api.twitch.tv/helix'
client_id = 'put here your app client id'  # Get from https://dev.twitch.tv/docs/authentication
client_secret = 'put here your app client secret'  # keep it private
redirect_uri = 'http://localhost:8080/oauth_callback'  # same url must be in OAuth Redirect URL https://dev.twitch.tv/console
scope = ['channel:manage:videos'] # choose scope for your app https://dev.twitch.tv/docs/authentication/#scopes
token_url = 'https://id.twitch.tv/oauth2/token'
authorize_url = 'https://id.twitch.tv/oauth2/authorize'
revoke_url = 'https://id.twitch.tv/oauth2/revoke'
force_verify = True

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def home():
    """
    Presents the 'Login with Twitch' link
    """
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url, force_verify=force_verify)
    session['state'] = state

    print("Login url: %s" % login_url)

    return '<a href="' + login_url + '">Login with Twitch</a>'


@app.route("/oauth_callback")
def oauth_callback():
    """
    for more info see https://dev.twitch.tv/docs/authentication/getting-tokens-oauth
    """
    twitch = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['state'], scope=scope)

    token = twitch.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    session['access_token'] = token

    return 'Thanks for granting us authorization. We are logging you in! You can now visit <a ' \
           'href="/user">/user</a> '


@app.route("/user")
def profile():
    """
    Example user page to demonstrate how to pull the user information
    once we have a valid access token after all OAuth negotiation.
    """
    twitch = OAuth2Session(client_id, token=session['access_token'])
    response = twitch.get(base_twitch_api_url + '/users/', headers={'Client-Id': client_id})

    return 'Profile: %s' % response.json()


@app.route('/logout')
def logout():
    # log out can be made in your twitch account page https://www.twitch.tv/settings/connections
    # find your app name and press Disconnect button
    pass


# To run this app
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
