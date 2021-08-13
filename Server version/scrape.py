import requests 
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

# Functions
def writeToFile(articles): # Writes the data to a csv file with the name of the media outlet
    mediaOutlet = articles[0].mediaOutlet
    writeFile = open("testData\\" + mediaOutlet[0] + ".csv", "a", newline='', encoding='utf-8') # Inits file
    readFile = open("testData\\" + mediaOutlet[0] + ".csv", "r", newline='', encoding='utf-8') # Reads data from file so same article isn't saved twice
    writer = csv.writer(writeFile)
    reader = csv.reader(readFile)

    pastHeadLines = []
    for line in reader:
        pastHeadLines.append(line[0]) # Get exisiting data 
    for article in articles:
        if article.headline not in pastHeadLines: # If this article is new, 
            row = [article.headline, article.description, article.author, article.publishDate]
            writer.writerow(row) # Write to file
    
    writeFile.close()
    readFile.close()

class article: # Article class containging all necessary information
    def __init__(self, headline, description, author, publishDate, mediaOutlet):
        super().__init__()
        self.headline = headline
        self.description = description
        self.author = author
        self.publishDate = publishDate
        self.mediaOutlet = mediaOutlet
    
    def toString(self):
        return self.headline + "\n" + self.description + "\n By " + self.author

def cleanText(text): # Function that cleans RSS data to remove unecessary characters
    if text == "</dc:creator>":
        text = "None found"
    if "<p>" in text:
        text = text[3:-2]
    if 'title="' in text:
        text = text[text.find('title="') + 25:-3]
    if '</div>' in text:
        text = text[text.find('</div>')+6:]
    if '&lt;' in text:
        text = text[:text.find("&lt;")] 
    if text == "<![CDATA[ ]]>":
        text = "None found"
    elif text[:9] == "<![CDATA[":
        text = text[9:-3]
    text.replace("</", "")
    text.replace('</', "")
    text.replace(">", "")
    return text

print("Compiled")

outlets = []

dataFile = open('Media Outlets.csv', 'r') # Get the links and headlines for each outlet
reader = csv.reader(dataFile)
for row in reader:
    outlets.append(row)

dataFile.close()
try:
    print("RUNNING ON " + str(datetime.now()))
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

    print("Done :)")

    goodFile = open("RunLog.txt", 'a', encoding='utf-8')
    goodFile.write(str(datetime.now()) + '\n')
    goodFile.close()

except Exception as e:
    print("AN ERROR OCCURED ON " + str(datetime.now()) + "\n" + e + "\n")
    print(e)
    errorFile = open("ERROR.txt", "a", encoding='utf-8')
    errorFile.write("\nAn error occured at " + str(datetime.now()) + " \n " + e + "\n")
    errorFile.close()

