import urllib
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
import re
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import pydotplus
from networkx.drawing.nx_pydot import graphviz_layout

from datetime import datetime
from datetime import timedelta
import suffix_array_long as sal
import time
import networkx as nx

zero_words = ['a', 'a’s', 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after',
              'afterwards', 'again', 'against', 'ain’t', 'all', 'allow', 'allows', 'almost', 'alone', 'along',
              'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any',
              'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear',
              'appreciate', 'appropriate', 'are', 'aren’t', 'around', 'as', 'aside', 'ask', 'asking', 'associated',
              'at', 'available', 'away', 'awfully', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been',
              'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better',
              'between', 'beyond', 'both', 'brief', 'but', 'by', 'c’mon', 'c’s', 'came', 'can', 'can’t', 'cannot',
              'cant', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 'comes',
              'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains',
              'corresponding', 'could', 'couldn’t', 'course', 'currently', 'definitely', 'described', 'despite', 'did',
              'didn’t', 'different', 'do', 'does', 'doesn’t', 'doing', 'don’t', 'done', 'down', 'downwards', 'during',
              'each', 'edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et',
              'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly',
              'example', 'except', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for',
              'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'get', 'gets', 'getting',
              'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', 'hadn’t', 'happens',
              'hardly', 'has', 'hasn’t', 'have', 'haven’t', 'having', 'he', 'he’s', 'hello', 'help', 'hence', 'her',
              'here', 'here’s', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself',
              'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', '', 'i', 'i’d', 'i’ll', 'i’m', 'i’ve', 'ie',
              'if', 'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates',
              'inner', 'insofar', 'instead', 'into', 'inward', 'is', 'isn’t', 'it', 'it’d', 'it’ll', 'it’s', 'its',
              'itself', 'just', 'keep', 'keeps', 'kept', 'know', 'knows', 'known', 'last', 'lately', 'later', 'latter',
              'latterly', 'least', 'less', 'lest', 'let', 'let’s', 'like', 'liked', 'likely', 'little', 'look',
              'looking', 'looks', 'ltd', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile', 'merely', 'might',
              'mine', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself', 'name', 'namely', 'nd',
              'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine',
              'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere',
              'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto',
              'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over',
              'overall', 'own', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible',
              'presumably', 'probably', 'provides', 'que', 'quite', 'qv', 'rather', 'rd', 're', 'really', 'reasonably',
              'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 'said', 'same', 'saw', 'say',
              'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen',
              'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'she',
              'should', 'shouldn’t', 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something',
              'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying',
              'still', 's', 'sub', 'such', 'sup', 'sure', 't’s', 'take', 'taken', 'tell', 'tends', 'th', 'than',
              'thank', 'thanks', 'thanx', 'that', 'that’s', 'thats', 'the', 'their', 'theirs', 'them', 'themselves',
              'then', 'thence', 'there', 'there’s', 'thereafter', 'thereby', 'therefore', 'therein', 'theres',
              'thereupon', 'these', 'they', 'they’d', 'they’ll', 'they’re', 'they’ve', 'think', 'third', 'this',
              'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to',
              'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice',
              'two', 'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use',
              'used', 'useful', 'uses', 'using', 'usually', 'value', 'various', 'very', 'via', 'viz', 'vs', 'want',
              'wants', 'was', 'wasn’t', 'way', 'we', 'we’d', 'we’ll', 'we’re', 'we’ve', 'welcome', 'well', 'went',
              'were', 'weren’t', 'what', 'what’s', 'whatever', 'when', 'whence', 'whenever', 'where', 'where’s',
              'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while',
              'whither', 'who', 'who’s', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with',
              'within', 'without', 'won’t', 'wonder', 'would', 'would', 'wouldn’t', 'yes', 'yet', 'you', 'you’d',
              'you’ll', 'you’re', 'you’ve', 'your', 'yours', 'yourself', 'yourselves', 'zero']


class ResponseAnalyzer(object):
    def __init__(self, responses):
        self.pattern_count_in_time_bucket = []
        self.comments_in_time_bucket = []
        self.responses = responses

    def show_state(self):
        num_responses = len(self.responses)
        print("Responses: %d" % num_responses)

    def country_count(self):
        self.country_counts = {}
        for response in self.responses:
            if response.country in self.country_counts:
                self.country_counts[response.country] += 1
            else:
                self.country_counts[response.country] = 1

    def count_comments_in_time_bucket(self, bucket_size='minute'):
        last_response_index = len(self.responses) - 1
        comment_count = 0
        previous_time_bucket = self.responses[0].time_bucket_string(bucket_size)
        for index, response in enumerate(self.responses):
            current_time_bucket = response.time_bucket_string(bucket_size)
            if index == last_response_index:
                if current_time_bucket == previous_time_bucket:
                    comment_count += 1
                    result_tuple = (current_time_bucket, comment_count)
                    self.comments_in_time_bucket.append(result_tuple)
                else:
                    result_tuple = (current_time_bucket, 1)
                    self.comments_in_time_bucket.append(result_tuple)
            elif current_time_bucket == previous_time_bucket:
                comment_count += 1
            else:
                result_tuple = (previous_time_bucket, comment_count)
                self.comments_in_time_bucket.append(result_tuple)
                previous_time_bucket = current_time_bucket
                comment_count = 1

    def country_bar_plot(self):
        x = []
        y = []
        for key, value in sorted(self.country_counts.items()):
            x.append(key)
            y.append(value)
        data = [go.Bar(
            x=x,
            y=y
        )]
        py.plot(data, file_name="Countries")

    def plot_comment_count_timeseries(self, bucket_size="minute"):
        self.count_comments_in_time_bucket(bucket_size)
        x_values = []
        y_values = []
        for time_bucket, comment_count in self.comments_in_time_bucket.items():
            x_values.append(time_bucket)
            y_values.append(comment_count)
        data = [go.Scatter(x=x, y=y_values)]
        py.plot(data)

    def combine_text_in_range(self, bucket_size="minute"):
        self.text_in_bucket = []
        previous_time_bucket = self.responses[0].time_bucket_string(bucket_size)
        text_in_time_bucket = ''
        last_response_index = len(self.responses) - 1
        for index, response in enumerate(self.responses):
            current_time_bucket = response.time_bucket_string(bucket_size)
            current_text = response.text.lower()
            if previous_time_bucket == current_time_bucket and index < last_response_index:
                text_in_time_bucket += current_text
            elif index == last_response_index and previous_time_bucket == current_time_bucket:
                text_in_time_bucket += current_text
                result_tuple = (previous_time_bucket, text_in_time_bucket)
                self.text_in_bucket.append(result_tuple)
            elif index == last_response_index and previous_time_bucket != current_time_bucket:
                result_tuple = (previous_time_bucket, text_in_time_bucket)
                self.text_in_bucket.append(result_tuple)
                previous_time_bucket = current_time_bucket
                text_in_time_bucket = current_text
                result_tuple = (previous_time_bucket, text_in_time_bucket)
                self.text_in_bucket.append(result_tuple)
            else:
                result_tuple = (previous_time_bucket, text_in_time_bucket)
                self.text_in_bucket.append(result_tuple)
                previous_time_bucket = current_time_bucket
                text_in_time_bucket = current_text

    def count_patterns_in_time_bucket(self, patterns, bucket_size):
        print("Counting patterns:", end=" ")
        start_time = time.time()
        self.combine_text_in_range(bucket_size)
        for time_bucket, text in self.text_in_bucket:
            result_dict = {}
            for pattern in patterns:
                pattern_count = sal.find_pattern_count(pattern, text)
                result_dict[pattern] = len(pattern_count)
            result_tuple = (time_bucket, result_dict)
            self.pattern_count_in_time_bucket.append(result_tuple)
        print("%d seconds" % round(time.time() - start_time, 3))

    def plot_pattern_count(self, patterns, bucket_size):
        self.count_patterns_in_time_bucket(patterns, bucket_size)
        self.count_comments_in_time_bucket(bucket_size)
        x_values = []
        patterns.sort()
        y_values = [[] for _ in range(len(patterns))]
        traces = []
        for timestamp, result_dic in self.pattern_count_in_time_bucket:
            x_values.append(timestamp)
            for pattern, count in result_dic.items():
                y_values[patterns.index(pattern)].append(count)
        comment_counts = [comment_counts for t, comment_counts in self.comments_in_time_bucket]
        for i in range(len(patterns)):
            pattern_trace = go.Scatter(
                x=x_values,
                y=y_values[i],
                mode='lines+markers',
                name=patterns[i]
            )
            traces.append(pattern_trace)
        count_trace = go.Scatter(
            x=x_values,
            y=comment_counts,
            mode='lines+markers',
            name='total comments',
            yaxis='y2'
        )
        traces.append(count_trace)
        layout = go.Layout(
            title="Patten Counts and Total Comment Counts",
            yaxis=dict(
                title='Pattern Count'
            ),
            yaxis2=dict(
                title='Total Comments',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=traces, layout=layout)
        py.plot(fig)


class Response:
    def __index__(self):
        self.country = ""
        self.time_human = ""
        self.time_utc = 0
        self.text = ""
        self.time_object = None

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

class ThreadAnalyzer(object):
    def __init__(self, file_name):
        self.all_posts = []
        self.stemmed_words_by_thread = None
        self.raw_text = ''
        self.post_text_clean = []
        self.file_name = file_name
        self.thread_graph = None
        self.thread_graph_gap2 = None
        self.thread_graph_gap5 = None



    def start_thread_graph(self):
        self.get_responses_from_file()
        self.process_text_by_thread()
        self.create_graph_by_thread()

    def get_responses_from_file(self):
        retriever = fileImporter(self.file_name)
        self.all_posts = retriever.get_responses_from_file()

    def get_raw_text(self):
        raw_text = ""
        for post in self.all_posts:
            raw_text += post.text
        self.raw_text = raw_text

    def process_text_by_thread(self):
        self.get_raw_text()
        zeroed_words = remove_zero_words(self.raw_text)
        self.stemmed_words_by_thread = stem_words(zeroed_words)

    def process_text_by_post(self):
        for post in self.all_posts:
            zeroed_words = remove_zero_words(post.text)
            stemmed_words = stem_words(zeroed_words)
            self.post_text_clean.append(stemmed_words)

    def create_graph_by_thread(self):
        graph = nx.Graph()
        graph.count = {}
        self.thread_graph = populate_2_pass_graph(graph, self.stemmed_words_by_thread)

    def plot_atlas_force_graph(self):
        force_atlas_plot(self.thread_graph)


def populate_2_pass_graph(graph, word_list):
    gap_size = 2
    for index, word in enumerate(word_list):
        if word not in graph:
            graph.add_node(word)
        graph = scan_gap(gap_size, graph, index, word, word_list)
    gap_size = 5
    for index, word in enumerate(word_list):
        graph = scan_gap(gap_size, graph, index, word, word_list)
    return graph


def scan_gap(gap_size, graph, index, word, word_list):
    try:
        for i in range(1, gap_size + 1):
            if graph.has_edge(word, word_list[index + i]):
                graph[word][word_list[index + i]]['weight'] += 1
                pass
            else:
                graph.add_edge(word, word_list[index + i], weight=1)
        return graph
    except IndexError:
        return graph
"""
Atlas of all graphs of 6 nodes or less.

"""
# Author: Aric Hagberg (hagberg@lanl.gov)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx.generators.atlas import *
from networkx.algorithms.isomorphism.isomorph import graph_could_be_isomorphic as isomorphic
import random


def atlas6():
    """ Return the atlas of all connected graphs of 6 nodes or less.
        Attempt to check for isomorphisms and remove.
    """

    Atlas = graph_atlas_g()[0:208] # 208
    # remove isolated nodes, only connected graphs are left
    U = nx.Graph() # graph for union of all graphs in atlas
    for G in Atlas:
        zerodegree = [n for n in G if G.degree(n)==0]
        for n in zerodegree:
            G.remove_node(n)
        U = nx.disjoint_union(U, G)

    # list of graphs of all connected components
    C = nx.connected_component_subgraphs(U)

    UU = nx.Graph()
    # do quick isomorphic-like check, not a true isomorphism checker
    nlist = [] # list of nonisomorphic graphs
    for G in C:
        # check against all nonisomorphic graphs so far
        if not iso(G, nlist):
            nlist.append(G)
            UU = nx.disjoint_union(UU, G) # union the nonisomorphic graphs
    return UU

def iso(G1, glist):
    """Quick and dirty nonisomorphism checker used to check isomorphisms."""
    for G2 in glist:
        if isomorphic(G1, G2):
            return True
    return False


def force_atlas_plot(G):
    # G = atlas6()

    print("graph has %d nodes with %d edges"\
          %(nx.number_of_nodes(G), nx.number_of_edges(G)))
    print(nx.number_connected_components(G), "connected components")



    # plt.figure(1, figsize=(8, 8))
    # layout graphs with positions using graphviz neato
    pos = graphviz_layout(G, prog="neato")
    # color nodes the same in each connected subgraph
    C = nx.connected_component_subgraphs(G)
    for g in C:
        c = [random.random()] * nx.number_of_nodes(g) # random color...
        nx.draw(g,
             pos,
             node_size=40,
             node_color=c,
             vmin=0.0,
             vmax=1.0,
             with_labels=False
             )
    plt.show()


def remove_zero_words(text):
    split_words = re.findall(r"[\w']+", text)
    clean_words = []
    for word in split_words:
        if word in zero_words:
            pass
        else:
            clean_words.append(word)
    return clean_words


def stem_words(word_list):
    stemmer = SnowballStemmer("english")
    stemmed_words = [stemmer.stem(word) for word in word_list]
    return stemmed_words


class fileImporter(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def get_responses_from_file(self):
        directory = "C:\\Users\\Ian\\PycharmProjects\\WebTextAnalysis\\scrapped_pages\\"
        formatted_filename = directory + self.file_name
        file = open(formatted_filename, 'r')
        response = Response()
        response_list = []
        for line in file:
            if line[0] == '*':
                response_list.append(response)
                response = Response()
            else:
                response.parse_line(line)
        return response_list



x = ThreadAnalyzer("1452072389230.jp.txt")
x.start_thread_graph()
x.plot_atlas_force_graph()
pass



#
# directory = 'C:\\Users\\Ian\\PycharmProjects\\WebTextAnalysis\\pres_debate'
# file_name = '4chan_responds_v2.txt'
# formatted_filename = directory + '\\' + file_name
#
# file = open(formatted_filename, "r")
#
# response_list = []
#
#
# def get_responses_from_file(file_name):
#     directory = "C:\\Users\\Ian\\PycharmProjects\\WebTextAnalysis\\scrapped_pages\\"
#     formatted_filename = directory + file_name
#     file = open(formatted_filename, 'r')
#     response = Response()
#     response_list = []
#     for line in file:
#         if line[0] == '*':
#             response_list.append(response)
#             response = Response()
#         else:
#             response.parse_line(line)
#     return response_list
#
#
#
# for index, line in enumerate(file):
#     if index % 4 == 0:
#         new_response = Response()
#         response_list.append(new_response)
#     new_response.parse_line(line)
#     pass
#
# x = ResponseAnalyzer(response_list)
# # x.country_count()
# # x.country_bar_plot()
# # x.comment_time_series('minute')
#
# patterns = ['kek', "lol"]
# x.plot_pattern_count(patterns, 'quarter_second')
# pass
