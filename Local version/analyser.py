# Imports
import sys
sys.path.append('../')

import csv
import datetime
import time
import json
from collections import Counter

import matplotlib.pyplot as plt

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag

from lib.media import outlet, article
from lib.data import getData, fileStringToDate

# Constants
dataVersion = 1 # Which dataset is used by the analyser
doAutoEarlyDates = False # (Dis/En) able automatic date searching 
topicWordsCount = 3 # Amount of keywords stored per day
doPOSTagging = False # (Dis/En) able POS tagging (Parts of Speech)
doTitleWordsSearch = True # (Dis/En) able only analysing articles with certain keywords in the title

setEarlyDate = datetime.datetime(2021, 9, 15)
setLateDate = datetime.datetime(2021, 12, 2)

wantedTitleWords = ["gladys", "Berejiklian"]
wantedPOS = ["NN", "NNS", "NNP", "NNPS", ]

stopWords = stopwords.words("english") 

# Get data for all the outlets 
outletFile = open("Media Outlets.csv", "r", encoding="utf-8")
outletsList = getData(outletFile)
outletFile.close()

earliestDate = datetime.datetime.fromtimestamp(time.time())
latestDate =  datetime.datetime(2021, 1, 1, 0, 0, 0)


def daterange(date1, date2): # Returns list of dates between 2 dates
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)


# Convert JSON data to python classes
outletList = []
for outletsIndex, outlets in enumerate(outletsList):
    thisOutletFile = open("data/" + str(dataVersion) + "/json/" + outlets[0] + ".json", "r", encoding="utf-8")
    thisOutletData = json.load(thisOutletFile)
    thisOutletFile.close()
    thisOutlet = outlet(thisOutletData["name"])
    outletList.append(thisOutlet)
    
    for articleDict in thisOutletData["articles"]:
        # Calculate earliest and latest dates an article was written
        articleDate = datetime.datetime.fromtimestamp(articleDict["date"])
        if articleDate < earliestDate:
            earliestDate = articleDate
        if articleDate > latestDate:
            latestDate = articleDate

        thisArticle = article(articleDict["headline"], articleDict["description"], articleDict["author"], articleDate, articleDict["intensityScore"])
        thisOutlet.addArticle(thisArticle)

print("Data Loaded")

if doAutoEarlyDates == False:
    earliestDate = setEarlyDate
    latestDate = setLateDate

earliestDate = earliestDate.replace(hour=0, minute=0)
latestDate = latestDate.replace(hour=0, minute=0)

# Get dayDict for each outlet
for mediaIndex, mediaOutlet in enumerate(outletList):
    # mediaOutlet = outletList[0]
    # mediaIndex = 0
    excludedCount = 0 # Counter that tracks how many articles are excluded due to search parameters
    dayDict = {}
    for date in daterange(earliestDate, latestDate):
        dayDict[date] = {}
        dayDict[date]["articles"] = []

    for article in mediaOutlet.articleList:
        articleDate = article.date.replace(hour=0, minute=0)
        try:
            if doTitleWordsSearch:
                for word in word_tokenize(article.headline):
                    if word.lower() in wantedTitleWords:
                        dayDict[articleDate]["articles"].append(article)
                        break
            else:
                dayDict[articleDate]["articles"].append(article)

        except KeyError:
            excludedCount += 1

    # Get average sentiment for day
    for date in list(dayDict.keys()):
        totalSentiment = 0
        for articleIndex, article in enumerate(dayDict[date]["articles"]):
            totalSentiment += article.sentimentScore
        try:
            dayDict[date]["avgSentiment"] = totalSentiment / len(dayDict[date]["articles"])
        except ZeroDivisionError:
            dayDict[date]["avgSentiment"] = 0

    # Get keywords for day
    for dateIndex, date in enumerate(list(dayDict.keys())):
        articleWords = []
        for article in dayDict[date]["articles"]:
            for word in word_tokenize(article.headline):
                articleWords.append(word)

        filteredWords = []
        for word in articleWords:
            if word.lower() not in stopWords:
                if len(word) > 2:
                    if doPOSTagging:
                        if pos_tag([word])[0][1] in wantedPOS:
                            filteredWords.append(word)
                    else:
                        filteredWords.append(word)
        filteredWords = list(Counter(filteredWords).most_common(topicWordsCount))
        dayDict[date]["topicWords"] = filteredWords
        if doPOSTagging:
            print(str(dateIndex) + "/" + str(len(list(dayDict.keys()))))
    mediaOutlet.setDayDict(dayDict)

    print(str(mediaIndex + 1) + "/" + str(len(outletList)))

# Plot things
for mediaOutlet in outletList:
    #mediaOutlet = outletList[0]
    yList = []
    for date in list(mediaOutlet.dayDict.keys()):
        yVal = len(mediaOutlet.dayDict[date]["articles"])
        yList.append(yVal)
        try:
            plt.annotate(str(mediaOutlet.dayDict[date]["topicWords"][0][0]), [date, yVal])
        except IndexError: # If date had no articles published, no topicwords are present
            pass

    plt.plot(list(mediaOutlet.dayDict.keys()), yList, label=mediaOutlet.name)

    plt.legend()
    #plt.ylim(-1, 1)
    plt.show()