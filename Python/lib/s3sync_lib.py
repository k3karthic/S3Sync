#!/usr/bin/env python

import os
import codecs
import json

def get_config():
    path = os.path.dirname(__file__) + '/../../config/credentials.json'

    content = ''
    with codecs.open(path,encoding='UTF-8',mode='r') as cfile:
        content = cfile.read()

    config = json.loads(content)

    return config

def get_files():
    path = os.path.dirname(__file__) + '/../../config/files.json'

    content = ''
    with codecs.open(path,encoding='UTF-8',mode='r') as cfile:
        content = cfile.read()

    files = json.loads(content)

    return files
