__author__ = 'Ian'
import urllib
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
import os
from datetime import datetime

website = 'http://boards.4chan.org/pol/thread/90483380'
# with urllib.request.urlopen(website) as response:
#     html = response.read()

r = requests.get(website)

soup = BeautifulSoup(r.text, 'html.parser')

# directory_name = "scraped_lectures"
# cwd = os.path.dirname(os.path.abspath(__file__))
# new_directory_name = cwd + "\\" + directory_name + "\\"
# os.makedirs(new_directory_name, exist_ok=True)
#
post_replies = soup.find_all('div', class_='post reply')


def extract_post_data(reply):
    message = reply.find_all(class_="postMessage")
    if len(message) > 1:
        print("I found more than once postMessage class")
        return {"country": None, "time_human": None, "time_utc": None, "text": None}
    else:
        country = reply.find_all(class_="flag")[0]['title']
        time_human = reply.find_all(class_="dateTime postNum")[0].getText()
        time_utc = reply.find_all(class_="dateTime postNum")[0]['data-utc']
        text = reply.find_all(class_="postMessage")[0].getText()
        return {"country": country, "time_human": time_human, "time_utc": time_utc, "text": text}


directory_name = "pres_debate"
cwd = os.path.dirname(os.path.abspath(__file__))
new_directory_name = cwd + "\\" + directory_name + "\\"
os.makedirs(new_directory_name, exist_ok=True)

doc_title = '4chan_responds_v2.txt'

for index, reply in enumerate(post_replies):
    rd = extract_post_data(reply)
    file = open(new_directory_name + doc_title, "a")
    file.write("country: {0}\ntime_human: {1}\ntime_utc: {2}\n".format(rd["country"], rd['time_human'], rd['time_utc']))
    file.write("text: {0}\n".format(rd['text'].encode("UTF-8")))
    file.close()
    if index % 50 == 0:
        print("Wrote %d replies to file" % index)
print("I'm finished")