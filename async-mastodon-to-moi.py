# Aims
# DONE: 1. Should be a python script that syncs my Mastodon feed to my microblog
# DONE: 2. Learn to give them types and learn mypy. Learnt the basics. not for this project
# TODO: 3. Async Downloads
# TODO: 4. Switch away from `.py` and `.json` to a `sqlite.db`
# DONE: 5. It should be a standalone python utility, with no need for a system python, use freeze/typer/click?
#          not for this project. requires too much scaffolding. 
# TODO: 6. Talk to the Mastodon API to get retweets and see if that is something you want to save or publish.


# Sample micropost skeleton
# ---
# title: "2023-02-25T15:00:06+05:30"
# date: "2023-02-25T15:00:06+05:30"
# categories:
# tags:
# ---


from pathlib import Path
import datetime
import json
import asyncio
from collections import namedtuple

import aiofiles
import feedparser
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

from settings import mastodon_feed_url, post_path, image_path

microblog_post_path = Path(post_path)
microblog_image_path = Path(image_path)


# grab images from a url
async def get_img(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code:
            image_name = url.split('/')[-1]
            image_content = r.content
            return (image_name, image_content)



def load_state():
    """
    returns a state dict, loaded from a json file or defaults from dictionary in here
    """
    base_dict = {
        "last_toot_id": None,
    }
    feed_state_file = Path('feed_state.json')
    feed_state = {}
    if feed_state_file.is_file():
        with open(feed_state_file, 'r') as f2r:
            feed_state = json.load(f2r)
    else:
        print('Could not find last known state. Loading Defaults')
        feed_state = base_dict
    return feed_state


def save_state(program_state):
    with open('feed_state.json', 'w') as f2w:
        json.dump(program_state, f2w)


async def write_toots_to_posts(feed_url, feed_state):
    # Parse URL
    url_to_process, state_dict = feed_url, feed_state
    mastodon_feeds = feedparser.parse(url_to_process)
    latest_toot_id = int(mastodon_feeds.entries[0].id.split('/')[-1])

    # Process toots we get from the feed
    for toot in mastodon_feeds.entries:

        if int(toot.id.split('/')[-1]) == state_dict['last_toot_id']:
            break
        else:
            # Set up an empty dictionary to hold parsed values, that’ll serve as templated strings for the blog post
            post_dict = {
                'meta_string': "---",  # for yaml metadata boundaries in the post
                'title': None,
                'date': None,
                'categories': [],
                'tags': [],
                'tag_link_strings': [],
                'original_link': None,
                'content': [],
                'image_link_strings': [],
            }

            # Get toot date and then assign it to the post dict. used for title, date and filename in the blog post
            toot_date = datetime.datetime.strptime(toot.published, "%a, %d %b %Y %H:%M:%S %z")
            post_dict['date'] = post_dict['title'] = toot_date.strftime("%Y-%m-%dT%H:%M:%S%z")
            post_file_name = toot_date.strftime("%Y%m%d%H%M%S.md")

            # Get tags and put them in the post dict. also create tag links, so we can put them at the end of the post
            if 'tags' in toot:
                for tag in toot.tags:
                    tag_term = tag['term']
                    tag_link_string = f'[#{tag_term}](/tags/{tag_term.lower()})'
                    post_dict['tags'].append(tag_term)
                    post_dict['tag_link_strings'].append(tag_link_string)
            else:
                pass

            # Get link to the original toot.
            post_dict['original_link'] = toot.link

            # Get the toot’s content
            toot_content_soup = BeautifulSoup(toot.summary, "lxml")
            toot_content = toot_content_soup.find_all('p')
            for each_line in toot_content:
                post_dict['content'].append(markdownify(str(each_line), heading_style='atx'))
                post_dict['content'].append("{{< hbr >}}" + "  \n")

            # Get images # IN-PROGRESS: figure out how to do this asynchronously
            if 'media_content' in toot:
                # Create yearly image folder if it does not exist
                img_year = microblog_image_path.joinpath(str(toot_date.year))
                Path.mkdir(img_year, parents=True, exist_ok=True)

                image_urls_to_download = []  # build up a dict of image names & urls to download

                # if media is an image put url in the list above, generate a local link for the post on moi
                # and put it in the post dict
                for each_item in toot.media_content:
                    if 'image' in each_item['type']:
                        image_name = each_item['url'].split('/')[-1]
                        post_dict['image_link_strings'].append(
                            f"![{image_name}](/images/{str(toot_date.year)}/{image_name})")
                        image_urls_to_download.append(each_item['url'])


                # Create a task list of image urls
                image_tasks = []
                for each_img in image_urls_to_download:
                    t = asyncio.create_task(get_img(each_img))
                    image_tasks.append(t)
                # Process tasks and get images from urls
                image_results = []
                for task in asyncio.as_completed(image_tasks):
                    image_results.append(await task)

                # Write them out to files
                for img in image_results:
                    async with aiofiles.open(f"{img_year.joinpath(img[0])}" , 'wb') as f2w:
                        await f2w.write(img[1])

            else:
                pass

            # Write the post to a file
            with open(f'{microblog_post_path.joinpath(post_file_name)}', 'w') as f2w:
                f2w.write(f"{post_dict['meta_string']}\n")
                f2w.write(f"title: {post_dict['title']}\n")
                f2w.write(f"date: {post_dict['date']}\n")
                f2w.write(f"categories: {post_dict['categories']}\n")
                f2w.write(f"tags: {post_dict['tags']}\n")
                f2w.write(f"{post_dict['meta_string']}\n\n")
                if post_dict['image_link_strings']:
                    f2w.writelines('\n\n'.join(post_dict['image_link_strings']))
                f2w.writelines('  \n'.join(post_dict['content']))
                f2w.write("{{< hbr >}}\n\n")
                f2w.write(f"Original: [{post_dict['original_link']}]({post_dict['original_link']})\n\n")
                if post_dict['tag_link_strings']:
                    f2w.writelines(', '.join(post_dict['tag_link_strings']))
                f2w.write("\n\n{{< hbr >}}")

    # Save State
    state_dict['last_toot_id'] = latest_toot_id
    save_state(state_dict)


async def main(mastodon_account_rss_url):
    initial_feed_state = load_state()
    await (write_toots_to_posts(mastodon_account_rss_url, initial_feed_state))


if __name__ == "__main__":
    asyncio.run(main(mastodon_feed_url))
