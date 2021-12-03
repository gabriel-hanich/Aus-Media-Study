# Convert .csv files into .json files
import csv
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import json

from lib.media import outlet, article
from lib.data import getData, fileStringToDate


# Constants
dataVersion = 1
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
mediaFile = open("Media Outlets.csv", "r")
mediaData = getData(mediaFile)
mediaFile.close()

print(str(len(mediaData)) + " Outlets detected")

# Convert into classes
outletsList = []
for thisOutlet in mediaData:
    outletsList.append(outlet(thisOutlet[0]))

for outletIndex, thisOutlet in enumerate(outletsList):
    print(str(outletIndex + 1) + "/" + str(len(outletsList)))
    outletDataFile = open("data/" + str(dataVersion) + "/csv/" + thisOutlet.name + ".csv", "r", encoding='utf-8')
    outletData = getData(outletDataFile)
    outletDataFile.close()


    articleList = []
    outputDict = {"name": thisOutlet.name, "articles": []}
    for thisArticle in outletData:
        thisDate = fileStringToDate(thisArticle[3], monthsDict)
        intensityScore = analyser.polarity_scores(thisArticle[0])["compound"]
        articleList.append(article(thisArticle[0], thisArticle[1], thisArticle[2], thisDate, intensityScore))
        outputDict["articles"].append({"headline": thisArticle[0], "description": thisArticle[1], "author": thisArticle[2], "date": thisDate.timestamp(), "intensityScore": intensityScore})

    outletOutPutFile = open("data/" + str(dataVersion) + "/json/" + thisOutlet.name + ".json", "w", encoding='utf-8')
    json.dump(outputDict, outletOutPutFile, indent=4)
    outletOutPutFile.close()