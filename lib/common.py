#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

import os
import codecs
import json
import glob

dirname = os.path.dirname(__file__)


def get_config():
    path = os.path.join(dirname, '../config/credentials.json')

    with codecs.open(path, encoding='UTF-8', mode='r') as cfile:
        content = cfile.read()
        config = json.loads(content)

        return config


def get_files():
    path = os.path.join(dirname, '../config/files.json')

    with codecs.open(path, encoding='UTF-8', mode='r') as cfile:
        content = cfile.read()
        files = json.loads(content)

        return files


def clear_working():
    files = glob.glob(os.path.join(dirname, '../working/*.txt'))

    for f in files:
        os.remove(f)

    return
