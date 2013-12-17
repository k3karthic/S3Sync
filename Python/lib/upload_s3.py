#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import s3sync_lib
import os
import codecs
import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key

config = s3sync_lib.get_config()
input_file = os.path.dirname(__file__) + '/../working/TransferList.txt'

s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
bucket = s3conn.get_bucket(config[u'bucket'])

with codecs.open(input_file,encoding='UTF-8',mode='r') as file:
    for line in file:
        line = line.strip()
        line_list = line.split('<>')

        action = line_list[0]
        s3key = line_list[1]

        k = Key(bucket)
        k.key = s3key

        if action == 'ADD':
            file_name = line_list[2]
            rrs = line_list[3]
            encrypt = line_list[4]
            mtime = line_list[5]

            if rrs == '1':
                rrs = True
            else:
                rrs = False

            if encrypt == '1':
                encrypt = True
            else:
                encrypt = False

            print('Uploading file %s...' % s3key)

            k.set_contents_from_filename(
                file_name,
                reduced_redundancy=rrs,
                encrypt_key=encrypt
                )

        if action == 'DELETE':
            print('Removing file %s...' % s3key)

            bucket.delete_key(k)
