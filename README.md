# scaling

We want to handle scale.

We want to keep our architecture simple.

This means our goal is S3 and Postgres. Adding OpenSearch adds 1) complexity and 2) cost. Doing so must be motivated by a clear demonstration that Postgres **cannot** handle our needs. Or, that using Postgres is substantially more costly than, say, standing up an OpenSearch cluster.

# data

We have been testing with a NASA crawl carried out by Jemison. We'll do some testing with other data that we can more easily standardize on.

The ClueWeb22 dataset requires licensing and a PCard purchase.

https://lemurproject.org/clueweb22/index.php

It looks like Common Crawl might be a place to start:

https://commoncrawl.org/

https://dzone.com/articles/need-billions-of-web-pages-dont-bother-crawling


# preparing the db

```
DATABASE_URL=postgresql://postgres@localhost:5432/postgres?sslmode=disable dbmate up
```

# fetching WET files

```
python wet-fetch.py <count> <offset>
```

Fetch one WET file:

```
python wet-fetch.py 1 0
```

Fetch 50, starting at file 60:

```
python wet-fetch.py 50 60
```

Each file yields ~10K plain text webpages.


This will

1. Download
2. Unzip
3. Load into the DB

# building a common word corpus

```
python -m nltk.downloader stopwords
python -m nltk.downloader wordnet
```

```
python common-words.py
```

this spits out `common.json`, which is a list of the 100 most common words in the corpus.

It also builds the table `common`, which lists all of the ROWIDs of content that contains those words.