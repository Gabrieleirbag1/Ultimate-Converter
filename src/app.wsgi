#! /usr/bin/python3

import logging
import sys
import os
logging.basicConfig(stream=sys.stderr)

activate_this = '/home/dev/.local/share/virtualenvs/Ultimate-Converter-jge_3DdZ/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '/home/dev/Ultimate-Converter/src')
from app import app as application
from app import main

main()
application.secret_key = os.urandom(24)