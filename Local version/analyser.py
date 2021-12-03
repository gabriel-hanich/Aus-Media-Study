# Imports
import sys
sys.path.append('../')

import csv
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import json

from lib.media import outlet, article
from lib.data import getData, fileStringToDate

# Constants
dataVersion = 1

# Get data for all the outlets 
outletFile = open("Media Outlets.csv", "r", encoding="utf-8")
outletsList = getData(outletFile)
outletFile.close()

# Convert JSON data to python classes
outletList = []
for outletsIndex, outlets in enumerate(outletsList):
    thisOutletFile = open("data/" + str(dataVersion) + "/json/" + outlets[0] + ".json", "r", encoding="utf-8")
    thisOutletData = json.load(thisOutletFile)
    thisOutletFile.close()
    thisOutlet = outlet(thisOutletData["name"])
    outletList.append(thisOutlet)
    
    for articleDict in thisOutletData["articles"]:
        articleDate = datetime.datetime.fromtimestamp(articleDict["date"])
        thisArticle = article(articleDict["headline"], articleDict["description"], articleDict["author"], articleDate, articleDict["intensityScore"])
        thisOutlet.addArticle(thisArticle)

print("Data Loaded")