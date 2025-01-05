#! /usr/bin/python3

import logging
import sys
import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/dev/Ultimate-Converter/src')
from app import app as application
application.secret_key = 'supersecretkey'