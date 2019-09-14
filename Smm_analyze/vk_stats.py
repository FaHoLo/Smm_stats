import os
import vk_api
from dotenv import load_dotenv
from datetime import datetime, timedelta


def main():
    load_dotenv()
    show_vkontakte_stats()

def show_vkontakte_stats():
    core_audience = get_vkontakte_core_audience()
    print('Core audience:\n', core_audience)

def get_vkontakte_core_audience():
    vk = customize_vk_api()
    company_name = os.getenv('COMPANY_NAME_VK')
    vk_group_id = vk.groups.getById(group_ids=company_name)[0]['id']
    vk_group_id = f'-{vk_group_id}'
    all_posts = get_all_posts_vk(vk, vk_group_id)
    all_comments = get_all_comments_vk(vk, vk_group_id, all_posts)
    latest_comments = collect_latest_comments(all_comments)
    all_commenters = collect_commenters(latest_comments, vk_group_id)
    all_likers = get_all_likers(vk, latest_comments, vk_group_id)
    core_audience = all_commenters.intersection(all_likers) 
    return core_audience

def customize_vk_api():
    vk_service_key = os.getenv('VK_SERVICE_KEY')    
    vk_api_version = '5.101'
    vk_session = vk_api.VkApi(token=vk_service_key, api_version=vk_api_version)
    vk = vk_session.get_api()
    return vk

def get_all_posts_vk(vk, vk_group_id):
    posts_number = 101
    fetched_posts_number = 0
    count = 100
    all_posts = []
    while fetched_posts_number < posts_number:
        response = vk.wall.get(owner_id=vk_group_id, offset=fetched_posts_number, count=count)
        posts_number = response['count']
        fetched_posts_number += count
        all_posts.extend(response['items'])
    return all_posts

def get_all_comments_vk(vk, vk_group_id, all_posts):
    all_comments = []
    for post in all_posts:
        post_comments = get_post_comments(vk, post['id'], vk_group_id)
        all_comments.extend(post_comments) 
    return all_comments

def get_post_comments(vk, post_id, group_id):
    count = 100
    comments_number = 101
    fetched_comments_number = 0 
    post_comments = []
    while fetched_comments_number < comments_number:
        response = vk.wall.getComments(owner_id=group_id, post_id=post_id, thread_items_count=10,
                                       offset=fetched_comments_number, count=count)
        comments_number = response['count']
        fetched_comments = response['items']
        post_comments.extend(fetched_comments)
        fetched_comments_number += count
        thread_comments, fetched_comments_number = collect_thread_comments(fetched_comments, 
                                                                           fetched_comments_number)
        post_comments.extend(thread_comments)
    return post_comments

def collect_thread_comments(fetched_comments, fetched_comments_number):
    thread_comments = []
    for comment in fetched_comments:
        number_of_thread_comments = comment['thread']['count']
        if number_of_thread_comments:
            thread_comments.extend(comment['thread']['items']) 
            fetched_comments_number += number_of_thread_comments
    return thread_comments, fetched_comments_number

def collect_latest_comments(comments, days_number=14):
    now_time = datetime.now()
    latest_comments = []
    for comment in comments:
        comment_time = datetime.fromtimestamp(comment['date'])
        if now_time - comment_time > timedelta(days=days_number): continue
        latest_comments.append(comment)
    return latest_comments

def collect_commenters(comments, vk_group_id):
    all_commenters = set()
    for comment in comments:
        try: 
            commenter_id = comment['from_id']
        except KeyError: 
            continue   
        if commenter_id == int(vk_group_id): continue
        all_commenters.add(commenter_id)
    return all_commenters

def get_all_likers(vk, comments, vk_group_id):
    all_likers = set()
    processed_posts = []
    for comment in comments:
        try: 
            post_id = comment['post_id']
        except KeyError: 
            continue
        if post_id in processed_posts: continue
        post_likers = get_post_likers(vk, vk_group_id, post_id)
        all_likers.update(post_likers)
        processed_posts.append(post_id)
    return all_likers

def get_post_likers(vk, vk_group_id, post_id):
    likes_number = 1001
    count = 1000
    post_likers = []
    fetched_likes_number = 0
    while fetched_likes_number < likes_number:
        response = vk.likes.getList(type='post', owner_id=vk_group_id, item_id=post_id,
                                    offset=fetched_likes_number, count=count)
        likes_number = response['count']
        fetched_likes_number += count
        post_likers.extend(response['items'])
    return post_likers

if __name__ == '__main__':
    main()