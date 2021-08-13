import praw
from psaw import PushshiftAPI
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import time
from collections import Counter




def getPosts(searchWord, searchCount, stopWords):  # Get the posts from reddit
    wordList = []
    # Authenticate with reddit API and create reddit object
    reddit = praw.Reddit(
        client_id="GRD68owJs221Qw",
        client_secret="K1ug6GHtgHiKxkcHBpiO3ei7yRtDWQ",
        user_agent="Gabriel",
    )
    all = reddit.subreddit("all")  # Create subreddit object

    for post in all.search(
        searchWord, limit=searchCount
    ):  # Search for the top (seachCount) posts about (searchWord)
        title = word_tokenize(post.title)
        for word in title:  # Clean data [WIP]
            word = word.lower()
            if not word in stopWords:
                if word.isalpha():
                    wordList.append(word)
    return Counter(wordList)


if __name__ == "__main__":
    avgTime = 0
    for i in range(5):
        sTime = time.time()
        stopWords = set(stopwords.words("english"))
        print(Counter(getPosts("Doge", 100, stopWords)))
        avgTime += time.time() - sTime
    print(avgTime / 5)
