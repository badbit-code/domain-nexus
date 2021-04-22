#! /usr/local/bin/python3.9

from pathlib import Path
from contextlib import closing
import sqlite3
from ftplib import FTP
from tempfile import TemporaryFile
from zipfile import ZipFile
from io import BytesIO
from json import loads

Path("db").mkdir(exist_ok=True)

db_path = "db/__godaddy_db.db"

limiter = None  # set this to None for writing all rows to db

create_query = """create table if not exists godaddy_details
(domain_name text primary key, available timestamp, domain_length text,
wiki integer default 0, alexa integer DEFAULT -999,
archive_count integer default 0,
com integer default 0, net integer default 0,
org integer default 0, io integer default 0,
edu integer default 0, gov integer default 0,
site integer default 0, biz integer default 0,
brandable integer default 0,
creation_date timestamp NULL,
date_added timestamp default CURRENT_DATE)"""


def download_and_extract(file_name):
    print(f"Downloading {file_name}")
    with BytesIO() as tempfile:
        ftp.retrbinary(f"RETR {file_name}", tempfile.write)
        with ZipFile(tempfile) as zip_:
            file_to_extract = file_name.rsplit(".", 1)[0]
            with zip_.open(file_to_extract) as json_contents:
                file_to_extract = file_name.rsplit(".", 1)[0]
                add_to_db(file_to_extract, json_contents.read().decode("utf-8"))


def add_to_db(file_name, json_contents):
    print(f"Adding {file_name}")
    keys_needed = {"domainName", "auctionEndTime"}
    data = [
        [
            v if k != "auctionEndTime" else v.replace("Z", "")
            for k, v in x.items()
            if k in keys_needed
        ]
        for x in loads(json_contents)["data"]
    ][:limiter]
    with sqlite3.connect(
        db_path, detect_types=sqlite3.PARSE_DECLTYPES
    ) as conn, closing(conn.cursor()) as cur:
        cur.execute(create_query)
        cur.executemany(
            f"insert or ignore into godaddy_details (domain_name, available, domain_length) values (?,?,?)",
            (i + [len(i[0].split(".")[0])] for i in data),
        )

    conn.close()


with FTP("ftp.godaddy.com", "auctions") as ftp:
    files_needed = (
        x
        for x in ftp.nlst()
        if x.startswith("all_listings") and not x.startswith("all_listings_")
    )
    for file in files_needed:
        download_and_extract(file)
