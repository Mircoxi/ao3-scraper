import socket

from prometheus_client import CollectorRegistry, Gauge, Summary, Histogram, push_to_gateway, instance_ip_grouping_key
from prometheus_client import start_http_server

start_http_server(8000)
# Declare metric categories. Gauges are used bcause the values can go up as well as down.
registry = CollectorRegistry()
work_hits = Gauge('work_hits', 'Hits', ['work_title'])
work_subs = Gauge('work_subscriptions', 'Subscriptions', ['work_title'])
work_kudos = Gauge('work_kudos', 'Kudos', ['work_title'])
work_comment_threads = Gauge('work_comments', 'Comment Threads', ['work_title'])
work_bookmarks = Gauge('work_bookmarks', 'Bookmarks', ['work_title'])
work_wordcount = Gauge('work_wordcount', 'Word Count', ['work_title'])
# Global user metrics

user_subs = Gauge('user_subscriptions', 'Global Subscriptions')
user_kudos = Gauge('user_kudos', 'Global Kudos')
user_threads = Gauge('user_comments', 'Global Comment Threads')
user_bookmarks = Gauge('user_bookmarks', 'Global Bookmarks')
user_wordcount = Gauge('user_wordcount', 'Global Wordcount')
user_hits = Gauge('user_hits', 'Global Hits')
user_global_subs = Gauge('user_global_subs', 'User Subscriptions')
