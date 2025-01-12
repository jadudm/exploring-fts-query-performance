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
docker compose up
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

It also builds the table `common`, which lists all of the ROWIDs of content that contains those words. This is needed for the `t3()` SQL tests.

# running tests

In an interactive shell (DBeaver or similar), run the following. Assuming you have roughly the first 50-75 WET files from the common crawl downloaded, then the common words used in these queries below (as-is) should work. YMMV, and checking the `common.json` document and using terms from there might be a good idea.

```
create type query_timing as (query text, timing float);

drop function t1
CREATE OR REPLACE FUNCTION t1(qp text) RETURNS query_timing
AS $$
DECLARE total TEXT; 
	retval query_timing;
BEGIN
    EXPLAIN (ANALYZE, TIMING, FORMAT JSON) into total 
	select 
		domain64,
		path,
		ts_rank(fts, query, 1) AS rank
	from
		searchable_content,
		to_tsquery('english', qp) query
	where
		fts @@ query
	order by rank desc
	limit 10;
	select qp into retval.query;
	select ((total::jsonb)-> 0 -> 'Execution Time') into retval.timing;
	RETURN retval ;
END;
$$  LANGUAGE plpgsql;

select rowid from searchable_content, to_tsquery('english', 'record') as query where fts @@ query


-- These all come out at 2.3 seconds
select t1('moon & landing')
union all
select t1('apollo & moon & landing')
union all
select t1('apparent & apollo & moon & landing')
union all
select t1('(moon | moon:*) & (landing | land:*)')
union all
select t1('privacy')
union all 
select t1('privacy & page')
union all 
select t1('privacy & page & administrator')
union all 
select t1('privacy & page & administrator & information')
union all 
select t1('privacy & page & administrator & information & october')

-- This only works if you've run `python common-words.py` first.
drop function if exists t3;
CREATE OR REPLACE FUNCTION t3(qp text, common_word text) RETURNS query_timing
AS $$
DECLARE 
	total TEXT; 
	retval query_timing;
	subset_ids record;
BEGIN
	-- select rowid into subset_ids from common where word = common_word;

	if exists(select rowid from common where word = common_word)
	then
	    EXPLAIN (ANALYZE, TIMING, FORMAT JSON) into total
		select 
			domain64,
			path,
			ts_rank(fts, query, 1) AS rank
		from
			searchable_content,
			to_tsquery('english', qp) query
		where 
			rowid in (select rowid from common where word = common_word)
			and 
			fts @@ query
		order by rank desc
		limit 10;
		select qp into retval.query;
		select ((total::jsonb)-> 0 -> 'Execution Time') into retval.timing;
		RETURN retval;
	else
	    EXPLAIN (ANALYZE, TIMING, FORMAT JSON) into total
		select 
			domain64,
			path,
			ts_rank(fts, query, 1) AS rank
		from
			searchable_content,
			to_tsquery('english', qp) query
		where 
			fts @@ query
		order by rank desc
		limit 10;
		select qp into retval.query;
		select ((total::jsonb)-> 0 -> 'Execution Time') into retval.timing;
		RETURN retval;
	end if;
END;
$$  LANGUAGE plpgsql;


select t1('privacy')
union all 
select t1('privacy & page')
union all 
select t1('privacy & page & administrator')
union all 
select t1('privacy & page & administrator & information')
union all 
select t1('privacy & page & administrator & information & october')
union all
select t3('privacy', 'privacy')
union all 
select t3('privacy & page', 'privacy')
union all 
select t3('privacy & page & administrator', 'privacy')
union all 
select t3('privacy & page & administrator & information', 'privacy')
union all 
select t3('privacy & page & administrator & information & october', 'privacy')
union all
select t3('privacy', 'supercalifragilistic')
union all 
select t3('privacy & page', 'supercalifragilistic')
union all 
select t3('privacy & page & administrator', 'supercalifragilistic')
union all 
select t3('privacy & page & administrator & information', 'supercalifragilistic')
union all 
select t3('privacy & page & administrator & information & october', 'supercalifragilistic')
```