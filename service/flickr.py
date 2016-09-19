import json
import re

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

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
        self.logger.info("Adding task %s to worker pool.", task.func_name)
        future = self.worker_pool.submit(task, **kwargs)
        future.add_done_callback(callback)
        self.fs.append(future)
        return

    def crawl(self):
        for url in self.urls:
            self.add_to_worker_queue(self.load_url, self.handle_response, url=[url])
        return
    
    def stop(self):
        self.worker_pool.shutdown(wait=True)
        return
    
    def load_url(self, url):
        response = self.make_requests(urls=url)
        # response is a generator, so to get the data out of it need to iterate through it.
        for res in response:
            return res
    
    def handle_response(self, response):
        photo_urls = self.generate_photo_urls(response)
        for urls in photo_urls.values():
            # now using a thread per username to make concurrent requests to fetch photos data
            self.add_to_worker_queue(self.extract_photo_metadata, self.save_photo_metadata, urls=urls)
        return    

    """
    Sends concurrent requests to the list of urls passed
        @param data: http response object
    Returns:
        dict: returns a dictionary which contains photo urls grouped by username --> {"username" : [urls] }
    """
    def generate_photo_urls(self, future):
        response = future.result()
        urls = {}
        script_data = self.__extract_script_data(response.text)
        if script_data:
            for photo  in script_data.get("search-photos-lite-models")[0].get("photos").get("_data"):
                urls.setdefault(photo.get("pathAlias"), []).append(Flickr.PHOTO_URL.format(username=photo.get("pathAlias")
                                                                                           , photo_id=photo.get("id")))
        return urls
    
    def extract_photo_metadata(self, urls):
        metadata = []
        response = self.make_requests(urls)
        for res in response:
            script_data = self.__extract_script_data(res.text)
            geo_info = script_data.get("photo-geo-models")[0]
            image_info = script_data.get("photo-head-meta-models")[0]
            metadata.append({"id" : image_info.get("id")
                             , "url" : image_info.get("og:image")
                             , "latitude" : geo_info.get("latitude")
                             , "longitude" : geo_info.get("longitude")
                             , "isPublic" : geo_info.get("isPublic")})
        return metadata
            
            
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
