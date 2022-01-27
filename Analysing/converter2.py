# Use flair sentiment analysis

import csv
import time
import datetime
import json

from flair.models import TextClassifier
from flair.data import Sentence

import sys
sys.path.append('../') # Allows importing of local modules

from lib.media import outlet, article
from lib.data import getData, fileStringToDate


# Constants
dataVersion = 3
classifier = TextClassifier.load('en-sentiment')
monthsDict = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12
}


# Read available media outlets 
mediaFile = open("Media Outlets.csv", "r", encoding="utf-8")
mediaData = getData(mediaFile)
mediaFile.close()

print(str(len(mediaData)) + " Outlets detected")

# Convert into classes
outletsList = []
for thisOutlet in mediaData:
    outletsList.append(outlet(thisOutlet[0]))

def daterange(date1, date2): # Returns list of dates between 2 dates
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)

def getSentiment(headline, analyser):
    headline = Sentence(headline)
    analyser.predict(headline)
    if headline.labels[0].value == "NEGATIVE":
        return headline.labels[0].score * -1
    else:
        return headline.labels[0].score
    return score

print("Running")
for outletIndex, thisOutlet in enumerate(outletsList):
    earliestDate = datetime.datetime.fromtimestamp(time.time())
    latestDate = datetime.datetime(2021, 1, 1)
    outletDataFile = open("data/" + str(dataVersion) + "/csv/" + thisOutlet.name + ".csv", "r", encoding='utf-8')
    outletData = getData(outletDataFile)
    outletDataFile.close()


    articleList = []
    for thisArticle in outletData:
        thisDate = fileStringToDate(thisArticle[3], monthsDict)
        thisDate = thisDate.replace(hour=0, minute=0)
        if thisDate < earliestDate:
            earliestDate = thisDate
        if thisDate > latestDate:
            latestDate = thisDate

    dayDict = {}
    for date in daterange(earliestDate, latestDate):
        thisDate = date.strftime("%d/%m/%Y")
        dayDict[thisDate] = []
        for headlineIndex, thisHeadline in enumerate(outletData):
            if fileStringToDate(thisHeadline[3], monthsDict).replace(hour=0, minute=0).strftime("%d/%m/%Y") == thisDate:
                intensityScore = getSentiment(thisHeadline, classifier)
                dayDict[thisDate].append({"headline": thisHeadline[0], "description": thisHeadline[1], "author":thisHeadline[2], "intensityScore":intensityScore})
                print(str(headlineIndex + 1) + "/" + str(len(outletData)) + "  " + str(outletIndex + 1) + "/" + str(len(outletsList)))
    with open("data/" + str(dataVersion) + "/json/" + thisOutlet.name + ".json", "w", encoding='utf-8') as outletOutPutFile:
        json.dump(dayDict, outletOutPutFile, indent=4, ensure_ascii=False)
    print(str(outletIndex + 1) + "/" + str(len(outletsList)))