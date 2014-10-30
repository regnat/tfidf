import html5lib
import requests
import tfidf


class guardianParser:
    """
    A simple class to parse articles from the guardian for tf-idf
    Use it with
    guardianParser.parseGuardianPage(uri)
    or
    guardianParser.parseRss(RssUri)
    """

    def parseGuardianPage(uri):
        """
        Parse a single article
        """
        r = requests.get(uri)
        doc = html5lib.parse(r.text)
        mainNode = None

        tf = tfidf.tfIdf()

        for node in doc.findall(".//{http://www.w3.org/1999/xhtml}div"):
            if ('class', 'flexible-content-body') in node.items():
                mainNode = node
                break

        if (mainNode):
            for node in mainNode.findall('.//*'):
                if (node.text):
                    tf.addStringToCorpus(node.text)

    def getUrisFromRss(rssUri):
        """
        Get all the articles from the given RSS feed
        """
        r = requests.get(rssUri)
        rss = html5lib.parse(r.text)
        return [item.find(".//{http://www.w3.org/1999/xhtml}link").tail for
                item in rss.findall(".//{http://www.w3.org/1999/xhtml}item")]

    def parseRss(rssUri):
        """
        Parse all the articles present in the given RSS feed
        """
        for uri in guardianParser.getUrisFromRss(rssUri):
            guardianParser.parseGuardianPage(uri)
