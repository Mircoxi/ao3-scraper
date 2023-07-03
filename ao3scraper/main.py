import requests
from bs4 import BeautifulSoup
import time
from ao3scraper.config import USERNAME, PASSWORD


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
        request = session.get(base_url, allow_redirects=True)
        login_soup = BeautifulSoup(request.text, features='html.parser')
        # AO3 has a CSRF token for logins. We should find this first before we try to log in.
        auth_token = login_soup.find('input', {'name': 'authenticity_token'})['value']
        time.sleep(2)  # To be nice...
        # Logging in is just a POST request. We can discard the old request now we have the CSRF token.
        request = session.post(login_url, data={
            'authenticity_token': auth_token,
            'user[login]': username,
            'user[password]': password,
        })
        time.sleep(2)  # Let it sit, in case AO3 is under load.
        # Unfortunately, AO3 doesn't return status codes, so...
        # TODO: Proper login handler checks.
        stats_request = session.get(stats_url)
        stat_soup = BeautifulSoup(stats_request.text, features='html.parser')
        stat_box = stat_soup.find('li', attrs= {'class': 'fandom listbox group'})
        # class=None is a required check; there's a nested one with a "stats" class that throws this off otherwise.
        stat_items = stat_box.findChildren('dl', attrs={'class': None})
        for item in stat_items:
            # These are the actual works, start processing them.
            title = item.find('a').text
            fandom = item.find('span', attrs={'class': 'fandom'}).text.replace('(', '').replace(')', '')
            child_stats = item.find('dl')
            subscriptions = int(child_stats.find('dd', attrs={'class': 'subscriptions'}).text)
            hits = int(child_stats.find('dd', attrs={'class': 'hits'}).text.replace(',', ''))
            kudos = int(child_stats.find('dd', attrs={'class': 'kudos'}).text)
            comment_threads = int(child_stats.find('dd', attrs={'class': 'comments'}).text)
            bookmarks = int(child_stats.find('dd', attrs={'class': 'bookmarks'}).text)
            print(title + ' (' + fandom + ') - ' + str(subscriptions) + ' subs, ' + str(hits) + ' hits')
        # Get the global stats too.
        global_statbox = stat_soup.find('dl', attrs={'class': 'statistics meta group'})
        print(global_statbox.find('dd', attrs={'class': 'user subscriptions'}).text + ' user subs')

get_stats(USERNAME, PASSWORD)