import socket

from prometheus_client import CollectorRegistry, Gauge, Summary, Histogram, push_to_gateway, instance_ip_grouping_key
from prometheus_client import start_http_server

start_http_server(8000)
# Declare metric categories. Gauges are used bcause the values can go up as well as down.
registry = CollectorRegistry()
ao3_work_hits = Gauge('work_hits', 'Hits', ['work_title'])
ao3_work_subs = Gauge('work_subscriptions', 'Subscriptions', ['work_title'])
ao3_work_kudos = Gauge('work_kudos', 'Kudos', ['work_title'])
ao3_work_comment_threads = Gauge('work_comments', 'Comment Threads', ['work_title'])
ao3_work_bookmarks = Gauge('work_bookmarks', 'Bookmarks', ['work_title'])
ao3_work_wordcount = Gauge('work_wordcount', 'Word Count', ['work_title'])
# Global user metrics

# ao3_user_subs = Gauge('user_subscriptions', 'Global Subscriptions')  # Removed because it gets the wrong stat.
ao3_user_kudos = Gauge('user_kudos', 'Global Kudos')
ao3_user_threads = Gauge('user_comments', 'Global Comment Threads')
ao3_user_bookmarks = Gauge('user_bookmarks', 'Global Bookmarks')
ao3_user_wordcount = Gauge('user_wordcount', 'Global Wordcount')
ao3_user_hits = Gauge('user_hits', 'Global Hits')
ao3_user_global_subs = Gauge('user_global_subs', 'User Subscriptions')
