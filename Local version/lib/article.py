class article:
    def __init__(self, headline, description, author, publishDate, mediaOutlet):
        super().__init__()
        self.headline = headline
        self.description = description
        self.author = author
        self.publishDate = publishDate
        self.mediaOutlet = mediaOutlet

    def toString(self):
        return self.headline + "\n" + self.description + "\n By " + self.author


def cleanText(text):
    if text == "</dc:creator>":
        text = "None found"
    if "<p>" in text:
        text = text[3:-2]
    if 'title="' in text:
        text = text[text.find('title="') + 25 : -3]
    if "</div>" in text:
        text = text[text.find("</div>") + 6 :]
    if "&lt;" in text:
        text = text[: text.find("&lt;")]
    if text == "<![CDATA[ ]]>":
        text = "None found"
    elif text[:9] == "<![CDATA[":
        text = text[9:-3]
    text.replace("</", "")
    text.replace("</", "")
    text.replace(">", "")
    return text


class dayPeriod:
    def __init__(self, date, freq, commonWord, avgSentiment):
        self.date = date
        self.freq = freq
        self.commonWord = commonWord
        self.avgSentiment = avgSentiment
        self.relatedWords = []
    
    def setRelatedWords(self, relatedWords):
        self.relatedWords.append(relatedWords)

class relatedWords:
    def __init__(self, wordName, data):
        self.data = data
        self.wordName = wordName
        self.nextLink = ""
        self.linkScore = 0.0

    def toList(self):
        return self.data

    def setLink(self, link, score):
        self.nextLink = link 
        self.linkScore = score

class outlet:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.articleList = []
        self.daysList = []

    def addArticle(self, article):
        self.articleList.append(article)

    def getArticles(self):
        return self.articleList

    def addDays(self, days):
        self.daysList.append(days)

    def getDays(self):
        return self.daysList

