# Convert .csv files into .json files
import csv
import time
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import json

from lib.media import outlet, article
from lib.data import getData, fileStringToDate


# Constants
dataVersion = 2
analyser = SentimentIntensityAnalyzer()
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
        for thisHeadline in outletData:
            if fileStringToDate(thisHeadline[3], monthsDict).replace(hour=0, minute=0).strftime("%d/%m/%Y") == thisDate:
                intensityScore = analyser.polarity_scores(thisHeadline[0])["compound"]
                dayDict[thisDate].append({"headline": thisHeadline[0], "description": thisHeadline[1], "author":thisHeadline[2], "intensityScore":intensityScore})
    with open("data/" + str(dataVersion) + "/json/" + thisOutlet.name + ".json", "w", encoding='utf-8') as outletOutPutFile:
        json.dump(dayDict, outletOutPutFile, indent=4, ensure_ascii=False)
    print(str(outletIndex + 1) + "/" + str(len(outletsList)))