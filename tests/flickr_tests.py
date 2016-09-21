import unittest

from service.flickr import Flickr

class TestCases(unittest.TestCase):

    def setUp(self):
        self.flickr_crawler = Flickr()
        
    
    def test_generate_photo_urls(self):
        response = self.flickr_crawler.make_request("https://www.flickr.com/search/?text=rome")
        response = next(response)
        self.assertEqual(25, len(self.flickr_crawler.generate_photo_urls(response)), "page returned 25 photos")
        
        response = self.flickr_crawler.make_request("https://www.google.com")
        response = next(response)
        self.assertEqual(0, len(self.flickr_crawler.generate_photo_urls(response)), "page returned 0 photos")
            
    def test_extract_photo_metadata(self):
        expected = {'username': u'guidobarberis', 'url': u'https://www.flickr.com/photos/guidobarberis/26844098895/'
                    , 'image_url': u'https://c2.staticflickr.com/8/7589/26844098895_b6e2ec79cd_b.jpg'
                    , 'description': u'View From Ellis Island Two', 'title': u'New York', 'latitude': 40.702797
                    , 'isPublic': True, 'id': u'26844098895', 'longitude':-74.01678}
        response = self.flickr_crawler.make_request("https://www.flickr.com/photos/guidobarberis/26844098895/")
        response = next(response)
        self.assertEquals(expected, self.flickr_crawler.extract_photo_metadata(response), "matches expacted metadata")

        response = self.flickr_crawler.make_request("https://www.google.com/")
        response = next(response)
        self.assertFalse(self.flickr_crawler.extract_photo_metadata(response), "no metadata found")

if __name__ == "__main__":
    unittest.main()
