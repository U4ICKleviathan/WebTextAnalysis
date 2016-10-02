__author__ = 'Ian'
import urllib
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
import bs4
import os
from datetime import datetime, timedelta
import shutil
import time
import threading
import inspect
from getsize import getsize
import lxml

list_of_websites = [
    "http://boards.4chan.org/pol/thread/90962775/btfo",
    "http://boards.4chan.org/pol/thread/90985328/happening-the-end-is-nigh",
    "http://boards.4chan.org/pol/thread/90985993/there-are-people-on-pol-right-now-that-do-not-own",
]

website = "http://boards.4chan.org/pol/thread/91113226/how-do-we-fix-low-testosterone-in-boys"

"""
https://github.com/4chan/4chan-API
"""
bad_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]


def build_name(potential_name):
    built_name = ''
    for i in potential_name:
        if i in bad_characters:
            pass
        else:
            built_name = built_name + i
            if len(built_name) > 15:
                return built_name
    return built_name


class Response:
    def __index__(self):
        self.country = ""
        self.time_human = ""
        self.time_utc = 0
        self.text = ""
        self.time_object = None
        self.op_subject = None
        self.user_id = 0
        self.post_id = ''
        self.image_url = None
        self.image_name = None
        self.country = None

    def parse_line(self, line):
        if 'text:' in line[:10]:
            self.text = line[7:].strip()
        elif 'country: ' in line[:9]:
            self.country = line[8:].strip()
        elif 'time_human: ' in line[:15]:
            self.time_human = line[12:].strip()
        elif 'time_utc: ' in line[:15]:
            self.time_utc = int(line[10:].strip())
            self.time_object = datetime.fromtimestamp(self.time_utc)
        pass

    def time_bucket_string(self, bucket_size):
        if bucket_size == 'minute':
            return str(
                datetime(self.time_object.year, self.time_object.month, self.time_object.day, self.time_object.hour,
                         self.time_object.minute))
        elif bucket_size == 'hour':
            return str(
                datetime(self.time_object.year, self.time_object.month, self.time_object.day, self.time_object.hour))
        elif bucket_size == 'day':
            return str(datetime(self.time_object.year, self.time_object.month, self.time_object.day))
        elif bucket_size == 'second':
            return str(
                datetime(self.time_object.year, self.time_object.month, self.time_object.day, self.time_object.hour,
                         self.time_object.minute, self.time_object.second))
        elif bucket_size == 'quarter_second':
            rounded_time = self.time_object - timedelta(seconds=self.time_object.second % 15)
            return str(datetime(rounded_time.year, rounded_time.month, rounded_time.day, rounded_time.hour,
                                rounded_time.minute, rounded_time.second))
        elif bucket_size == '10_second':
            rounded_time = self.time_object - timedelta(seconds=self.time_object.second % 10)
            return str(datetime(rounded_time.year, rounded_time.month, rounded_time.day, rounded_time.hour,
                                rounded_time.minute, rounded_time.second))


class scraperThread(threading.Thread):
    def __init__(self, threadId, website):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.website = website

    def run(self):
        print("Starting " + self.website)
        download_until_it_dies(self.threadId, self.website)
        print("Exiting " + self.website)


class ChanScrapper(object):
    def __init__(self, threadId, website):
        self.threadId = threadId
        self.url = website
        self.soup = None
        self.responses = []
        self.saved_post_ids = []
        self.directory_name = None
        self.sub_directory = None
        self.output_file = None
        pass

    def get_soup(self):
        r = requests.get(self.url)
        self.soup = BeautifulSoup(r.text, 'html.parser')

    def strip_responses(self):
        self.get_soup()
        self.add_op_post()
        self.create_outfile()
        self.add_thread_responses()

    def add_op_post(self):
        post = self.soup.find_all(class_="post op")[0]
        op_post = Response()
        op_post.op_subject = self.get_post_subject(post)
        op_post.time_human = self.get_post_human_time(post)
        op_post.time_utc = self.get_post_time_utc(post)
        op_post.user_id = self.get_post_user_id(post)
        op_post.post_id = self.get_post_id(post)
        op_post.country = self.get_post_country(post)
        op_post.text = self.get_post_text(post)
        op_post.image_url = self.get_post_image_url(post)
        op_post.image_name = self.get_post_image_name(post)
        self.responses.append(op_post)

    def add_thread_responses(self):
        all_replies = self.soup.find_all(class_="post reply")
        for reply in all_replies:
            next_response = self.strip_reply_data(reply)
            self.responses.append(next_response)

    def strip_reply_data(self, reply):
        response = Response()
        response.time_human = self.get_post_human_time(reply)
        response.time_utc = self.get_post_time_utc(reply)
        response.user_id = self.get_post_user_id(reply)
        response.post_id = self.get_post_id(reply)
        response.country = self.get_post_country(reply)
        response.text = self.get_post_text(reply)
        response.image_url = self.get_post_image_url(reply)
        response.image_name = self.get_post_image_name(reply)
        return response

    def get_post_subject(self, post):
        return post.find_all(class_='subject')[1].text

    def get_post_human_time(self, post):
        return post.find_all(class_='dateTime')[1].text

    def get_post_time_utc(self, post):
        return post.find_all(class_='dateTime')[0]['data-utc']

    def get_post_user_id(self, post):
        return post.find_all(class_="hand")[0].text

    def get_post_id(self, post):
        return post.find_all('input')[0]['name']

    def get_post_country(self, post):
        return post.find_all(class_="flag")[0]['title']

    def get_post_text(self, post):
        post_text = ''
        post_message = post.find_all(class_='postMessage')[0]
        for line in post_message.contents:
            if isinstance(line, bs4.element.NavigableString):
                post_text = post_text + " " + line
            elif isinstance(line, bs4.element.Tag):
                post_text = post_text + " " + line.text
        return post_text

    def get_post_image_url(self, post):
        if len(post.find_all(class_='file')) != 0:
            try:
                file_data = post.find_all(class_='fileText')[0]
                return 'http:' + file_data.find_all('a', href=True)[0]['href']
            except IndexError:
                return None
        else:
            return None

    def get_post_image_name(self, post):
        if len(post.find_all(class_='file')) != 0:
            try:
                file_data = post.find_all(class_='fileText')[0]
                return file_data.find_all('a', href=True)[0].text
            except IndexError:
                file = post.find_all(class_='file')[0]
                return file.img['alt']
        else:
            return None

    def check_if_page_is_closed(self):
        if len(self.soup.find_all(class_='closed')) > 0:
            return True
        else:
            False

    def set_directory(self, name):
        cwd = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
        new_directory_name = cwd + "\\" + name + "\\"
        os.makedirs(new_directory_name, exist_ok=True)
        self.directory_name = new_directory_name

    def set_sub_directory(self):
        sub_directory_name = self.directory_name + "\\" + self.output_file + "\\"
        os.makedirs(sub_directory_name, exist_ok=True)
        self.sub_directory = sub_directory_name
        pass

    def create_outfile(self):
        doc_title = ""
        if len(self.responses[0].op_subject) <= 1:
            doc_title = build_name(self.responses[0].image_name)
        else:
            doc_title = build_name(self.responses[0].op_subject)
        self.output_file = doc_title

    def save_image_to_file(self, response):
        if response.image_url[:2] == '//':
            url = "http:" + response.image_url
        else:
            url = response.image_url
        imr = requests.get(url, stream=True)
        if imr.status_code == 200:
            name = ''
            for letter in response.image_name:
                if letter in bad_characters:
                    pass
                else:
                    name += letter
            with open(self.sub_directory + name, "wb") as f:
                imr.raw.decode_content = True
                shutil.copyfileobj(imr.raw, f)

    def write_responses_to_file(self, save_images=True):
        self.set_directory("scrapped_pages")
        self.set_sub_directory()
        for index, reply in enumerate(self.responses):
            if index == 0:
                self.save_op_post(reply, save_images)
            else:
                self.save_response(reply, save_images)
        self.collect_saved_ids()
        print("Thread %s: Added %d original posts" % (self.output_file, index))

    def save_op_post(self, op_post, save_image=True):
        file = open(self.directory_name + self.output_file + '.txt', "a")
        file.write("post_id: {0}\n".format(op_post.post_id))
        file.write("time_human: {0}\n".format(op_post.time_human))
        file.write("image: {0}\nimage_url {1}\n".format(op_post.image_name, op_post.image_url))
        if save_image:
            self.save_image_to_file(op_post)
        file.write("subject: {0}\n".format(op_post.op_subject))
        file.write("country: {0}\n".format(op_post.country))
        file.write("text: {0}\n".format(op_post.text))
        file.write("**END_OF_POST**\n")
        file.close()

    def save_response(self, reply, save_image=True):
        file = open(self.directory_name + self.output_file + '.txt', "a")
        file.write("time_human: {0}\n".format(reply.time_human))
        if reply.image_url is not None:
            file.write("image: {0}\nimage_url {1}\n".format(reply.image_name, reply.image_url))
            if save_image:
                self.save_image_to_file(reply)
        file.write("country: {0}\n".format(reply.country))
        try:
            file.write("text: {0}\n".format(reply.text))
        except UnicodeEncodeError:
            file.write("text: {0}\n".format(reply.text.encode("UTF-8")))
        file.write("**END_OF_POST**\n")
        file.close()

    def collect_saved_ids(self):
        self.saved_post_ids = [r.post_id for r in self.responses]

    def save_new_replies(self):
        self.get_soup()
        new_responses = []
        for reply in self.soup.find_all(class_="post reply"):
            if self.get_post_id(reply) in self.saved_post_ids:
                pass
            else:
                new_reply = self.strip_reply_data(reply)
                new_responses.append(new_reply)
                self.save_response(new_reply)
                self.saved_post_ids.append(new_reply.post_id)
        print("thread %s: %d new replies" % (self.threadId, len(new_responses)))
        [self.responses.append(response) for response in new_responses]


def download_until_it_dies(threadId, website):
    scrapper = ChanScrapper(threadId, website)
    scrapper.strip_responses()
    scrapper.write_responses_to_file()
    sleep_time = 30
    while not scrapper.check_if_page_is_closed():
        time.sleep(sleep_time)
        # print("Paused for %d sec:" % sleep_time, end=" ")
        scrapper.save_new_replies()
    print("Scraping {0} last time:".format(scrapper.url), end=" ")
    scrapper.save_new_replies()


def main():
    threads = []
    for index, page in enumerate(list_of_websites):
        thread = scraperThread(index + 1, page)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    # main()
    download_until_it_dies(1, website)