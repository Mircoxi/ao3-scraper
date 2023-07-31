import socket

import requests
from bs4 import BeautifulSoup
import time

from config import AO3_USERNAME, AO3_PASSWORD
import metrics as metrics

def get_stats(username, password):
    print(username)
    base_url = 'https://archiveofourown.org/'
    login_url = 'https://archiveofourown.org/users/login'
    '''
    The stats URL deliberately has specific parameters set to format data predictably. 

    The following assumptions are made:
    - Latest fics are more interesting stats-wise than older ones, which have likely tapered off; 
    - We want to get stats for ALL fics we've written;
    - We want to use flat view because it's easier to parse.
    '''
    stats_url = 'https://archiveofourown.org/users/' + username + '/stats?flat_view=true&sort_column=date&sort_direction=DESC&year=All+Years'
    with requests.Session() as session:
        request = session.get(login_url, allow_redirects=True)
        login_soup = BeautifulSoup(request.text, features='html.parser')
        # AO3 has a CSRF token for logins. We should find this first before we try to log in.
        auth_token = login_soup.find('input', {'name': 'authenticity_token'})['value']
        time.sleep(2)  # To be nice...
        # Logging in is just a POST request. We can discard the old request now we have the CSRF token.
        debug = session.post(login_url, data={
            'authenticity_token': auth_token,
            'user[login]': username,
            'user[password]': password,
        })
        time.sleep(2)  # Let it sit, in case AO3 is under load.
        # Unfortunately, AO3 doesn't return status codes, so...
        # TODO: Proper login handler checks.
        stats_request = session.get(stats_url)
        stat_soup = BeautifulSoup(stats_request.text, features='html.parser')
        stat_box = stat_soup.find('li', attrs={'class': 'fandom listbox group'})
        # class=None is a required check; there's a nested one with a "stats" class that throws this off otherwise.
        stat_items = stat_box.findChildren('dl', attrs={'class': None})
        for item in stat_items:
            # These are the actual works, start processing them.
            title = item.find('a').text
            fandom = item.find('span', attrs={'class': 'fandom'}).text.replace('(', '').replace(')', '')
            work_label = title + ' (' + fandom + ')'
            metrics.work_wordcount.labels(work_title=work_label).set(int(item.find('span', attrs={'class': 'words'}).text.replace('(', '').replace('words)', '').replace(',', '')))

            child_stats = item.find('dl')
            metrics.work_subs.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'subscriptions'}).text.replace(',', '')))
            metrics.work_hits.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'hits'}).text.replace(',', '')))
            metrics.work_kudos.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'kudos'}).text.replace(',', '')))
            metrics.work_comment_threads.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'comments'}).text.replace(',', '')))
            metrics.work_bookmarks.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'bookmarks'}).text.replace(',', '')))
        # Get the global stats too.
        global_statbox = stat_soup.find('dl', attrs={'class': 'statistics meta group'})
        metrics.user_threads.set(int(global_statbox.find('dd', attrs={'class': 'comment thread count'}).text.replace(',', '')))
        metrics.user_wordcount.set(int(global_statbox.find('dd', attrs={'class': 'words'}).text.replace(',', '')))
        metrics.user_hits.set(int(global_statbox.find('dd', attrs={'class': 'hits'}).text.replace(',', '')))
        metrics.user_subs.set(int(global_statbox.find('dd', attrs={'class': 'subscriptions'}).text.replace(',', '')))
        metrics.user_kudos.set(int(global_statbox.find('dd', attrs={'class': 'kudos'}).text.replace(',', '')))
        metrics.user_bookmarks.set(int(global_statbox.find('dd', attrs={'class': 'bookmarks'}).text.replace(',', '')))
        metrics.user_global_subs.set(int(global_statbox.find('dd', attrs={'class': 'user subscriptions'}).text.replace(',', '')))

if __name__ == "__main__":
    print("DEBUG: Starting.")
    while True:
        get_stats(AO3_USERNAME, AO3_PASSWORD)
        time.sleep(1800)