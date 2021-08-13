import matplotlib.pyplot as plt
from lib.article import article, outlet, dayPeriod, relatedWords
from lib.reddit import getPosts
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import timedelta, datetime
import time
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv  # Imports

def getData(file):  # Function that reads data from a csv and returns as a list of  lists (columns and rows)
    csvFile = open(file, "r", encoding="utf-8")
    csvReader = csv.reader(csvFile, delimiter=",")
    data = []
    for row in csvReader:
        data.append(row)
    return data

# Constants
backupDate = "12.07.21"
searchWord = ""
analyser = SentimentIntensityAnalyzer()
thisStopwords = set(stopwords.words("english"))
commonWordsCount = 2
minSimScore = 3
minWordFreq = 2
postCount = 50
monthsIndex = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}



outletData = getData("Media Outlets.csv")  # Get the data on the media outlets used (names, url, etc)
outletListRaw = []  # List containing just the names (string) of each  outlet
for obj in outletData:
    outletListRaw.append(obj[0])


#Convert list of strings into list of media Publications
outletList = []
for mediaOutleta in outletListRaw:
    thisOulet = outlet(mediaOutleta)  # Convert this media outlet into an outlet object
    data = getData(
        "Backups/" + backupDate + "/" + mediaOutleta + ".csv"
    )  # Get article data from relavent csv file
    for headline in data:
        try:
            publishDate = headline[3]  # Get the date it was published, Howvever is in werid format
            publishDate = publishDate[publishDate.find(",") + 2 : publishDate.find(":") - 3]  # Remove unecessary parts
            publishDate = (publishDate[:2]+ "/" + str(monthsIndex[publishDate[3:6]]) + "/" + publishDate[9:])  # Add slashes and convert monthu names to number
            publishDate = datetime.strptime(publishDate, "%d/%m/%y")  # Convert to datetime object
            thisOulet.addArticle(article(headline[0], headline[1], headline[2], publishDate, outlet))  # Add this to the media objects articleList
        except KeyError:
            print("KEYERROR " + str(publishDate) + "\n" + str(headline[3]))
    outletList.append(thisOulet)

for media in outletList:

    # Generate list containing every date between the oldest and most recent article
    startDate = datetime.today()  # The latest date possible to compare against
    endDate = datetime.strptime("01/01/21", "%d/%m/%y")  # This date has to be sooner then any present in the database
    for article in media.getArticles():
        if article.publishDate < startDate:
            startDate = (article.publishDate)  # Find the earliest date an article was published
        if article.publishDate > endDate:
            endDate = (article.publishDate)  # Find the latest date an article was published

    possibleDates = []
    articleCount = 0
    daysCount = endDate - startDate
    for i in range(daysCount.days):
        day = startDate + timedelta(days=i)
        possibleDates.append(day)  
    
    for thisdate in possibleDates:
        availableHeadlines = ""  # Constants that are used by the specific 'day Period'
        totalSentiment = 0
        articleCount = 0
        for article in media.getArticles():
            if (article.publishDate == thisdate):  # If the article matches uup with the date being searched for
                if searchWord.lower() in article.headline:
                    availableHeadlines += (article.headline.lower())  # Add to string (To be tokenized and then further analyzed)
                    score = analyser.polarity_scores(article.headline)  # Get intensity score
                    totalSentiment += score["compound"]  # Add that top the average
                    articleCount += 1  # Increase the article count for this day

        availableHeadlines = word_tokenize(availableHeadlines)  # Tokenize thue headlines
        cleanHeadlines = []

        for word in availableHeadlines:
            if word not in thisStopwords:  # If the word is important
                if (len(word) > 2):  # And more then 2 letters (removes punctuation and other smaller words)
                    cleanHeadlines.append(word)
        cleanHeadlines = list(Counter(cleanHeadlines).most_common(commonWordsCount))  # Get the most comon words for this day period

        if articleCount == 0:
            avgSentiment = 0
            cleanHeadlines = [["", 0]]

        else:
            avgSentiment = float(totalSentiment / articleCount)

        media.addDays(dayPeriod(thisdate, articleCount, cleanHeadlines, avgSentiment))  # add this day to the media's 'dayList'

    print("Completed basic data gathering for " + media.name)

    # Funky reddit analysis
    wordsList = []
    rotations = 0
    thisStopwords = set(stopwords.words("english"))
    for index, today in enumerate(media.getDays()):
        for i in range(commonWordsCount):
            thisWord = today.commonWord[i][0] # Get the common word(s) for this day
            if thisWord not in wordsList: # If this word has not been seen before
                relatedList = []
                wordsList.append(thisWord)
                commons = getPosts(thisWord, postCount, thisStopwords) # Get similar words and their frequencies
                keys = list(commons.keys()) # All the similar words
                values = list(commons.values()) # All the frequencies of those similar words
                for valueIndex, value in enumerate(values):
                    if value >= minWordFreq: # Ensure the word is commmon enough to count
                        relatedList.append([keys[valueIndex], value])
                today.setRelatedWords(relatedWords(thisWord, relatedList)) # Set the related words for this day period
            else: # If the word has been seen somewhere else in the list
                sameIndex = wordsList.index(thisWord)
                foundObj = False
                k = 0
                while(foundObj == False):
                    for j in range(commonWordsCount):
                        if media.getDays()[k].relatedWords[j].wordName == thisWord:
                            today.setRelatedWords(relatedWords(thisWord, media.getDays()[k].relatedWords[j].data)) # Duplicate the related words from the copy
                            foundObj = True
                    k += 1
            rotations += 1
            print(media.name + " Scanning reddit at location " + str(rotations / (int(daysCount.days) * commonWordsCount))) # Print a loading bar
                
    # Find the most similar word to the commonWords

    for index, today in enumerate(media.getDays()):
        if index + 1 != len(media.getDays()): # If not the last day 
            tomorrow = media.getDays()[index + 1]
            for todayCount in range(commonWordsCount): # For every freq Word for that day
                todayList = []
                print("TODAY = " + today.relatedWords[todayCount].wordName)
                hiScore = minSimScore # Innit defauults
                closestLink = relatedWords("NULL", [])
                # Generate processed list containing just the similar words for today
                for i in today.relatedWords[todayCount].data: 
                    todayList.append(i[0])
                # For each commonWord today, look at all the common words tomorrow to find the closest match
                for tomorrowCount in range(commonWordsCount):
                    thisScore = 0
                    for wordPair in tomorrow.relatedWords[tomorrowCount].data:
                        if wordPair[0] in todayList:
                            thisScore += wordPair[1] + today.relatedWords[todayCount].data[todayList.index(wordPair[0])][1]
                            thisScore = round(thisScore / 2, 5)
                            # This score = Average of the two frequencies (today and yesterdays)
                    if thisScore > hiScore: # Ensure each word is linked enough
                        closestLink = tomorrow.relatedWords[tomorrowCount]
                        hiScore = thisScore
                
                if hiScore == minSimScore:
                    hiScore = 0
                print("MATCH FOR '" + today.relatedWords[todayCount].wordName + "' = '" + closestLink.wordName + "' Score = " + str(hiScore))
                today.relatedWords[todayCount].setLink(closestLink, hiScore)
    
    
    # Clean the data ig
    for today in media.getDays():
        for i in range(commonWordsCount):
            try:
                today.relatedWords[i].wordName + " - " + today.relatedWords[i].nextLink.wordName
                today.relatedWords[i].linkScore
            except AttributeError:
                today.relatedWords[i].setLink(relatedWords("NULL", []), 0)
    
    
    #Write all the data to a file in a standardised format
    fileStr = ""
    fName = ""
    media = outletList[0]
    #for media in outletList
    fName = r"Backups/" + backupDate + "/processed/" + media.name + '.txt'
    fileStr +=  "<searchWord>" + searchWord + "\n"
    fileStr += "<commonWordCount>" + str(commonWordsCount) + "\n\n"
    for todayIndex, today in enumerate(media.getDays()):
        fileStr += "<date>" + str(today.date) + "\n"
        fileStr += "<freq>" + str(today.freq) + "\n"
        fileStr += "<avgSentiment>" + str(round(today.avgSentiment, 3)) + "\n"
        for i in range(commonWordsCount):
            fileStr += "<commonWord>" + str(i) + str(today.relatedWords[i].wordName) + "\n"
            fileStr += "<commonWordFreq>" + str(i) + str(today.commonWord[i][1]) + "\n"
            fileStr +=  "<linkWordName>" + str(today.relatedWords[i].nextLink.wordName) + "\n"
            fileStr += "<linkScore>" + str(today.relatedWords[i].linkScore) + "\n"
            
        fileStr += "\n"

    f = open(fName, "w", encoding='utf-8')
    f.writelines(fileStr)
    f.close()

    print("Wrote to file for " + str(media.name))