import csv
import datetime

def GetData(data):
    csvReader = csv.reader(data)

    result = []
    for row in csvReader:
        result.append(row)
    
    return result

def fileStringToDate(dateString, monthIndexes):
    hour = int(dateString[dateString.find(":") - 2: dateString.find(":")])
    minutes = int(dateString[dateString.find(":")+ 1: dateString.find(":") + 3])

    day = int(dateString[dateString.find(",") + 2: dateString.find(",") + 4])
    month = monthIndexes[dateString[dateString.find(",") + 5: dateString.find(",") + 8].lower()]
    year = int(dateString[dateString.find(",") + 9: dateString.find(",") + 13])
    return datetime.datetime(year, month, day, hour, minutes)
