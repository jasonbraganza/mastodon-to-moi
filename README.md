## Python script to get the content of my public toots on my mastodon instance, via rss  and then cross post them to my microblog for long term archival
The script will gets RSS entries from a mastodon account feed and create text files in the current directory, which you can then give to Hugo to process

## Prerequisites, if you want to use this script
1. You have a mastodon account and its url
2. This script is tailored to a Hugo microblog running J N Josh’s [internet-weblog](https://github.com/jnjosh/internet-weblog) theme
3. This works if, you work on the blog, locally. You need to `rsync` or `git-push` once done. If your whole workflow is cloud based, this probably won’t do it for you 


 ### Caveats
The script also does no verification of any sort. for e.g.,  to see, if the feed is malformed.  
Use at your own risk.  
Media other than photos, don’t work for now.  

## Install
1. In a virtualenv, install requirements with `pip`.  
I use Python 3.11.

```bash
python -m pip install -r requirements.txt
```

2. Copy `settings.py.example` to `settings.py` and update `mastodon_feed_url`, `post_path` and `image_path`.  
  

3. Run the script to pull toots and push to the microblog.
```bash
python mastodon_to_moi.py
```
