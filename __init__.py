#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

__version__ = "0.5.3.1"
__author__ = "np1"
__license__ = "LGPLv3"

# External api
from pafy import new
from pafy import get_categoryname
from pafy import backend
from playlist import get_playlist, get_playlist2