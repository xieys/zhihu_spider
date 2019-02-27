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
                'cookie': 'd_c0="AACnkZyY1Q2PTok7Ubw6wOlJZDWvBBk1Mbk=|1530452493";'
                          '_zap=43073ef8-3c79-4869-ac38-e1b1e92a5686;_xsrf=c6MLgFIwo7uTEdeXM8N5I6inmnT7mU79;'
                          'tst=r;q_c1=1f6c2295ca254d28a35d4b9424a3f618|1551097311000|1530452493000;'
                          'tgw_l7_route=f2979fdd289e2265b2f12e4f4a478330;'
                          'capsion_ticket="2|1:0|10:1551098005|14:capsion_ticket|'
                          '44:MmQ0MzM4OWNiNTE1NDRlNjg4N2U4MmM1ZmQ3MDhjZjU=|'
                          '7c1a57cf0baf958a705d9a673c165e4b8a8b13eb62cbdebb137b0d0ae500b6b7";'
                          'z_c0="2|1:0|10:1551098048|4:z_c0|'
                          '92:Mi4xTHBZaUF3QUFBQUFBQUtlUm5KalZEU2NBQUFDRUFsVk53RzJiWEFEeHZJRHhIYU5ndj'
                          'RBVFhuR1k5TVdDb3I2eUtn|d83abaaa83d3636e8fb8b248e02413a1ead9ec8215a6eee7775c1ec8e950382e"'
            }
            # headers = {
            #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            #                   '(KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'
            # }
            r = requests.get(url, headers=headers)
            # 爬取延时
            time.sleep(0.2)
            print(r.status_code)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                return r.text
        return None

    def get_following_urls(self, userinfo_page_url, userinfo_html):
        if not userinfo_html:
            return None
        userinfo_html = etree.HTML(userinfo_html)
        following_num = \
            userinfo_html.xpath(
                '//div[@class="NumberBoard FollowshipCard-counts NumberBoard--divider"]//strong/text()')[0]
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
        user_page_html = etree.HTML(user_page_html)
        username = user_page_html.xpath('//span[@class="ProfileHeader-name"]/text()')[0]
        following_num = \
            user_page_html.xpath(
                '//div[@class="NumberBoard FollowshipCard-counts NumberBoard--divider"]//strong/text()')[0]
        followers_num = \
            user_page_html.xpath(
                '//div[@class="NumberBoard FollowshipCard-counts NumberBoard--divider"]//strong/text()')[1]
        user_avatar_url = user_page_html.xpath('//img[@class="Avatar Avatar--large UserAvatar-inner"]/@src')[0]
        userinfo_detail_items = user_page_html.xpath('//div[@class ="ProfileHeader-infoItem"]')
        if userinfo_detail_items:
            userinfo_detail = {
                'jobs': userinfo_detail_items[0].xpath('.//text()'),
                'school': userinfo_detail_items[1].xpath('.//text()')
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
        userinfo = self.get_userinfo(userinfo_url, user_page_html)
        following_urls = self.get_following_urls(userinfo_url, user_page_html)
        for following_url in following_urls:
            following_html = self.get_page_html(following_url)
            new_urls.extend(self.get_new_urls(following_html))
        return userinfo, new_urls
        # print(userinfo, new_urls)


if __name__ == '__main__':
    page_url = 'https://www.zhihu.com/people/zhouyuan'
    a = Crawler()
    # html = a.get_page_html(page_url)
    # urls = a.get_following_urls(page_url, html)
    # for url in urls:
    #     print(url)
    #     follow_json = a.get_page_html(url)
    #     a.get_new_urls(follow_json)
    #     break
    # follow_json = a.get_page_html(urls[0])
    # a.get_new_urls(follow_json)
    # a.get_userinfo(html)
    a.main(page_url)
