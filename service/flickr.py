import json
import re

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from base import Base
import settings

class Flickr(Base):
    
    WORKER_THREADS = settings.WORKER_THREADS
    PHOTO_URL = "https://www.flickr.com/photos/{username}/{photo_id}"
    
    def __init__(self, urls=[], callback=None):
        super(Flickr, self).__init__()
        self.urls = urls
        self.worker_pool = ThreadPoolExecutor(max_workers=Flickr.WORKER_THREADS)
        self.metadata = []
        self.callback = callback
    
    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, traceback):
        """
            to clear up thread pool resources correctly
        """
        self.logger.info("waiting for all threads to complete.")
        self.worker_pool.shutdown(wait=True)
        self.logger.info("execution finished.")
        return True

    
    def add_to_worker_queue(self, task, callback, **kwargs):
        """
            adds a task to the thread pool and hooks a callback to the future object
        """        
        self.logger.info("Adding task '%s' to worker pool.", task.func_name)
        self.worker_pool.submit(task, **kwargs).add_done_callback(callback)
        return
    
    def crawl(self):
        for url in self.urls:
            self.load_url(url, callback=self.handle_response)
        return None
    
    def load_url(self, url, callback=None):
        """
            makes an http request to the passed url and an optional callback to process the response object
        """        
        response = self.make_request(url=url)
        response = next(response)
        # response is a generator, so to get the data out of it need to iterate through it.
        if not callback: return response
        callback(response)
                
    def handle_response(self, response):
        photo_urls = self.generate_photo_urls(response)
        for url in photo_urls:
            # now adding each url to thread pool
            self.add_to_worker_queue(task=self.load_url
                                     , callback=self.extract_photo_metadata
                                     , url=url)
        return None

    def generate_photo_urls(self, response):
        """
            @param response: http response object
        Returns:
            list: returns a list of individual photo urls from the main page
        """
        urls = []
        script_data = self.__extract_script_data(response.text, "modelExport")
        if script_data:
            for photo  in script_data.get("search-photos-lite-models")[0].get("photos").get("_data"):
                urls.append(Flickr.PHOTO_URL.format(username=photo.get("pathAlias"), photo_id=photo.get("id")))
        return urls
    
    def extract_photo_metadata(self, response):
        """
            @param future: a future object
        Returns:
            dict : dictionary containing photo metadata
        """
        try:
            # response is a future object when function is passed in the callback
            response = response.result()
        except AttributeError:
            pass
        script_data = self.__extract_script_data(response.text, "modelExport")
        geo_info = script_data.get("photo-geo-models")[0]
        image_info = script_data.get("photo-head-meta-models")[0]
        owner_info = script_data.get("photo-models")[0].get("owner")
        
        photo_meta = {"id" : image_info.get("id")
                      , "username" : owner_info.get("pathAlias")
                      , "image_url" : image_info.get("og:image")
                      , "latitude" : geo_info.get("latitude")
                      , "longitude" : geo_info.get("longitude")
                      , "isPublic" : geo_info.get("isPublic")
                      , "url" : image_info.get("og:url")
                      , "title" : image_info.get("title")
                      , "description" : image_info.get("og:description")}
        if self.callback:
            self.logger.info("sending data back to main thread.")
            self.callback(photo_meta)
        return photo_meta

    def __extract_script_data(self, html_res, tag_id):
        """
            extracts javascript from html text for a script tag 
        """
        soup = BeautifulSoup(html_res, "html.parser")
        script_data = soup.find('script', tag_id).text
        script_data = re.search('%s:(.*)%s' % (tag_id, ","), script_data).group(1)
        if not script_data:
            self.logger.error("could not extract photos data from javascript!")
        try:
            script_data = json.loads(script_data)
        except ValueError, e:
            self.logger.error("could not convert data to JSON. exception : %s", e)
        return script_data
