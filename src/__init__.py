# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-03-10"

import logging

# to avoid "No handler found" warnings
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
