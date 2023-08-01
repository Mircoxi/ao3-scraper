# AO3 Stats Exporter

This is a simple Python app designed to act as a Prometheus endpoint for collecting stats about your fics on AO3. For most people, the on-site stats page is fine - but if you're interested in seeing how your stuff is doing over time, you may find this useful.

## How it works

The script works by logging in to AO3, and loading your statistics page. It then reads it, extracting information for both you as a user as well as your individual fics, and exposes a Prometheus metrics endpoint that can be scraped to provide historical data over time. 

AO3 only updates your stats every 30 minutes, so the script will only check on this interval. If AO3 is down for whatever reason, it'll back off, and check again in 10 minutes until it successfully scrapes. These intervals are chosen because there's both no point to scraping more often than that, and to make sure that it's not interpreted as a malicious bot.

The script only scrapes basic stats, to remain completely unopinionated on what's important, or how to present it. See below for the metrics exposed!

Your login details are only ever used for the login endpoint on AO3. Please feel free to verify this in the script.

## Running it

This can be run in one of two ways - with Docker, or standalone. In either case, a Prometheus metrics endpoint is exposed, so you'll need Prometheus, and probaly Grafana if you want to make the results look pretty. 

It's strongly recommended to run this under Docker, as that's the only way I test! 

### Docker

I'm assuming you understand the basics of how Docker works if you're using Prometheus to begin with. Three environment variables are used for the container:

- AO3_USERNAME - Your AO3 username. 
- AO3_PASSWORD - Your password.
- DEBUG_MODE - An integer, 0 or 1. Converted to a boolean internally. If not set, assumes False.

To get it going, pull the container from ghcr:
`docker pull ghcr.io/mircoxi/ao3-stats-exporter:latest`

Run it with the following:

`docker run --name ao3-exporter --env AO3_USERNAME=my_username --env AO3_PASSWORD=supersecurepassword --p 8000:8000 --dns 1.0.0.1 --dns 1.1.1.1 ghcr.io/mircoxi/ao3-stats-exporter:latest`

Add the container to your Prometheus config. The default scrape interval is fine, though data will only update every 30 minutes as per AO3's own update interval. The metrics endpoint isn't on a path, and runs on port 8000. In this command, DNS entries are provided to give the container the ability to resolve AO3's IP address - 1.0.0.1 and 1.1.1.1 are Cloudflare's resolver, but you may want to use 8.8.8.8 and 8.4.4.8 instead if you prefer Google. Advanced users will know if they're using a custom DNS, and can substitute that in as needed. 

### Standalone

This is tested with Python 3.11, but nothing particularly exotic is used - it'll likely run on a few earlier versions too. Create a venv and install the requirements as you would any other app. 

Edit `ao3scraper/main.py` to add your username and password. Replace the `os.environ.get` sections with a quoted string, and then run it with `python3 main.py`.

Add the script to your Prometheus config. The default scrape interval is fine, though data will only update every 30 minutes as per AO3's own update interval. The metrics endpoint isn't on a path, and runs on port 8000.

## Exposed Metrics

Anything that can be found on the stats page is exported, with the exception of the total subscription count. This is due to the layout of the stats page, and the classes of the HTML elements making it difficult to extract. A simple workaround is to simply sum the subscription count for individual fics. 

All metrics are prefixed with `ao3_` as a simple namespace mechanism, in case you use your Prometheus instance for multiple things.  All metrics are created as gauges to allow for people unsubscribing, etc. 

Feel free to create a dashboard in Grafana to display whichever ones are most useful to you! 

### Work Metrics

Work Metrics all have a label, `work_title`, which will help distinguish it in your dashboard. This includes the fandom name too - for example, if you publish a fic called "Joker and Skull's Excellent Adventure" for Persona 5, the `work_title` label will be `Joker and Skull's Excellent Adventure (Persona 5)`. This allows for filtering in PromQL queries, and allows dashboards to display information better.

| Metric        | Details       |
| ------------- | ------------- |
| ao3_work_hits  | The number of hits a work has. Unfortunately, AO3 doesn't expose this per chapter, so it's only available for the full work.  |
| ao3_work_subs  | The subscription count for the work.  |
| ao3_work_kudos | How many kudos the work has. Like hit count, this is for the work as a whole rather than per chapter. |
| ao3_work_comment_threads | The number of comment threads a work has. While this *could* be done per chapter, the stats page exposes this for the work as a whole, so we're rolling with it for consistency with other metrics. |
| ao3_work_bookmarks | The number of bookmarks on the work. Currently doesn't distinguish between normal bookmarks and recommendations, but may be adjusted in a future update. |
| ao3_work_wordcount | The wordcount for the work. This is mostly useful when used as context for other metrics - a bump here most likely indicates a new chapter, which would help you gauge how many new hits came from it.

### Global Metrics

These are the ones that apply to the user as a whole. As noted above, total work subscription count is excluded due to issues.

| Metric     | Details     |
| ---------- | ----------- | 
| ao3_user_kudos | Your total kudos, across all works. |
| ao3_user_threads | Comment thread total, across all works. |
| ao3_user_bookmarks | How many times your works have been bookmarked, across all works. | 
| ao3_user_wordcount | Your total wordcount across everything you've published. |
| ao3_user_hits | Your total hit count. |
| ao3_user_global_subs | How many people have subscribed to you, as a user. |


## Bugs, Features, and Support

As of publishing, I have this working fine - but that can change! If there's any issues, or things you think of missing, please feel free to open an issue on GitHub, or a Pull Request if you're feeling up for it. 

This script is free to use, but if you found it useful, feel free to [drop me a couple dollars](https://patreon.com/mircoxi) so I can buy a coffee. I'd really appreciate it! 
