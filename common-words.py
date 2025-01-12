import psycopg2
import textcleaner as tc
from collections import defaultdict
from pprint import pprint
import time
import json

conn = psycopg2.connect(
    user="postgres", host="localhost", port="5432", database="postgres"
)

# Create a common words table, and truncate it.
ct = "create table if not exists common (word text, rowid bigint)"
with conn.cursor() as curs:
    curs.execute(ct)
    conn.commit()
    curs.execute("truncate table common")
    conn.commit()

q = "select content from searchable_content tablesample bernoulli(30) limit %s"

common = defaultdict(int)

with conn.cursor() as curs:
    curs.execute(q, [100])
    conn.commit()
    for row in curs:
        txt = row[0]
        cleaned = tc.main_cleaner(txt)
        for word in filter(lambda w: len(w) > 2, cleaned[0].split(" ")):
            common[word] += 1


ls = list(reversed(sorted(list(common.items()), key=lambda x: x[1])))
js = list(map(lambda p: p[0], ls[:100]))
print(js)

with open("common.json", "w") as f:
    json.dump(js, f)

with conn.cursor() as curs:
    for word in js:
        q = "select rowid from searchable_content, to_tsquery('english', %s) as query where fts @@ query"
        curs.execute(q, [word])
        conn.commit()
        all = curs.fetchall()
        print(word, len(all))
        for row in all[:1000]:
            i = "insert into common (rowid, word) values (%s, %s)"
            curs.execute(i, [row[0], word])
            conn.commit()
