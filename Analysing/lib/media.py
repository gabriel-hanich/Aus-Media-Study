class outlet:
    def __init__(self, name):
        self.name = name
        self.articleList = []
        self.dayDict = {}

    def addArticle(self, article):
        self.articleList.append(article)

    def setDayDict(self, dayDict):
        self.dayDict = dayDict


class article:
    def __init__(self, headline, description, author, date, sentimentScore):
        self.headline = headline
        self.description = description
        self.author = author
        self.date = date
        self.sentimentScore = sentimentScore