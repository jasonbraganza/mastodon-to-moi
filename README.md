## Python script to get the content of my public toots on my fediverse instance, via rss  and then cross post them to my microblog for long term archival
The script will gets RSS entries from a mastodon feed and create text files in the current directory, which I then give to Hugo to post to the microblog

 

## Install
1. In a virtualenv, install requirements with `pip`  
I use Python 3.11

```bash
python -m pip install -r requirements.txt
```

2. Run the script to pull toots and push to the microblog *(this is wip)*
```bash
python mastodon_to_moi.py <'mastodon rss feed url (without the angle brackets)'>
```

### Caveats
The script also does no verification of any sort. for e.g.,  to see, if the feed is malformed.  
Use at your own risk