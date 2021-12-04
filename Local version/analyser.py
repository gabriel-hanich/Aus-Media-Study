# Imports
import sys
sys.path.append('../')

import csv
import datetime
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import json
import matplotlib.pyplot as plt

from lib.media import outlet, article
from lib.data import getData, fileStringToDate

# Constants
dataVersion = 1
doAutoEarlyDates = False

setEarlyDate = datetime.datetime(2021, 9, 15)
setLateDate = datetime.datetime(2021, 12, 2)


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
for mediaOutlet in outletList:
    excludedCount = 0 # Counter that tracks how many articles are excluded due to search parameters
    dayFreqDict = {}
    for date in daterange(earliestDate, latestDate):
        dayFreqDict[date] = {}
        dayFreqDict[date]["articles"] = []
    
    for article in mediaOutlet.articleList:
        articleDate = article.date.replace(hour=0, minute=0)
        try:
            dayFreqDict[articleDate]["articles"].append(article)
        except KeyError:
            excludedCount += 1
    
    for date in list(dayFreqDict.keys()):
        totalSentiment = 0
        for articleIndex, article in enumerate(dayFreqDict[date]["articles"]):
            totalSentiment += article.sentimentScore
        try:
            dayFreqDict[date]["avgSentiment"] = totalSentiment / articleIndex
        except ZeroDivisionError:
            dayFreqDict[date]["avgSentiment"] = 0

    mediaOutlet.setDayDict(dayFreqDict)


# Plot things
for mediaOutlet in outletList:
    yList = []
    for date in list(mediaOutlet.dayDict.keys()):
        yList.append(mediaOutlet.dayDict[date]["avgSentiment"])

    plt.plot(list(mediaOutlet.dayDict.keys()), yList, label=mediaOutlet.name)

plt.legend()
plt.ylim(-1, 1)
plt.show()