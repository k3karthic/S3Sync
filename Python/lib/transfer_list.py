#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import s3sync_lib
import os
import codecs
import sys
import hashlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3ResponseError

config = s3sync_lib.get_config()
local_list_file = os.path.dirname(__file__) + '/../working/LocalList.txt'
s3_list_file = os.path.dirname(__file__) + '/../working/S3List.txt'
last_sync_file = os.path.dirname(__file__) + '/../working/LastSync.txt'
output_file = os.path.dirname(__file__) + '/../working/TransferList.txt'

s3_files = {}
local_files = {}
mtime_files = {}

s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
bucket = s3conn.get_bucket(config[u'bucket'])
last_sync = Key(bucket)

def convert_to_s3key(file_name,dir_name,alias):
    dir_pos = file_name.index(dir_name)
    key = file_name[dir_pos::]
    alias = alias.strip()

    if len(alias) > 0:
        key = key.replace(dir_name,alias)

    return key

def create_digest(key):
    m = hashlib.md5()
    m.update(key)

    return m.hexdigest()

try:
    last_sync.key = 'LastSync.txt'
    last_sync.get_contents_to_filename(last_sync_file)
except S3ResponseError as e:
    message = e.message

    if message == "The specified key does not exist.":
        open(last_sync_file, 'w').close()
    else:
        pass

# Clear output file
open(output_file, mode='w').close()

with codecs.open(s3_list_file,encoding='UTF-8',mode='r') as sfile:
    for line in sfile:
        line = line.strip()
        s3key, size = line.split('<>')

        s3key_hash = create_digest(s3key)

        s3_files[s3key_hash] = [s3key,size]

with codecs.open(local_list_file,encoding='UTF-8',mode='r') as lfile:
    for line in lfile:
        line = line.strip()
        line_list = line.split('<>')
        dir_name = line_list[0]
        file_name = line_list[1]
        alias = line_list[6]

        file_key = convert_to_s3key(file_name,dir_name,alias)
        file_key_hash = create_digest(file_key)

        local_files[file_key_hash] = line_list

with codecs.open(last_sync_file,encoding='UTF-8',mode='r') as sfile:
    for line in sfile:
        line = line.strip()
        key, mtime = line.split('<>')

        key_hash = create_digest(key)

        mtime_files[key_hash] = [key, mtime]

with codecs.open(output_file,encoding='UTF-8', mode='w') as ofile:
    for key in s3_files:
        if key in local_files:
            add_file = False
            s3key, s3size = s3_files[key]
            s3mtime = 0

            file_list = local_files[key]
            file_name = file_list[1]
            file_size = file_list[2]
            file_mtime = file_list[3]

            if key in mtime_files:
                s3mtime = mtime_files[key][1]
            else:
                s3mtime = file_mtime

            if s3size != file_size:
                add_file = True

            if s3mtime != file_mtime:
                add_file = True

            if add_file == True:
                ofile.write('<>'.join([
                            'ADD',
                            s3key,
                            file_name,
                            file_list[4],
                            file_list[5],
                            file_mtime
                            ]))

                ofile.write(os.linesep)

    for key in s3_files:
        if key not in local_files:
            s3key, size = s3_files[key]

            ofile.write('<>'.join([
                        'DELETE',
                        s3key,
                        ]))

            ofile.write(os.linesep)
