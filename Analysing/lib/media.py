class Outlet:
    def __init__(self, name):
        self.name = name
        self.articleList = []
        self.dayDict = {}
        self.xVals, self.yVals, self.zVals = [], [], []

    def addArticle(self, article):
        self.articleList.append(article)

    def setDayDict(self, dayDict):
        self.dayDict = dayDict

    def setVals(self, xVals, yVals, zVals):
        self.xVals, self.yVals, self.zVals = xVals, yVals, zVals



class Article:
    def __init__(self, headline, description, author, date, sentimentScore):
        self.headline = headline
        self.description = description
        self.author = author
        self.date = date
        self.sentimentScore = sentimentScore