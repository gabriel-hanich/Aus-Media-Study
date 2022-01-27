# Media analyser 

## By Gabriel Hanich

Media analyser scans 10 australian media sources twice a day to then record and analyse these sources.
These sources include 
1. [ABC News](https://www.abc.net.au/news/feed/51120/rss.xml)
2. [9 News](https://www.9news.com.au/rss)
3. [Syndey Morning Herald](https://www.smh.com.au/rss/feed.xml)
4. [The Australian](https://www.theaustralian.com.au/feed/) *Broken*
5. [SBS Australia](https://www.sbs.com.au/news/feed)
6. [Independent Australia](http://feeds.feedburner.com/IndependentAustralia)
7. [Daily Telegraph](https://www.dailytelegraph.com.au/feed)
8. [The Age](https://www.theage.com.au/rss/feed.xml)
9. [Michael West](https://www.michaelwest.com.au/feed/)
10. [The Guardian](https://www.theguardian.com/au/rss)

The pages are scanned at 6am and 6pm AEST, and then compiled into .csv files (1 Per outlet). These .csv files are added into a dateset, with each dataset getting a numebr as it's name. From there `converter.py` convertes the .csv files into JSON files, as well as computing the seniment score which is then analysed either using `analyser.py` or `notebooks/Analyser.ipynb`

The project is split into `Analysing` and `Scraping` where scraping is the server side code and analysing runs locally. 