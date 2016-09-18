from bs4 import BeautifulSoup

from base import Base
import settings


class Flickr(Base):
    
    def __init__(self):
        super(Flickr, self).__init__()