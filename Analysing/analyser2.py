# Imports
from ctypes import pointer
import json
from os import execv, stat
from typing import Counter
import matplotlib.pyplot as plt
from datetime import date, datetime
import datetime as dt

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.util import pr

from lib.data import getData
from lib.media import outlet, article

# Constants
dataVersion = 1
stopwords = stopwords.words("english")


def daterange(date1, date2): # Returns list of dates between 2 dates
    for n in range(int((date2 - date1).days)+1):
        yield date1 + dt.timedelta(n)



with open("Media Outlets.csv") as outletsFile:
    outletsData = getData(outletsFile)

outlets = []
for thisOutlet in outletsData:
    outlets.append(outlet(thisOutlet[0]))

    with open("data/" + str(dataVersion) + "/json/" + thisOutlet[0] + ".json", encoding="utf-8") as dataFile:
        outlets[-1].setDayDict(json.load(dataFile))
    


def getXYVals(outlet, statType, startDate, endDate, titleSearchWords, commonWordCount):
    xVals = []
    yVals = []
    zVals = []
    for myDate in list(daterange(startDate, endDate)):
        try:
            articleCount = 0
            avgSentiment = 0
            commonWords = []
            totalWords = []
            for articleIndex, article in enumerate(outlet.dayDict[myDate.strftime("%d/%m/%Y")]):
                if titleSearchWords == [] or set(titleSearchWords).intersection(word_tokenize(article["headline"].lower())):
                    articleCount += 1
                    avgSentiment += article["intensityScore"]
                    for word in word_tokenize(article["headline"]):
                        if len(word) > 2:
                            if word not in stopwords:
                                totalWords.append(str(word))

            commonWords = Counter(totalWords).most_common(commonWordCount)
                    
            if statType == "articleCount":
                yVals.append(articleCount)
            elif statType == "avgSentiment":
                try:
                    yVals.append(avgSentiment / articleCount)
                except ZeroDivisionError:
                    yVals.append(0)
            elif statType  == "commonWords":
                yVals.append(articleCount)
                zVals.append(commonWords)

            xVals.append(myDate)
        except KeyError:
            pass
    return xVals, yVals, zVals


# Plot things
startingDate = "13/9/2021"
endDate = "9/1/2022"

doSetDates = True # Whether to use user-specified dates
doSetOutlets = False # Whether to limit search to a set of outlets
commonWordCount = 1 # How many common words per day are displayed
titleSearchWords = ["covid", "covid-19", "variant", "omicron", "vaccine"] # Only include articles with headlines containing these words (Leave BLANK to disable)
setOutlets = ["ABC News"] # Only include a set of outlets
chartType = "articleCount"


if doSetOutlets:
    newOutlets = []
    for outlet in outlets:
        if outlet.name in setOutlets:
            newOutlets.append(outlet)
    outlets = newOutlets



startingDate = datetime.strptime(startingDate, "%d/%m/%Y")
endDate = datetime.strptime(endDate, "%d/%m/%Y")


# Plot daily article count
for mediaOutlet in outlets:
    try:
        if not doSetDates:
            startingDate = list(mediaOutlet.dayDict.keys())[0]
            endDate = list(mediaOutlet.dayDict.keys())[-1]

            startingDate = datetime.strptime(startingDate, "%d/%m/%Y")
            endDate = datetime.strptime(endDate, "%d/%m/%Y")

    except IndexError:
        continue

    xVals, yVals, zVals = getXYVals(mediaOutlet, chartType, startingDate, endDate, titleSearchWords, commonWordCount)

    plt.plot(xVals, yVals, label=mediaOutlet.name)   
    
    if len(zVals) != 0:
        for dayIndex, dayPoint in enumerate(zVals):
            for i in range(len(dayPoint)):
                plt.annotate(dayPoint[i][0], (xVals[dayIndex], yVals[dayIndex] - i))

plt.legend()
plt.show()    




