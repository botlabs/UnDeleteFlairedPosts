import praw
import requests
import time

# Account settings (private)
USERNAME = ''
PASSWORD = ''

# OAuth settings (private)
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Configuration Settings
USER_AGENT = "UndeleteFlairedPosts for JessicaJones"
SUBREDDIT = "JessicaJones"
AUTH_TOKENS = ["identity","history", "read", "modposts", "submit", "edit"]
MAX_TIME_FLAIRLESS = 60 # Seconds. Amount of time a post can be without flair (to allow user time to set it)
REMOVAL_IDENTIFIER = "[UNFLAIRED]:#" # Used to identify comments removed for being unflaired. I believe this is cleaner than keeping a list.
REMOVAL_MESSAGE = REMOVAL_IDENTIFIER +"\n\n"+ """
This post has been temporarily and automatically removed because it has no assigned flair. It will be unremoved once a flair is assigned.

------------------------------

If you believe this is an error, [contact the subreddit moderators](https://www.reddit.com/message/compose?to=%2Fr%2F{SUBREDDIT}).
""".format(SUBREDDIT=SUBREDDIT)

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

# Determines if the bot has already dealt with this post WRT REMOVAL_IDENTIFIER
def already_replied(post):
    for comment in post.comments:
        if comment.author is None:
            continue
        if comment.author.name.lower() == USERNAME.lower() and comment.body.startswith(REMOVAL_IDENTIFIER):
            return comment
    return None

def main(r):
    while True:
        sub = r.get_subreddit(SUBREDDIT)
        
        # Delete unflaired posts
        for post in sub.get_new(limit=None):
            if post.link_flair_text is None and (post.created_utc >= BOT_START_TIME):
                diff = int(time.time()) - post.created_utc
                if (diff > MAX_TIME_FLAIRLESS) and not already_replied(post):
                    post.add_comment(REMOVAL_MESSAGE)
                    post.remove()
        
        # Undelete flaired posts
        for post in sub.get_spam(limit=None):
            if isinstance(post, praw.objects.Submission) and post.link_flair_text is not None:
                my_comment = already_replied(post)
                if my_comment is not None: # We know it was removed for being unflaired
                    post.approve()
                    my_comment.delete()
        time.sleep(10)

if __name__ == "__main__":
    BOT_START_TIME = int(time.time())
    while True:
        try:
            main(get_praw())
        except praw.errors.OAuthInvalidToken:
            print("OAuth token expired.")
