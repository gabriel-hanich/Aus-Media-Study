import csv

def writeToFile(articles):
    mediaOutlet = articles[0].mediaOutlet
    writeFile = open("testData\\" + mediaOutlet[0] + ".csv", "a", newline='', encoding='utf-8')
    readFile = open("testData\\" + mediaOutlet[0] + ".csv", "r", newline='', encoding='utf-8')
    writer = csv.writer(writeFile)
    reader = csv.reader(readFile)

    pastHeadLines = []
    for line in reader:
        pastHeadLines.append(line[0])
    for article in articles:
        if article.headline not in pastHeadLines:
            row = [article.headline, article.description, article.author, article.publishDate]
            writer.writerow(row)
    
    writeFile.close()
    readFile.close()