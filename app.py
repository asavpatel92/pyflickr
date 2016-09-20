import sqlite3

from service.flickr import Flickr
import settings


def create_table(conn, db):
    with open("db/DDL.sql", "r") as ddl:
        conn.execute(ddl.read())
    return

def __ensure_connected(db):
    return sqlite3.connect(db)

def save_to_db(data):
    db = getattr(settings, 'DATABASE', 'pyflickr.db')
    conn = __ensure_connected(db)
    cursor = conn.cursor()
    create_table(conn, db)
    for metadata in data:
        query = "REPLACE INTO pyflickr (%s) values (%s)" % (', '.join(metadata.keys()), ', '.join('?' * len(metadata)))
        cursor.execute(query, metadata.values())
    conn.commit()
    conn.close()

def main():
    start_urls = [ 'https://www.flickr.com/search/?text=new%20york'
                , 'https://www.flickr.com/search/?text=paris'
                , 'https://www.flickr.com/search/?text=rome'
                  ]
    flickr_crawler = Flickr(urls=start_urls, callback=save_to_db)
    with flickr_crawler:
        flickr_crawler.crawl()

if __name__ == "__main__":
    main()
