import os
import requests
import dateutil.parser as dateparser
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


def main():
    load_dotenv()
    show_facebook_stats()

def show_facebook_stats():
    latest_comments, user_reaction_stats = get_facebook_stats()
    print(
        'Latest commenters:\n', 
        latest_comments, 
        '\nUser reaction stats:\n', 
        user_reaction_stats,
    )

def get_facebook_stats():
    group_id = get_fb_group_id()
    all_posts = get_all_posts_fb(group_id)
    all_comments = get_all_comments_fb(all_posts)
    latest_comments = collect_latest_commenters_fb(all_comments)
    all_reactions = get_all_reactions(all_posts)
    user_reaction_stats = collect_reaction_stats(all_reactions)
    return latest_comments, user_reaction_stats

def get_fb_group_id(group_number=0):
    method_name = 'me/groups'
    payload = {}
    response = make_fb_api_request(method_name, payload)
    group_id = response['data'][group_number]['id']
    return group_id

def make_fb_api_request(method_name, params):
    fb_token = os.getenv('FB_TOKEN')
    url = f'https://graph.facebook.com/{method_name}'
    payload = {
        'access_token': fb_token
    }
    payload.update(params)
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()

def get_all_posts_fb(group_id):
    method_name = f'{group_id}/feed'
    payload = {}
    response = make_fb_api_request(method_name, payload)
    fetched_posts = response['data']
    all_posts = [post['id'] for post in fetched_posts]
    have_new_page = True
    while True:
        fetched_posts, response = fetch_next_page_data(response)
        if not fetched_posts: break
        all_posts.extend([post['id'] for post in fetched_posts])
    return all_posts

def fetch_next_page_data(response):
    url = response['paging']['next']
    response = requests.get(url)
    response.raise_for_status()
    fetched_data = response.json()['data']
    return fetched_data, response.json()

def get_all_comments_fb(all_posts):
    payload = {'filter': 'stream',}
    all_comments = []
    for post in all_posts:
        method_name = f'{post}/comments'
        response = make_fb_api_request(method_name, payload)
        all_comments.extend(response['data'])
    return all_comments

def collect_latest_commenters_fb(all_comments, days_number=30):
    now_time = datetime.now(timezone.utc)
    latest_commenters = set()
    for comment in all_comments:
        comment_time = dateparser.parse(comment['created_time'])
        if now_time - comment_time > timedelta(days=days_number): continue
        latest_commenters.add(comment['from']['id'])
    return latest_commenters

def get_all_reactions(all_posts):
    payload = {}
    all_reactions = []
    for post in all_posts:
        method_name = f'{post}/reactions'
        response = make_fb_api_request(method_name, payload)
        all_reactions.extend(response['data'])
    return all_reactions

def collect_reaction_stats(all_reactions):
    reaction_stats = {}
    for reaction in all_reactions:
        user_id = reaction['id']
        reaction_type = reaction['type']
        if not user_id in reaction_stats:
            reaction_stats.update({user_id: {
                                    'LIKE': 0,
                                    'LOVE': 0,
                                    'WOW': 0,
                                    'HAHA': 0, 
                                    'SAD': 0, 
                                    'ANGRY': 0, 
                                    'THANKFUL': 0,
                                }
            })
        reaction_stats[user_id][reaction_type] += 1
    return reaction_stats

if __name__ == '__main__':
    main()