import praw
import time
import traceback
from uuid import uuid4
from bs4 import BeautifulSoup
import urllib.request
import webbrowser
from pprint import pprint



''' User Config
http://praw.readthedocs.io/en/stable/pages/oauth.html#oauth-webserver
'''
app_ua = "FriendsOfFrineds by /u/91_percent_fake"
app_id = "xdZTsHGsR4pjUQ"
app_secret = "OFGwdTEPEiRislfFo2eSr2vM31g"
app_uri = "https://u4ickleviathan.github.io/FriendsOfFriends/"
# app_scopes = "account read"

app_scopres = "account creddits edit flair history identity livemanage modconfig modcontributors modflair modlog modothers modposts modself modwiki mysubreddits privatemessages read report save submit subscribe vote wikiedit wikiread"

WAIT = 60

r = praw.Reddit(user_agent=app_ua)
r.set_oauth_app_info(client_id=app_id,
                     client_secret=app_secret,
                     redirect_uri=app_uri)

comment_object = r.get_submission(submission_id="5669dj")

comment_object.replace_more_comments(limit=None, threshold=0)
