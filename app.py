from service.flickr import Flickr

if __name__ == "__main__":
    start_urls = [
        'https://www.flickr.com/search/?text=paris',
        'https://www.flickr.com/search/?text=rome',
        'https://www.flickr.com/search/?text=new%20york',
    ]
    flickr_crawler = Flickr()