import logging

WORKER_THREADS = 80

log = { "file": "../crawler.log"
       , "level": logging.DEBUG
       , "max_size": 10000000
       , "backup_count": 10
   }


DATABASE = "db/pyflickr.db"