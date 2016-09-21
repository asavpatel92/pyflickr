from db.db import DB
from service.flickr import Flickr
import settings

def main():
    db_file = getattr(settings, 'DATABASE', 'pyflickr.db')
    db = DB(db_file)
    db.create_table()
    start_urls = [ 'https://www.flickr.com/search/?text=new%20york'
                , 'https://www.flickr.com/search/?text=paris'
                , 'https://www.flickr.com/search/?text=rome'
                  ]
    flickr_crawler = Flickr(urls=start_urls, callback=db.save_to_db)
    with flickr_crawler:
        flickr_crawler.crawl()

if __name__ == "__main__":
    main()
