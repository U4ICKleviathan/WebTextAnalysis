__author__ = 'Ian'
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
import bs4
import os
from datetime import datetime, timedelta
import shutil
import time
import inspect
import threading
import sys
from getsize import getsize
import logging
import logging.handlers

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name) - 30s - %(levelname)s - %(message)s')

module_stream_handler = logging.StreamHandler()
module_stream_handler.setLevel(logging.WARNING)
module_stream_handler.setFormatter(formatter)

module_logger.addHandler(module_stream_handler)

logFilePath = "C:\\Users\\Ian\\PycharmProjects\\WebTextAnalysis\\logs\\analyze_texts.log"
file_handler = logging.handlers.TimedRotatingFileHandler(filename=logFilePath, when='midnight', backupCount=30)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
module_logger.addHandler(file_handler)

now = time.strftime("%H:%M:%S", time.localtime(time.time()))


def print_status(thread_id, status_message):
    print(thread_id, now, status_message)

directory_for_data = 'scrapped_pages'

list_of_websites = [
    "http://boards.4chan.org/pol/thread/90962775/btfo",
    "http://boards.4chan.org/pol/thread/90985328/happening-the-end-is-nigh",
    "http://boards.4chan.org/pol/thread/90985993/there-are-people-on-pol-right-now-that-do-not-own",
]

website = 'http://boards.4chan.org/pol/thread/91466560/if-hillary-wins'
# website = "http://boards.4chan.org/pol/thread/91324290/travel-back-to-the-past"
# website = "http://boards.4chan.org/pol/thread/91113226/how-do-we-fix-low-testosterone-in-boys"

"""
https://github.com/4chan/4chan-API
"""
bad_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]


def build_name(potential_name):
    built_name = ''
    for i in potential_name:
        if i == " ":
            i = "_"
        if i in bad_characters:
            pass
        else:
            built_name = built_name + i
            if len(built_name) >= 25:
                return built_name
    return built_name

def build_name_from_url(url):
    named_portion_of_url = ""
    len_url = len(url) - 1
    for i in range(len_url, 0, -1):
        if url[i] == "/":
            break
        else:
            named_portion_of_url = url[i] + named_portion_of_url

    built_name = ''
    for i in named_portion_of_url:
        built_name = built_name + i
        if len(built_name) > 25:
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
        get_new_replies_until_page_dies(self.threadId, self.website)
        print("Exiting " + self.website)


class ChanScrapper(object):
    def __init__(self, threadId, website):
        self.cs_logger = logging.getLogger(__name__ + '.ChanScrapper')
        self.cs_logger.info("created an instance of chan scrapper")
        module_logger.info("creating an instance of ChanScrapper for website {0}".format(website))
        self.threadId = threadId
        self.url = website
        self.soup = None
        self.all_posts = []
        self.saved_post_ids = []
        self.thread_directory = None
        self.picture_directory = None
        self.output_file = None
        pass

    def scrape_existing_posts(self):
        self.cs_logger.info("getting_url")
        self.get_soup()
        self.cs_logger.info("scrapping replies from thread")
        self.strip_post_data_from_thread()
        self.cs_logger.info("creating outfile")
        self.create_outfile()
        self.cs_logger.info("configuring directories")
        self.configure_directories()
        self.cs_logger.info("writing files to directories")
        self.write_responses_to_file()
        self.cs_logger.info("done writing files")
        self.collect_saved_ids()

    def get_soup(self):
        r = requests.get(self.url)
        if r.status_code == 404:
            self.cs_logger.warning("EXIT PROCESS: website not found {0} ".format(str(self.url)))
            sys.exit()
        elif r.status_code == 200:
            self.soup = BeautifulSoup(r.text, 'html.parser')

    def strip_post_data_from_thread(self):
        self.add_op_post()
        self.add_thread_responses()

    def add_op_post(self):
        post = self.soup.find_all(class_="post op")[0]
        op_post = Response()
        op_post.op_subject = get_post_subject(post)
        op_post.time_human = get_post_human_time(post)
        op_post.time_utc = get_post_time_utc(post)
        op_post.user_id = get_post_user_id(post)
        op_post.post_id = get_post_id(post)
        op_post.country = get_post_country(post)
        op_post.text = get_post_text(post)
        op_post.image_url = get_post_image_url(post)
        op_post.image_name = get_post_image_name(post)
        self.all_posts.append(op_post)

    def add_thread_responses(self):
        all_replies = self.soup.find_all(class_="post reply")
        for reply in all_replies:
            next_response = strip_post_data(reply)
            self.all_posts.append(next_response)

    def check_if_page_is_closed(self):
        if len(self.soup.find_all(class_='closed')) > 0:
            return True
        else:
            False

    def configure_directories(self):
        self.set_thread_directory(self.output_file)
        self.set_picture_directory()

    def set_thread_directory(self, thread_title):
        cwd = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
        new_directory_name = cwd + "\\" + directory_for_data + "\\" + thread_title + "\\"
        os.makedirs(new_directory_name, exist_ok=True)
        self.thread_directory = new_directory_name

    def set_picture_directory(self):
        sub_directory_name = self.thread_directory + "\\" + "pics" + "\\"
        os.makedirs(sub_directory_name, exist_ok=True)
        self.picture_directory = sub_directory_name
        pass

    def create_outfile(self):
        doc_title = build_name_from_url(self.url)
        if doc_title.isdigit():
            doc_title = ""
            if len(self.all_posts[0].op_subject) <= 1:
                doc_title = build_name(self.all_posts[0].text)
            else:
                doc_title = build_name(self.all_posts[0].op_subject)
        self.output_file = doc_title

    def write_responses_to_file(self, save_images=True):
        for index, reply in enumerate(self.all_posts):
            if index == 0:
                self.save_op_post(reply, save_images)
            else:
                self.save_response(reply, save_images)
        # module_logger.info("Thread %s: Added %d original posts" % (self.output_file, index))

    def save_op_post(self, op_post, save_image=True):
        file = open(self.thread_directory + self.output_file + '.txt', "w")
        write_post_id(file, op_post)
        write_time_info(file, op_post)
        write_image_data(file, op_post, self.picture_directory, save_image)
        write_subject(file, op_post)
        write_country_info(file, op_post)
        write_text(file, op_post)
        file.write("**END_OF_POST**\n")
        file.close()

    def save_response(self, post, save_image=True):
        file = open(self.thread_directory + self.output_file + '.txt', "a")
        write_time_info(file, post)
        write_post_id(file, post)
        write_image_data(file, post, self.picture_directory, save_image)
        write_country_info(file, post)
        write_text(file, post)
        file.write("**END_OF_POST**\n")
        file.close()

    def collect_saved_ids(self):
        self.saved_post_ids = [r.post_id for r in self.all_posts]

    def save_new_replies(self):
        self.get_soup()
        new_responses = []
        for reply in self.soup.find_all(class_="post reply"):
            if get_post_id(reply) in self.saved_post_ids:
                pass
            else:
                new_reply = strip_post_data(reply)
                new_responses.append(new_reply)
                self.save_response(new_reply)
                self.saved_post_ids.append(new_reply.post_id)
        print("thread %s: %d new replies" % (self.threadId, len(new_responses)))
        [self.all_posts.append(response) for response in new_responses]


def strip_post_data(reply):
    response = Response()
    response.time_human = get_post_human_time(reply)
    response.time_utc = get_post_time_utc(reply)
    response.user_id = get_post_user_id(reply)
    response.post_id = get_post_id(reply)
    response.country = get_post_country(reply)
    response.text = get_post_text(reply)
    response.image_url = get_post_image_url(reply)
    response.image_name = get_post_image_name(reply)
    return response


def get_post_subject(post):
    return post.find_all(class_='subject')[1].text


def get_post_human_time(post):
    return post.find_all(class_='dateTime')[1].text


def get_post_time_utc(post):
    return post.find_all(class_='dateTime')[0]['data-utc']


def get_post_user_id(post):
    return post.find_all(class_="hand")[0].text


def get_post_id(post):
    return post.find_all('input')[0]['name']


def get_post_country(post):
    return post.find_all(class_="flag")[0]['title']


def get_post_text(post):
    post_text = ''
    post_message = post.find_all(class_='postMessage')[0]
    for line in post_message.contents:
        if isinstance(line, bs4.element.NavigableString):
            post_text = post_text + " " + line
        elif isinstance(line, bs4.element.Tag):
            post_text = post_text + " " + line.text
    return post_text


def get_post_image_url(post):
    if len(post.find_all(class_='file')) != 0:
        try:
            file_data = post.find_all(class_='fileText')[0]
            return 'http:' + file_data.find_all('a', href=True)[0]['href']
        except IndexError:
            return None
    else:
        return None


def get_post_image_name(post):
    if len(post.find_all(class_='file')) != 0:
        try:
            file_data = post.find_all(class_='fileText')[0]
            return file_data.find_all('a', href=True)[0].text
        except IndexError:
            file = post.find_all(class_='file')[0]
            return file.img['alt']
    else:
        return None


def write_subject(file, op_post):
    file.write("subject: {0}\n".format(op_post.op_subject))


def write_country_info(file, post):
    file.write("country: {0}\n".format(post.country))


def write_post_id(file, post):
    file.write("post_id: {0}\n".format(post.post_id))


def write_time_info(file, post):
    file.write("time_human: {0}\ntime_utc: {1}\n".format(post.time_human, post.time_utc))


def write_text(file, post):
    try:
        file.write("text: {0}\n".format(post.text))
    except UnicodeEncodeError:
        file.write("text: {0}\n".format(post.text.encode("UTF-8")))


def write_image_data(file, post, pic_directory, save_image=True):
    if post.image_url is not None:
        try:
            file.write("image_name: {0}\nimage_url {1}\n".format(post.image_name, post.image_url))
        except UnicodeEncodeError as e:
            pass
            module_logger.warning("Found Exception while writing image data")
            module_logger.debug("could not write image data to file. message {0}".format(e))
        if save_image:
            try:
                save_image_to_file(post, pic_directory)
            except UnicodeEncodeError:
                print("could not write {0} to file.  url: {1}".format(post.image_name, post.image_url))


def save_image_to_file(post, pic_directory):
    if post.image_url[:2] == '//':
        url = "http:" + post.image_url
    else:
        url = post.image_url
    imr = requests.get(url, stream=True)
    if imr.status_code == 200:
        name = ''
        for letter in post.image_name:
            if letter in bad_characters:
                pass
            else:
                name += letter
        with open(pic_directory + name, "wb") as f:
            imr.raw.decode_content = True
            shutil.copyfileobj(imr.raw, f)


def get_new_replies_until_page_dies(threadId, website):
    scrapper = ChanScrapper(threadId, website)
    scrapper.scrape_existing_posts()
    sleep_time = 30
    while not scrapper.check_if_page_is_closed():
        time.sleep(sleep_time)
        scrapper.save_new_replies()
    # print("Scraping {0} last time:".format(scrapper.url), end=" ")
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
    get_new_replies_until_page_dies(1, website)