import logging
from logging import handlers

import settings

class Log(object):
    # setting up logger information.
    def __init__(self):
        log_info = settings.log
        self.__logger = self.prepare_logger(log_info.get("file")
                                          , log_info.get("level", logging.DEBUG)
                                          , log_info.get('max_size', 10000000)
                                          , log_info.get('backup_count', 10))

    def prepare_logger(self, name, level, max_size, backup_count):
        logFormatter = self.MyFormatter()
        handler = handlers.RotatingFileHandler(filename=name
                                              , maxBytes=max_size
                                              , backupCount=backup_count)
        handler.setFormatter(logFormatter)
        logger = logging.getLogger("crawler")
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    @property
    def logger(self):
        return self.__logger

    # Inner class for formating the log
    class MyFormatter(logging.Formatter):
        width = 24
        datefmt = '%Y-%m-%d %H:%M:%S'

        def format(self, record):
            cpath = '%s:%s:%s' % (record.module, record.funcName, record.lineno)
            cpath = cpath[-self.width:].ljust(self.width)
            record.message = record.getMessage()
            s = "%-7s | %s | %s | %s" % (record.levelname, self.formatTime(record, self.datefmt), cpath, record.getMessage())
            if record.exc_info:
                # Cache the traceback text to avoid converting it multiple times
                # (it's constant anyway)
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                if s[-1:] != "\n":
                    s = s + "\n"
                s = s + record.exc_text
            return s
