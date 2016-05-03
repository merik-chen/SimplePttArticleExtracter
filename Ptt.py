#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Selector
import requests
import time
import re


class Ptt(object):
    def __init__(self):
        pass

    @staticmethod
    def make_get_request(url, payload=None, headers=None, is_json=True):
        req = requests.get(
            url,
            params=payload,
            headers=headers and headers or {}
        )

        if 200 >= req.status_code <= 299:
            if is_json:
                return req.json()
            else:
                return req.content
        else:
            return None

class Article(Ptt):
    def __init__(self):
        super(Article, self).__init__()

    def get(self, board, article, with_raw=False):
        target = 'https://www.ptt.cc/bbs/%s/%s.html' % (board, article)

        resp = self.make_get_request(
            target,
            headers={
                'cookie': ';over18=1;'
            },
            is_json=False
        )

        if resp:

            article = {
                'url': target,
                'board': board,
                'article': article
            }

            selector = Selector(text=resp)
            body = selector.css('#main-content').extract()
            body = re.sub(ur'<div.+>.+</div>\n', '', body[0])
            body = re.sub(re.compile(ur'--.+', re.DOTALL), '', body)

            article['body'] = body

            for test in selector.css('span.f2::text'):
                valid_ip_regex = re.compile(ur'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
                text_txt = test.extract().encode('utf-8').strip()
                text_find = re.search(valid_ip_regex, text_txt)
                if text_find:
                    ip = text_find.group()
                    article['ip'] = ip

            for index, info in enumerate(selector.css('#main-content > div[class*="article-metaline"]')):
                title = info.css('span.article-meta-tag::text').extract()
                title = len(title) > 0 and title[0] or None

                if u'作者' == title:
                    author = info.css('span.article-meta-value::text').extract()
                    author = len(author) > 0 and author[0] or None
                    author_regex = re.compile(ur'^(.+) \((.+)\)$')
                    author = re.findall(author_regex, author)
                    for _index, value in enumerate(author[0]):
                        if 0 == _index:
                            article['author'] = value
                        if 1 == _index:
                            article['nick'] = value

                if u'標題' == title:
                    _title = info.css('span.article-meta-value::text').extract()
                    _title = len(title) > 0 and _title[0] or None
                    if _title:
                        article['title'] = _title

                if u'時間' == title:
                    # Sun Mar  6 20:46:11 2016
                    date = info.css('span.article-meta-value::text').extract()
                    date = len(title) > 0 and date[0] or None
                    if date:
                        article['date'] = int(time.mktime(time.strptime(date, "%a %b %d %H:%M:%S %Y")))

            article['like'] = 0  # 推
            article['dislike'] = 0  # 噓
            article['comments'] = []

            for index, push in enumerate(selector.css('#main-content > div.push')):
                symbol = push.css('span.push-tag::text').extract()[0].strip()
                if symbol == u'推':
                    article['like'] += 1
                if symbol == u'噓':
                    article['dislike'] += 1

                comment = {
                    'comment': push.css('span.push-content::text').extract_first(),
                    'user': push.css('span.push-userid::text').extract_first(),
                    'tag': push.css('span.push-tag::text').extract_first().strip()
                }

                article['comments'].append(comment)

            if with_raw:
                return article, resp
            else:
                return article
        else:
            return None


if '__main__' == __name__:
    ptt_article = Article()
    rsp = ptt_article.get('StupidClown', 'M.1462275619.A.150', False)
    print(rsp)
