# pyflickr
simple web-crawler for flickr to download images with geo locations based on search

### Installation

```
pip install -r requirements.txt
```

## Usage:

```python
start_urls = [ 'https://www.flickr.com/search/?text=new%20york' ]
flickr_crawler = Flickr(urls=start_urls, callback=None)
with flickr_crawler:
    flickr_crawler.crawl()
```

You can also provide a callback function when creating a crawler object.
crawler will send the data to the callback function as soon as crawled data is available.

```python
def on_data_available(data):
    """ 
    perform operations on available data
    """
    pass

start_urls = [ 'https://www.flickr.com/search/?text=new%20york']
flickr_crawler = Flickr(urls=start_urls, callback=on_data_available)
with flickr_crawler:
    flickr_crawler.crawl()
```

### Settings
modify ```settings.py``` to configure the application

### Sample Application

a sample application is provided which shows the usage of the library. which also passes a callback function to the crawler which saves the crawled data in the sqlite database.

table structure is defined in ```db/DDL.sql``` and other database specific settings can be found in ```settings.py```

you can run the application by running following command

```
python app.py
```

