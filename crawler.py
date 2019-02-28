# -*- coding: utf-8 -*-
import requests
from lxml import etree
import math
import json
import time


class Crawler(object):
    def get_page_html(self, url):
        """
        获取页面源码
        :param url:页面url
        :return: 页面源码
        """
        if url:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                              '(KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
                'cookie': 'cookie' #这里填写你自己的登入的cookie
            }
            r = requests.get(url, headers=headers)
            print("正在获取{}的网页源码，状态码为{}".format(url, r.status_code))
            # 爬取延时
            time.sleep(0.2)
            print(r.status_code)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
        return None

    def get_following_urls(self, userinfo_page_url, following_num):
        if not following_num:
            return None
        base_following_url = '/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2C' \
                             'follower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5' \
                             'D.topics&offset={}&limit={}'
        page_nums = math.ceil(int(following_num.replace(',', '')) / 20)
        for i in range(int(page_nums)):
            following_url = userinfo_page_url.replace('people', 'api/v4/members') + base_following_url.format(i * 20, (
                    i + 1) * 20)
            yield following_url

    def get_new_urls(self, following_json):
        """
        获取新的URL
        :param following_json:
        :return:
        """
        if not following_json:
            return None
        # 解析返回的json数据
        base_url = 'https://www.zhihu.com'
        user_urls = []
        following_info_json = json.loads(following_json)
        items = following_info_json['data']
        for item in items:
            url_type = item['type']
            url_token = item['url_token']
            user_url = base_url + '/{}/{}'.format(url_type, url_token)
            print("爬取到新的用户链接：{}".format(user_url))
            user_urls.append(user_url)
        return user_urls

    def get_userinfo(self, userinfo_url, user_page_html):
        """
        获取用户的详细信息
        :param userinfo_url:
        :param user_page_html:
        :return:
        """
        if not user_page_html:
            return None
        print('正在爬取{}'.format(userinfo_url))
        user_page_html = etree.HTML(user_page_html)
        username = "".join(user_page_html.xpath('//span[@class="ProfileHeader-name"]/text()'))
        follow_num = user_page_html.xpath(
            '//div[@class="NumberBoard FollowshipCard-counts NumberBoard--divider"]//strong/text()')
        if not follow_num:
            return None
        following_num = follow_num[0]
        followers_num = follow_num[1]
        user_avatar_url = user_page_html.xpath('//img[@class="Avatar Avatar--large UserAvatar-inner"]/@src')[0]
        userinfo_detail_items = user_page_html.xpath('//div[@class ="ProfileHeader-infoItem"]')
        if userinfo_detail_items:
            jobs = userinfo_detail_items[0].xpath('.//text()')
            if len(userinfo_detail_items) > 1:
                school = userinfo_detail_items[1].xpath('.//text()')
            else:
                school = []
            userinfo_detail = {
                'jobs': jobs,
                'school': school
            }
        else:
            userinfo_detail = []
        userinfo = {
            'username': username,
            'user_url': userinfo_url,
            'following_num': following_num,
            'followers_num': followers_num,
            'user_avatar_url': user_avatar_url,
            'userinfo_deail': userinfo_detail
        }
        print('爬取到用户信息：{}'.format(userinfo))
        return userinfo

    def main(self, userinfo_url):
        """
        主程序
        :param userinfo_url:
        :return:
        """
        new_urls = []
        user_page_html = self.get_page_html(userinfo_url)
        if user_page_html:
            userinfo = self.get_userinfo(userinfo_url, user_page_html)
            if userinfo:
                following_urls = self.get_following_urls(userinfo_url, userinfo['following_num'])
                for following_url in following_urls:
                    following_html = self.get_page_html(following_url)
                    new_urls.extend(self.get_new_urls(following_html))
                return userinfo, new_urls
        return None, None


if __name__ == '__main__':
    a = Crawler()
    a.main('https://www.zhihu.com/people/kmxz')
