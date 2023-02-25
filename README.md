## Python script to get the content of my public toots on my fediverse instance, via rss  and then cross post them to my microblog for long term archival

## Install
1. In a virtualenv, install requirements with `pip`  
I use Python 3.11

```bash
python -m pip install -r requirements.txt
```

2. Run the script to pull toots and push to the microblog *(this is wip)*
```bash
python mastodon_to_moi.py
```