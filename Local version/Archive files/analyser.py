import matplotlib.pyplot as plt
from lib.article import article, outlet, dayPeriod
from lib.reddit import getPosts
from nltk.corpus import stopwords
from nltk import word_tokenize
from datetime import timedelta, datetime
import time
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv  # Imports

backupDate = "29.07.21"
searchWord = ""


def getData(file):  # Function that reads data from a csv and returns as a list of  lists (columns and rows)
    csvFile = open(file, "r", encoding="utf-8")
    csvReader = csv.reader(csvFile, delimiter=",")
    data = []
    for row in csvReader:
        data.append(row)
    return data


# Constants
plt.style.use("dark_background")
analyser = SentimentIntensityAnalyzer()
stopwords = set(stopwords.words("english"))
commonWordsCount = 1 
doSimilar = False
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


media = outletList[0]
for media in outletList:
    print("\n" + media.name + "\n")
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
        possibleDates.append(day)  # Get list with every date between the 1st and last day an article was published by this outlet

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
            if word not in stopwords:  # If the word is important
                if (len(word) > 2):  # And more then 2 letters (removes punctuation and other smaller words)
                    cleanHeadlines.append(word)
        cleanHeadlines = list(Counter(cleanHeadlines).most_common(commonWordsCount))  # Get the most comon words for this day period

        if articleCount == 0:
            avgSentiment = 0
            cleanHeadlines = [["", 0]]

        else:
            avgSentiment = float(totalSentiment / articleCount)

        media.addDays(dayPeriod(thisdate, articleCount, cleanHeadlines, avgSentiment))  # add this day to the mesia's 'dayList'


    wordsList = []
    rotations = 0
    sTime = time.time()
    for index, item in enumerate(media.getDays()):
        for i in range(commonWordsCount):
            if item.commonWord[i][0] not in wordsList:
                wordsList.append(item.commonWord[i][0]) 
                commons = getPosts(item.commonWord[i][0], 50, stopwords)
                possibleLinks = []
                keys = list(commons.keys())
                values = list(commons.values())
                for a, b in enumerate(keys):
                    possibleLinks.append((b, values[a]))
                item.setRelatedWords(possibleLinks)
            else:
                sameIndex = wordsList.index(item.commonWord[i][0])
                item.setRelatedWords(media.getDays()[sameIndex].relatedWords)
            rotations += 1
            print(rotations / (int(daysCount.days) * commonWordsCount))

    for item in media.getDays():
        print("\n" + str(item.date) + "\n")
        print(item.relatedWords)

    sentimentScore = []
    emptyList = []
    articles = []
    fig, ax = plt.subplots(3)
    # Plot things
    for index, item in enumerate(media.getDays()):
        sentimentScore.append(item.avgSentiment)
        emptyList.append(0)
        articles.append(item.freq)
        pastFreq = 0
        overlapCount = 0
        for i in range(commonWordsCount):
            try:
                ax[2].scatter(item.date, item.commonWord[i][1])
                if pastFreq == item.commonWord[i][1]:
                    overlapCount += 0.5
                    ax[2].annotate(item.commonWord[i][0], [item.date, float(item.commonWord[i][1] + overlapCount)])
                else:
                    ax[2].annotate(item.commonWord[i][0], [item.date, item.commonWord[i][1]])
                pastFreq = item.commonWord[i][1]
            except IndexError:
                pass

    ax[0].plot(possibleDates, sentimentScore, label="Sentiment")
    ax[0].plot(possibleDates, emptyList, label="Neutral")
    if searchWord == "":
        ax[0].set_title(media.name)
    else:
        ax[0].set_title(media.name + " reporting mentioning keyword '" + searchWord + "'")
    ax[0].set_ylim([-1, 1])
    ax[0].legend()

    ax[1].plot(possibleDates, articles)

    plt.show()
