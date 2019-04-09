# This file is licensed under MIT license.
# See the LICENSE file in the project root for more information.

# This is a helper to do more fancy logging
#
# Importing this file will automatically setup root logger:
# - logging to stdout
# - debug level
# - fancy colored format
#
# Use log_helper.getLogger() instead of logging.getLogger() to create new loggers

import logging
import sys

_max_name_length = 0
__registered_loggers = []


class FacnyFormatter(logging.Formatter):
    __levels = {
        logging.FATAL:  '\033[31m[FATAL]',
        logging.ERROR:  '\033[31m[ERROR]',
        logging.WARN:   '\033[33m[WARN] ',
        logging.INFO:   '\033[32m[INFO] ',
        logging.DEBUG:  '\033[36m[DEBUG]',
        logging.NOTSET: '       ',
    }

    def format(self, record):
        if record.name == 'root':
            return '{}   {}   {}'.format(FacnyFormatter.__levels[record.levelno], str.ljust(' ', _max_name_length), record.msg + '\033[0m')
        else:
            return '{}  [{}]  {}'.format(FacnyFormatter.__levels[record.levelno], str.ljust(record.name, _max_name_length), record.msg + '\033[0m')


def setupLogger(logger):
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FacnyFormatter())
    logger.handlers = [handler]
    logger.propagate = False


def getLogger(name):
    global _max_name_length
    logger = logging.getLogger(name)
    if logger not in __registered_loggers:
        _max_name_length = max(_max_name_length, len(name))
        setupLogger(logger)
        __registered_loggers.append(logger)
    return logger


def setLevel(logger, level):
    logger = logging.getLogger(logger)
    print(logger.name)
    print(logger.handlers)
    logger.handlers[0].setLevel(level)


# Setup root logger
setupLogger(logging.getLogger())
