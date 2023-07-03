import socket

from prometheus_client import CollectorRegistry, Gauge, Summary, Histogram, push_to_gateway, instance_ip_grouping_key
from ao3scraper.config import PROMETHEUS_PUSH_GATEWAY

# Declare metric categories. Gauges are used bcause the values can go up as well as down.
registry = CollectorRegistry()
work_hits = Gauge('work_hits', 'Hits', ['work_title'], registry=registry)
work_subs = Gauge('work_subscriptions', 'Subscriptions', ['work_title'], registry=registry)
work_kudos = Gauge('work_kudos', 'Kudos', ['work_title'], registry=registry)
work_comment_threads = Gauge('work_comments', 'Comment Threads', ['work_title'], registry=registry)
work_bookmarks = Gauge('work_bookmarks', 'Bookmarks', ['work_title'], registry=registry)
work_wordcount = Gauge('work_wordcount', 'Word Count', ['work_title'], registry=registry)
# Global user metrics

user_subs = Gauge('user_subscriptions', 'Global Subscriptions', registry=registry)
user_kudos = Gauge('user_kudos', 'Global Kudos', registry=registry)
user_threads = Gauge('user_comments', 'Global Comment Threads', registry=registry)
user_bookmarks = Gauge('user_bookmarks', 'Global Bookmarks', registry=registry)
user_wordcount = Gauge('user_wordcount', 'Global Wordcount', registry=registry)
user_hits = Gauge('user_hits', 'Global Hits', registry=registry)
user_global_subs = Gauge('user_global_subs', 'User Subscriptions', registry=registry)

def push_metrics():
    if PROMETHEUS_PUSH_GATEWAY is not None:
        push_to_gateway(gateway=PROMETHEUS_PUSH_GATEWAY,
                        job='ao3scraper',
                        grouping_key={'instance': socket.gethostname()},
                        registry=registry
                        #handler=my_auth_handler
                        )
