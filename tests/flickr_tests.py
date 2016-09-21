import unittest

from service.flickr import Flickr


class TestCases(unittest.TestCase):

    def setUp(self):
        self.flickr_crawler = Flickr()
        
    
    def test_generate_photo_urls(self):
        response = self.flickr_crawler.make_request("https://www.flickr.com/search/?text=rome")
        response = next(response)
        self.assertEqual(25, len(self.flickr_crawler.generate_photo_urls(response)), "page returned 25 photos")

if __name__ == "__main__":
    unittest.main()

        