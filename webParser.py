import feedparser
import requests
import re
import json
from html import unescape


class webParser:
    """
    A simple class to parse articles from the web
    Use it with
    webParser.parseGuardianPage(uri, fd)
    or
    webParser.getUrisFromRss(rssUri)
    """

    token = '4e0d09d001b1e2d0250d584ce7ac55fa14e1197f'

    def parse(self, url):
        # with self.readbilityGet(url) as article:
        article = self.readbilityGet(url)
        return self.parseText(article)

    def parseText(self, article):
        # Deals with anything resembling <something>
        article = re.sub(r"<.*?>", "", article)
        # Remove special characters
        article = unescape(article)
        return article

    def readbilityGet(self, url):
        json_response = requests.get('https://www.readability.com/api/content'
                                     '/v1/parser?url=' + url + '&token=' +
                                     self.token)

        # Then extract content from json data :
        article = json.loads(json_response.text)['content']
        return article

    def getUrisFromRss(rssUri):
        """
        Get all the articles from the given RSS feed
        """
        rss = feedparser.parse(rssUri)
        return [item.link for item in rss.entries]
