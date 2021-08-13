import requests 
from bs4 import BeautifulSoup
from article import article, cleanText
from writeToFile import writeToFile
import csv

outlets = []

dataFile = open('Media Outlets.csv', 'r')
reader = csv.reader(dataFile)
for row in reader:
    outlets.append(row)

dataFile.close()

outLetList = []


for mediaOutlet in outlets:
    print("Scanning " + mediaOutlet[0])

    url = mediaOutlet[1]

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    data = soup.prettify().split("\n")

    articleList = []
    emptyarticles = 0


    for index, line in enumerate(data):
        attributesFound = 0
        if line.strip() == "<title>":
            headline = cleanText(data[index + 1].strip())
        if line.strip() == "<description>":
            desc = data[index + 1]
            desc = cleanText(desc[13:-3])
        if line.strip() == "<dc:creator>" or line.strip() == "<author>":
            author = cleanText(data[index + 1].strip())
        if "<pubdate>" in line:
            publishDate = cleanText(data[index + 1]).strip()
        if line.strip() == "</item>":
            try:
                articleList.append(article(headline, desc, author, publishDate, mediaOutlet))
            except NameError as e:
                print(e)
    
    writeToFile(articleList)
    outLetList.append(articleList[2])

print("Done :)")