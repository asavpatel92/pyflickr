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
    
    
    def add_to_worker_queue(self, task, callback, **kwargs):
        # using with statement to ensure threads are cleaned up promptly
        with self.worker_pool as executor:
            running_tasks = {executor.submit(task, **kwargs)}
        
        for future in concurrent.futures.as_completed(running_tasks):
            try:
                result = future.result()
            except Exception as exc:
                    self.logger.error('URL : %r, generated an exception: %s' , running_tasks.get(future), exc)
            else:
                callback(result)

    def crawl(self):
        for url in self.urls:
            self.add_to_worker_queue(self.load_url, self.generate_photo_urls, url=[url])    
    
    def load_url(self, url):
        response = self.make_requests(urls=url)
        # response is a generator, so to get the data out of it need to iterate through it.
        for res in response:
            return res
    
    """
    Sends concurrent requests to the list of urls passed
        @param data: http response object
    Returns:
        dict: returns a dictionary which contains photo urls grouped by username --> {"username" : [urls] }
    """
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
    
    def extract_photo_data(self,):    
        pass
