# Aims
# 1. Should be a python script that syncs my Mastodon feed to my microblog
# 2. Learn to give them types and learn mypy
# 3. It should be a standalone python utility, with no need for a system python

import sys

import feedparser
import json
from bs4 import BeautifulSoup


def main(fedi_account_rss_url):
    # Parse URL
    fedifeed = feedparser.parse(fedi_account_rss_url)
    print(fedifeed)


if __name__ == "__main__":
    url = sys.argv[1]
    main(url)
