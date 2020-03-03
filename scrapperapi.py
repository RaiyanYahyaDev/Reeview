from bottle import run, get, post, request
from bs4 import BeautifulSoup
from textblob import TextBlob
from urllib.request import Request, urlopen
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import urllib.request
import nltk
import json
import simplejson
import sentiment_mod as s


@get('/cooper')
def health():
	return {"Cooper Scraper up and running .. "}

@post('/cooper/urllist')
def crawlAndNltk():
    resultlist = []
    stop_words = set(stopwords.words('english'))
    for url in request.json.get('urls'):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req) 
        html = response.read() 
        soup = BeautifulSoup(html,"html5lib")
        
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))    
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        word_tokens = word_tokenize(text)
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        text = str(filtered_sentence)
        testimonial = TextBlob(text)
        data = {}
        data['url'] = url
        data['sentiment'] = s.sentiment(text)
        data['polarity'] = testimonial.sentiment.polarity
        data['subjectivity'] = testimonial.sentiment.subjectivity
        data['word tokens'] = FreqDist(testimonial.words).most_common(2)
        testimonial = TextBlob(' ')
        json_data = json.dumps(data)
        resultlist.append(json_data)
    return resultlist
    
run(reloader=True, debug=True)