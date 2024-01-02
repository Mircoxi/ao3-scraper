import socket

import requests
from bs4 import BeautifulSoup
import time
import os
import ao3scraper.metrics as metrics

AO3_USERNAME = os.environ.get("AO3_USERNAME", "")
AO3_PASSWORD = os.environ.get("AO3_PASSWORD", "")
DEBUG_MODE = bool(os.environ.get("DEBUG_MODE", 0))

def get_stats(username, password):
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
        login_attempt = session.post(login_url, data={
            'authenticity_token': auth_token,
            'user[login]': username,
            'user[password]': password,
        })
        time.sleep(2)  # Let it sit, in case AO3 is under load.
        if login_attempt.status_code != 200:
            raise requests.exceptions.RequestException("AO3 is experiencing issues!")
        if 'Please try again' in login_attempt.text:
            raise RuntimeError('Error logging in - wrong username and password.')

        stats_request = session.get(stats_url)
        if stats_request.status_code != 200:
            raise requests.exceptions.RequestException("AO3 is experiencing issues!")
        stat_soup = BeautifulSoup(stats_request.text, features='html.parser')
        stat_box = stat_soup.find('li', attrs={'class': 'fandom listbox group'})
        # class=None is a required check; there's a nested one with a "stats" class that throws this off otherwise.
        stat_items = stat_box.findChildren('dl', attrs={'class': None})
        for item in stat_items:
            # These are the actual works, start processing them.
            title = item.find('a').text
            fandom = item.find('span', attrs={'class': 'fandom'}).text.replace('(', '').replace(')', '')
            work_label = title + ' (' + fandom + ')'
            metrics.ao3_work_wordcount.labels(work_title=work_label).set(int(item.find('span', attrs={'class': 'words'}).text.replace('(', '').replace('words)', '').replace(',', '')))

            child_stats = item.find('dl')
            try:
                metrics.ao3_work_subs.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'subscriptions'}).text.replace(',', '')))
            except AttributeError:
                # For when a work doesn't have any subscriptions yet.
                metrics.ao3_work_subs.labels(work_title=work_label).set(0)
            metrics.ao3_work_hits.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'hits'}).text.replace(',', '')))
            metrics.ao3_work_kudos.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'kudos'}).text.replace(',', '')))
            metrics.ao3_work_comment_threads.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'comments'}).text.replace(',', '')))
            metrics.ao3_work_bookmarks.labels(work_title=work_label).set(int(child_stats.find('dd', attrs={'class': 'bookmarks'}).text.replace(',', '')))
        # Get the global stats too.
        global_statbox = stat_soup.find('dl', attrs={'class': 'statistics meta group'})
        metrics.ao3_user_threads.set(int(global_statbox.find('dd', attrs={'class': 'comment thread count'}).text.replace(',', '')))
        metrics.ao3_user_wordcount.set(int(global_statbox.find('dd', attrs={'class': 'words'}).text.replace(',', '')))
        metrics.ao3_user_hits.set(int(global_statbox.find('dd', attrs={'class': 'hits'}).text.replace(',', '')))
        #metrics.user_subs.set(int(global_statbox.find('dd', attrs={'class': 'subscriptions'}).text.replace(',', '')))
        metrics.ao3_user_kudos.set(int(global_statbox.find('dd', attrs={'class': 'kudos'}).text.replace(',', '')))
        metrics.ao3_user_bookmarks.set(int(global_statbox.find('dd', attrs={'class': 'bookmarks'}).text.replace(',', '')))
        metrics.ao3_user_global_subs.set(int(global_statbox.find('dd', attrs={'class': 'user subscriptions'}).text.replace(',', '')))


if __name__ == "__main__":
    # Keep track of whether the last result was a failure or not, so we can let the user know.
    previous_error = False
    if DEBUG_MODE is True:
        print("DEBUG: Starting.")
    while True:
        try:
            get_stats(AO3_USERNAME, AO3_PASSWORD)
            if previous_error is True:
                print("AO3 back up! Got stats and resuming normal functions.")
                previous_error = False
            if DEBUG_MODE is True:
                print("Got stats! Sleeping 30 minutes...")
            time.sleep(1800)
        except RuntimeError:
            # Throw an error and quit.
            print("Your login credentials are probably wrong. Check them again!")
            exit(1)
        except requests.exceptions.RequestException:
            # AO3 likely experiencing issues. Sleep, but not as long so that stats update in a timely
            # fashion when it comes back.
            print("AO3 is experiencing issues! Backing off for a while... We'll check again in 10 minutes.")
            previous_error = True
            time.sleep(600)

