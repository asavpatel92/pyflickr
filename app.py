from service.flickr import Flickr

if __name__ == "__main__":
    start_urls = [ 'https://www.flickr.com/search/?text=new%20york'
                , 'https://www.flickr.com/search/?text=paris'
                , 'https://www.flickr.com/search/?text=rome'
                  ]
    flickr_crawler = Flickr(urls=start_urls)
    with flickr_crawler:
        flickr_crawler.crawl()
