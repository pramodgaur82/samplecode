#!/usr/bin/python
import sys
import logging
import os

activate_this = os.path.join("/home/romesh/meguk_dev/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/main/")
sys.path.insert(0,"/srv/http/main/")
sys.path.insert(0,"/meguk2017.com/main/")

from app import app as application
application.secret_key = '\xe0L\x05_\xd1uS\xec<,yn\x19\x97\xd5\xe8\xf9\x10\xd5&\xa6\xf1\xa0\xb8'
