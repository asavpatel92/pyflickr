import json
import re

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from base import Base
import settings

class Flickr(Base):
    
    WORKER_THREADS = settings.WORKER_THREADS
    PHOTO_URL = "https://www.flickr.com/photos/{username}/{photo_id}"
    
    def __init__(self, urls, callback):
        super(Flickr, self).__init__()
        self.urls = urls
        self.worker_pool = ThreadPoolExecutor(max_workers=Flickr.WORKER_THREADS)
        self.metadata = []
        self.callback = callback
    
    def __enter__(self):
        return self
         
    def __exit__(self, exception_type, exception_value, traceback):
        self.worker_pool.shutdown(wait=True)
        self.callback(self.metadata)
        return True

    
    def add_to_worker_queue(self, task, callback, **kwargs):
        self.logger.info("Adding task %s to worker pool.", task.func_name)
        self.worker_pool.submit(task, **kwargs).add_done_callback(callback)
        return

    def crawl(self):
        for url in self.urls:
            self.load_url(url, callback=self.handle_response)
        return
    
    def load_url(self, url, callback=None):
        response = self.make_request(url=url)
        # response is a generator, so to get the data out of it need to iterate through it.
        for res in response:
            if not callback: return res
            callback(res)
                
    def handle_response(self, response):
        photo_urls = self.generate_photo_urls(response)
        for url in photo_urls:
            # now using a thread per url to make concurrent requests to fetch photos data
            self.add_to_worker_queue(task=self.load_url
                                     , callback=self.extract_photo_metadata
                                     , url=url)
        return    

    """
        @param data: http response object
    Returns:
        list: returns a list of individual photo urls from the main page
    """
    def generate_photo_urls(self, response):
        urls = []
        script_data = self.__extract_script_data(response.text)
        if script_data:
            for photo  in script_data.get("search-photos-lite-models")[0].get("photos").get("_data"):
                urls.append(Flickr.PHOTO_URL.format(username=photo.get("pathAlias"), photo_id=photo.get("id")))
        return urls
    
    def extract_photo_metadata(self, future):
        response = future.result()
        script_data = self.__extract_script_data(response.text)
        geo_info = script_data.get("photo-geo-models")[0]
        image_info = script_data.get("photo-head-meta-models")[0]
        self.metadata.append({"id" : image_info.get("id")
                         , "image_url" : image_info.get("og:image")
                         , "latitude" : geo_info.get("latitude")
                         , "longitude" : geo_info.get("longitude")
                         , "isPublic" : geo_info.get("isPublic")
                         , "url" : image_info.get("og:url")
                         , "title" : image_info.get("title")
                         , "description" : image_info.get("og:description")})
        return
            
            
    def save_photo_metadata(self, future):
        metadata = future.result()
        self.logger.debug(metadata)

    def __extract_script_data(self, html_res):
        soup = BeautifulSoup(html_res, "html.parser")
        script_data = soup.find('script', 'modelExport').text
        script_data = re.search('%s(.*)%s' % ("modelExport:", ","), script_data).group(1)
        if not script_data:
            self.logger.error("could not extract photos data from javascript!")
        try:
            script_data = json.loads(script_data)
        except ValueError, e:
            self.logger.error("could not convert data to JSON. exception : %s", e)
        return script_data
