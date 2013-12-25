#!/usr/bin/env python

import os
import codecs
import json
import glob
import hashlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3ResponseError

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

def get_last_sync(config):
    s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
    bucket = s3conn.get_bucket(config[u'bucket'])
    file_name = os.path.dirname(__file__) + '/../working/LastSync.txt'
    k = Key(bucket)

    try:
        k.key = 'LastSync.txt'
        k.get_contents_to_filename(file_name)
    except S3ResponseError as e:
        message = e.message
    
        if message == "The specified key does not exist.":
            open(file_name, 'w').close()
        else:
            raise e

    return

def save_last_sync(config):
    s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
    bucket = s3conn.get_bucket(config[u'bucket'])
    sync_file = os.path.dirname(__file__) + '/../working/LastSync.txt'
    local_file = os.path.dirname(__file__) + '/../working/LocalList.txt'
    k = Key(bucket)

    file = open(sync_file,mode='w')
    with codecs.open(local_file,encoding='UTF-8',mode='r') as sfile:
        for line in sfile:
            line_list = line.split('<>')
            dir_name = line_list[0]
            file_name = line_list[1]
            file_mtime = line_list[3]
            alias = line_list[6]
            file_key = convert_to_s3key(file_name,dir_name,alias)

            file.write('<>'.join([file_key,file_mtime]))

            file.write(os.linesep)

    file.close()

    k.key = 'LastSync.txt'
    k.set_contents_from_filename(
        sync_file,
        reduced_redundancy=config[u'rrs'],
        encrypt_key=config[u'encrypt']
        )

    return

def clear_working():
    files = glob.glob(os.path.dirname(__file__) + '/../working/*.txt')

    for f in files:
        os.remove(f)

    return
