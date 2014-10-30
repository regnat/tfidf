import html5lib
import requests


class guardianParser:
    """
    A simple class to parse articles from the guardian
    Use it with
    guardianParser.parseGuardianPage(uri, fd)
    or
    guardianParser.getUrisFromRss(rssUri)
    """

    def parseGuardianPage(uri, fd):
        """
        Parse a single article and outputs its content to a file descriptor
        """
        r = requests.get(uri)
        doc = html5lib.parse(r.text)
        mainNode = None

        for node in doc.findall(".//{http://www.w3.org/1999/xhtml}div"):
            if ('class', 'flexible-content-body') in node.items():
                mainNode = node
                break

        if (mainNode):
            for node in mainNode.findall('.//*'):
                if node.text:
                    fd.write(node.text)

    def getUrisFromRss(rssUri):
        """
        Get all the articles from the given RSS feed
        """
        r = requests.get(rssUri)
        rss = html5lib.parse(r.text)
        return [item.find(".//{http://www.w3.org/1999/xhtml}link").tail for
                item in rss.findall(".//{http://www.w3.org/1999/xhtml}item")]

