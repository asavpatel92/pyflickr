import json
import re

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

from base import Base
import settings

class Flickr(Base):
    
    WORKER_THREADS = settings.WORKER_THREADS
    PHOTO_URL = "https://www.flickr.com/photos/{username}/{photo_id}"
    
    def __init__(self, urls):
        super(Flickr, self).__init__()
        self.urls = urls
        self.worker_pool = ThreadPoolExecutor(max_workers=Flickr.WORKER_THREADS)
        
    
    def load_url(self, url):
        response = self.make_requests(urls=url)
        # response is a generator, so to get the data out of it need to iterate through it.
        for res in response:
            return res
    
    def generate_photo_urls(self, data):
        urls = {}
        soup = BeautifulSoup(data.text, "html.parser")
        script_data = soup.find('script', 'modelExport').text
        script_data = re.search('%s(.*)%s' % ("modelExport:", ","), script_data).group(1)
        if not script_data:
            self.logger.error("could not extract photos data from javascript!")
            return urls
        try:

            test = json.loads(script_data)
            for photo  in test.get("search-photos-lite-models")[0].get("photos").get("_data"):
                urls.setdefault(photo.get("pathAlias"), []).append(Flickr.PHOTO_URL.format(username=photo.get("pathAlias")
                                                                                           , photo_id=photo.get("id")))
            return urls
        except ValueError, e:
            self.logger.error("could not convert data to JSON. exception : %s", e)
            return urls
    
    def crawl(self):
        with self.worker_pool as executor:
            running_tasks = {executor.submit(self.load_url, [url]): url for url in self.urls}
            print (running_tasks)
            for future in concurrent.futures.as_completed(running_tasks):
                try:
                    data = future.result()
                except Exception as exc:
                    self.logger.error('URL : %r, generated an exception: %s' , running_tasks.get(future), exc)
                else:
                    photo_urls = self.generate_photo_urls(data)
