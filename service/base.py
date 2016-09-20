import grequests

from utils.log import Log


class Base(object):
    
    def __init__(self):
        self.logger = Log().logger
    
    """
    Exception handling logic goes here
    """
    def exception_handler(self, request, exception):
        self.logger.error("Exception occured while processing request | request : %s, exception : %s", request, exception)    


    """
    Sends concurrent requests to the list of urls passed
        @param urls: list
    Returns:
        generator: returns a generator of responses.
    """
    def make_request(self, url):
        # Create a set of unsent Requests
        rs = (grequests.get(u) for u in [url])
        # Send them all at the same time
        return grequests.imap(rs, exception_handler=self.exception_handler)
