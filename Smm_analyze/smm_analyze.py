import argparse

from dotenv import load_dotenv

import fb_stats as fb
import vk_stats as vks
import insta_stats as insta


def main():
    load_dotenv()
    analyze_social_media()


def analyze_social_media():
    sm_name = parse_socmedia_name()
    if sm_name == 'vk':
        vks.show_vkontakte_stats()
    elif sm_name == 'instagram':
        insta.show_insta_stats()
    elif sm_name == 'facebook':
        fb.show_facebook_stats()
    else:
        print('Wrong social media name. Read help.')


def parse_socmedia_name():
    parser = argparse.ArgumentParser(
        description='Программа проведет анализ выбранной соцсети'
    )
    parser.add_argument('socmedia_name', help='Название соцсети из списка: vk, instagram, facebook', type=str)
    args = parser.parse_args()
    sm_name = args.socmedia_name
    return sm_name.lower()


if __name__ == '__main__':
    main()
