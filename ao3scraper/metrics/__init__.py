import socket

from prometheus_client import CollectorRegistry, Gauge, Summary, Histogram, push_to_gateway, instance_ip_grouping_key
from prometheus_client import start_http_server

start_http_server(8000)

# Declare metric categories. Gauges are used bcause some values can go up as well as down;
# for example a user unsubscribes, unbookmarks, etc.

registry = CollectorRegistry()
ao3_work_hits = Gauge('ao3_work_hits', 'Hits', ['work_title'])
ao3_work_subs = Gauge('ao3_work_subscriptions', 'Subscriptions', ['work_title'])
ao3_work_kudos = Gauge('ao3_work_kudos', 'Kudos', ['work_title'])
ao3_work_comment_threads = Gauge('ao3_work_comments', 'Comment Threads', ['work_title'])
ao3_work_bookmarks = Gauge('ao3_work_bookmarks', 'Bookmarks', ['work_title'])
ao3_work_wordcount = Gauge('ao3_work_wordcount', 'Word Count', ['work_title'])

# =========================
# == GLOBAL USER METRICS ==
# =========================

# ao3_user_subs = Gauge('user_subscriptions', 'Global Subscriptions')  # Removed because it gets the wrong stat.
ao3_user_kudos = Gauge('ao3_user_kudos', 'Global Kudos')
ao3_user_threads = Gauge('ao3_user_comments', 'Global Comment Threads')
ao3_user_bookmarks = Gauge('ao3_user_bookmarks', 'Global Bookmarks')
ao3_user_wordcount = Gauge('ao3_user_wordcount', 'Global Wordcount')
ao3_user_hits = Gauge('ao3_user_hits', 'Global Hits')
ao3_user_global_subs = Gauge('ao3_user_global_subs', 'User Subscriptions')
