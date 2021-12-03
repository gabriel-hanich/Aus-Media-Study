class outlet:
    def __init__(self, name):
        self.name = name
        self.articleList = []

    def addArticle(self, article):
        self.articleList.append(article)

class article:
    def __init__(self, headline, description, author, date, intensityScore):
        self.headline = headline
        self.description = description
        self.author = author
        self.date = date
        self.intensityScore = intensityScore