import praw
import requests

# Account settings (private)
USERNAME = ''
PASSWORD = ''

# OAuth settings (private)
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Configuration Settings
USER_AGENT = "JessicaJones UndeleteFlairedPosts"
SUBREDDIT = "JessicaJones"
AUTH_TOKENS = ["identity","history", "read", "modposts"]


def get_access_token():
    response = requests.post("https://www.reddit.com/api/v1/access_token",
      auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
      data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD},
      headers = {"User-Agent": USER_AGENT})
    return dict(response.json())["access_token"]

def get_praw():
    r = praw.Reddit(USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    r.set_access_credentials(set(AUTH_TOKENS), get_access_token())
    return r

def main(r):
    sub = r.get_subreddit(SUBREDDIT)
    for post in sub.get_spam(limit=None):
        # TODO if post has a comment saying the post was removed for being unflaired
        if post.link_flair_text is not None:
            post.approve()
    exit()

if __name__ == "__main__":
    try:
        main(get_praw())
    except praw.errors.OAuthInvalidToken:
        print("OAuth token expired.")
