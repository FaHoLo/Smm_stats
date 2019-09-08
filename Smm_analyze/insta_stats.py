import os
from instabot import Bot
from dotenv import load_dotenv
from datetime import datetime, timedelta


def main():
    load_dotenv()
    show_insta_stats()

def show_insta_stats():
    comments_top, posts_top = get_instagram_stats()
    print(
        'Comments top:\n', 
        comments_top,
        '\nPosts top:\n', 
        posts_top,
    )

def get_instagram_stats():
    bot = Bot()
    log_into_instagram(bot)
    company_name = os.getenv('COMPANY_NAME_INSTAGRAM')
    company_id = int(bot.get_user_id_from_username(company_name))
    all_post_ids = bot.get_total_user_medias(company_id)
    all_comments = get_all_comments_insta(bot, all_post_ids)
    latest_comments = collect_latest_comments_insta(all_comments)
    comments_top = collect_comments_top(latest_comments, company_id)
    posts_top = collect_posts_top(latest_comments, company_id)
    return comments_top, posts_top

def log_into_instagram(bot):
    insta_login = os.getenv('INSTA_LOGIN')
    insta_password = os.getenv('INSTA_PASSWORD')
    bot.login(username=insta_login, password=insta_password)

def get_all_comments_insta(bot, all_posts):
    all_comments = []
    for post in all_posts:
        all_comments.append(bot.get_media_comments_all(post))
    return all_comments

def collect_latest_comments_insta(all_comments, days_number=90):
    now_time = datetime.utcnow()
    latest_comments = []
    for post_comments in all_comments:
        post_latest_comments = []
        for comment in post_comments:
            comment_time = datetime.fromtimestamp(comment['created_at_utc'])
            if now_time - comment_time > timedelta(days=days_number): continue
            post_latest_comments.append(comment)
        latest_comments.append(post_latest_comments)
    return latest_comments

def collect_comments_top(comments, company_id):
    comments_top = {}
    for post_comments in comments:
        for comment in post_comments:
            commenter_id = comment['user_id']
            if commenter_id == company_id: continue
            if commenter_id not in comments_top:
                comments_top.update({commenter_id: 0})
            comments_top[commenter_id] += 1
    return comments_top

def collect_posts_top(comments, company_id):
    posts_top = {}
    for post_comments in comments:
        post_commenters = collect_post_commenters(post_comments, company_id)
        posts_top = update_posts_top(post_commenters, posts_top)
    return posts_top

def collect_post_commenters(post_comments, company_id):
    post_commenters = set()
    for comment in post_comments:
        commenter_id = comment['user_id']
        if commenter_id == company_id: continue
        post_commenters.add(commenter_id)
    return post_commenters

def update_posts_top(post_commenters, posts_top):
    for commenter in post_commenters:
        if commenter not in posts_top:
            posts_top.update({commenter: 0})
        posts_top[commenter] += 1
    return posts_top

if __name__ == '__main__':
    main()