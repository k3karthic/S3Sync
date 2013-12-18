#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import s3sync_lib
import os
import codecs
import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key

config = s3sync_lib.get_config()
output_file = os.path.dirname(__file__) + '/../working/S3List.txt'

s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
bucket = s3conn.get_bucket(config[u'bucket'])

# Clear file
open(output_file, 'w').close()

with codecs.open(output_file,encoding='UTF-8',mode='a') as lfile:
    previous_folder = ''

    for key in bucket.list():
        if key.size == 0:
            continue

        name = key.name
        folder = name[0:name.index('/')]

        if folder != previous_folder:
            print('Listing files in %s...' % folder)

        lfile.write('<>'.join([
                    name,
                    str(key.size)
                    ]))

        lfile.write(os.linesep)

        previous_folder = folder
