from collections import Counter
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
from instabot import Bot


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
    all_comments = {post_id: bot.get_media_comments_all(post_id) for post_id in all_post_ids}
    latest_comments = collect_latest_comments_insta(all_comments)
    comments_top = collect_comments_top(latest_comments, company_id)
    posts_top = collect_posts_top(latest_comments, company_id)
    return comments_top, posts_top


def log_into_instagram(bot):
    insta_login = os.getenv('INSTA_LOGIN')
    insta_password = os.getenv('INSTA_PASSWORD')
    bot.login(username=insta_login, password=insta_password)


def collect_latest_comments_insta(all_comments, days_number=90):
    now_time = datetime.utcnow()
    latest_comments = {
        post_id: [
            comment['user_id'] for comment in comments
            if now_time - datetime.fromtimestamp(comment['created_at_utc']) <= timedelta(days=days_number)
        ]
        for post_id, comments in all_comments.items()
    }
    return latest_comments


def collect_comments_top(comments, company_id):
    comments_top = Counter()
    for commenters in comments.values():
        comments_top.update(commenters)
    del comments_top[company_id]
    return dict(comments_top.most_common())


def collect_posts_top(comments, company_id):
    posts_top = Counter()
    for commenters in comments.values():
        post_commenters = {commenter for commenter in commenters}
        posts_top.update(post_commenters)
    del posts_top[company_id]
    return dict(posts_top.most_common())


if __name__ == '__main__':
    main()
