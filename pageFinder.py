import requests
from bs4 import BeautifulSoup
from getsize import getsize

class Post:
    def __init__(self, **kwargs):
        self.id = kwargs.get('no')
        self.country = kwargs.get('country_name')
        self.reply_count = kwargs.get('replies')
        self.subject = kwargs.get('sub')
        self.time_utc = kwargs.get('time')
        self.text = kwargs.get('com')
        self.semantic_url = kwargs.get('semantic_url')
        self.post_url = None

    def set_url(self):
        self.post_url = 'http://boards.4chan.org/pol/thread/'+str(self.id)+'/'+self.semantic_url


class pageFinder:
    def __init__(self):
        self.pol_url = "http://a.4cdn.org/pol/catalog.json"
        self.url_response = requests.get(self.pol_url)
        self.pages = self.url_response.json()
        self.interesting_posts = []
        self.posts = []

    def refresh_catalog(self):
        self.url_response = requests.get(self.pol_url)
        self.pages = self.url_response.json()

    def get_all_posts(self):
        for page in self.pages:
            self.get_threads_on_page(page)

    def get_threads_on_page(self, page):
        for index, thread in enumerate(page['threads']):
            # the first post is a sticked post, so ignor
            if page['page'] == 1 and index == 0:
                self.get_post_info_from_thread(thread, is_sticky_post=True)
            else:
                self.get_post_info_from_thread(thread)

    def get_post_info_from_thread(self, thread, is_sticky_post=False):
        if is_sticky_post:
            pass
        else:
            new_post = Post(**thread)
            new_post.set_url()
            self.posts.append(new_post)



x = pageFinder()
x.get_all_posts()

pass

