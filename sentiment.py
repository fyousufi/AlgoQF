import re
import requests
import urllib2
from boilerpipe.extract import Extractor
from BeautifulSoup import BeautifulSoup

def get_google_news(stock, num_links):
    links = set()
    for i in range(0, num_links, 10):
        url = "https://www.google.com/search?tbm=nws&q=%s+stock&start=%d" % (stock, i)
        page = requests.get(url).content
        soup = BeautifulSoup(page)
        curr_links = soup.findAll("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)"))
        for link in curr_links:
            links.add((link['href'].replace("/url?q=","")).split("&sa")[0])
    return links

if __name__ == "__main__":
    links = get_google_news("google", 100)
    for link in links:
        print link
        print "---"
        try:
            extractor = Extractor(extractor='ArticleExtractor', url=link)
            print extractor.getText()
        except:
            pass
