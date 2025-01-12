import click
import requests
import gzip
import shutil
from enum import Enum
import re
from pathlib import Path
import psycopg2
import os

BASE_URL = "https://data.commoncrawl.org"
PATH_PAT = "crawl-data/CC-MAIN-2024-51/segments/1733066035857.0/wet/CC-MAIN-20241201162023-20241201192023-%05d.warc.wet.gz"

COMPRESSED_PAT = "data/%05d.warc.wet.gz"
UNCOMPRESSED_PAT = "data/%05d.warc.wet"

conn = psycopg2.connect(
    user="postgres", host="localhost", port="5432", database="postgres"
)
cursor = conn.cursor()


def fetch_gzip(n):
    uncomp = Path(UNCOMPRESSED_PAT % n)
    comp = Path(COMPRESSED_PAT % n)
    if comp.is_file() or uncomp.is_file():
        print(COMPRESSED_PAT % n, "already downloaded")
    else:
        r = requests.get(BASE_URL + "/" + PATH_PAT % n)
        open(COMPRESSED_PAT % n, "wb").write(r.content)
        print(COMPRESSED_PAT % n, " downloaded")


def ungzip(n):
    uncomp = Path(UNCOMPRESSED_PAT % n)
    if uncomp.is_file():
        print(UNCOMPRESSED_PAT % n, "already expanded")
    else:
        with gzip.open(COMPRESSED_PAT % n, "rb") as f_in:
            with open(UNCOMPRESSED_PAT % n, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(UNCOMPRESSED_PAT % n, " downloaded")


# This is a state machine.
# Start of record:
# WARC/1.0
# Then watch for the language
# WARC-Identified-Content-Language: eng
# Then the content length
# Content-Length: 4600
# Which means we have that much content to read, or until the next WARC/1.0.


class State(Enum):
    START = 0
    LANG = 1
    CONTENT = 2
    READ = 3


records = 0


def load_wet(n):
    global records
    current_state = State.START
    lines = []
    with open(UNCOMPRESSED_PAT % n) as stream:
        for line in stream:
            line = line.strip()
            if current_state == State.START:
                if line == "WARC/1.0":
                    current_state = State.LANG
            elif current_state == State.LANG:
                if ("WARC" in line) and ("Language" in line):
                    if re.search(": eng$", line):
                        current_state = State.CONTENT
                    else:
                        current_state = State.START
            elif current_state == State.CONTENT:
                if re.match("Content-Length: ([0-9]+)", line):
                    current_state = State.READ
            elif current_state == State.READ:
                if line == "WARC/1.0":
                    # print(f"flushing {len(lines)} lines")
                    txt = " ".join(lines)
                    txt.replace("\x00", "\uFFFD")
                    cursor.execute(
                        "INSERT INTO searchable_content (domain64, path, content) values(%s, %s, %s)",
                        [0, "/path", txt[:500000]],
                    )
                    conn.commit()
                    lines = []
                    records += 1
                    if records % 1000 == 0:
                        print(f"{records} loaded")
                    current_state = State.LANG
                else:
                    lines.append(line)


@click.command()
@click.argument("number_of_files", type=int)
@click.argument("offset", type=int)
def wet_fetch(number_of_files, offset=0):
    for i in range(number_of_files):
        fetch_gzip(i + offset)
        ungzip(i + offset)
        load_wet(i + offset)


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    wet_fetch()
