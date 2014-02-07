#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys
import codecs
import sys
import subprocess
import json
import glob
import hashlib
import optparse
import time

from lib import common

import botocore.session
import botocore.paginate

BUFFSIZE = 1024 * 8
dirname = os.path.dirname(__file__)

##
## Classes
##

class ProxyFP:
    def __init__(self,filename):
        self.filename = filename
        self.size = os.path.getsize(filename)
        self.curr_size = 0
        self.fp = open(filename,'rb')
        self.start = True
        self.percent = 0
        self.np = 20

    def __len__(self):
        return self.size

    def seek(self,pos):
        self.fp.seek(pos)

    def read(self,size):
        if self.start == True:
            print('      Progress:    ',end="")
            sys.stdout.flush()
            self.start = False

        content = self.fp.read(size)
        size = len(content)
        self.curr_size = self.curr_size + size
        percent = self.curr_size / self.size
        times = int(percent * self.np)
        percent = percent * 100
        percent = int(percent)

        if self.percent != percent:
            self.percent = percent

            if percent > 9:
                print('\b' * 4,end='')
            else:
                print('\b' * 3,end='')

            print(' ' + str(percent) + '%',end="")
            sys.stdout.flush()

        return content

##
## Utility Functions
##

def convert_to_s3key(file_name,dir_name,alias):
    dir_pos = file_name.index(dir_name)
    key = file_name[dir_pos::]
    alias = alias.strip()

    if len(alias) > 0:
        key = key.replace(dir_name,alias)

    return key

def create_digest(key):
    m = hashlib.md5()
    m.update(key.encode('utf-8'))

    return m.hexdigest()

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def gen_s3_obj(method):
    config = common.get_config()
    session = botocore.session.get_session()
    session.set_credentials(config['access_key'],config['secret_key'])

    s3 = session.get_service('s3')
    operation = s3.get_operation(method)
    endpoint = s3.get_endpoint(config['region'])

    return [endpoint,operation]

##
## S3 Functions
##


def upload_file(key,filename,rrs,encrypt):
    endpoint,operation = gen_s3_obj('PutObject')
    size = os.stat(filename).st_size

    if size == 0:
        print('Bad filesize for "%s"' % (filename))
        return 0

    try:
        fp = ProxyFP(filename)

        http_response, data = operation.call(
            endpoint,
            bucket='k3backup',
            key=key,
            body=fp
        )

        code = http_response.status_code

        if code != 200:
            raise IOError(http_response.content)

        print(os.linesep)
    except IOError as e:
        print(e)
        return 0

    return size

def get_last_sync(config):
    endpoint, operation = gen_s3_obj('GetObject')
    file_name = os.path.join(dirname,'../working/LastSync.txt')

    http_response, data = operation.call(
        endpoint,
        bucket=config[u'bucket'],
        key='LastSync.txt'
    )

    code = http_response.status_code

    if code == 200:
        with open(file_name, 'wb') as f:
            b = data['Body'].read(BUFFSIZE)

            while b:
                f.write(b)
                b = data['Body'].read(BUFFSIZE)
    else:
        message = http_response.content.decode('UTF-8')

        if message.find('The specified key does not exist') != -1:
            open(file_name, 'w').close()
        else:
            raise Exception('Could not download LastySync.txt')

    return

def save_last_sync(config):
    endpoint, operation = gen_s3_obj('PutObject')

    sync_file = os.path.join(dirname,'../working/LastSync.txt')
    local_file = os.path.join(dirname,'../working/LocalList.txt')

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

    fp = open(sync_file,'rb')

    http_response, data = operation.call(
        endpoint,
        bucket=config[u'bucket'],
        key='LastSync.txt',
        body=fp
    )

    code = http_response.status_code

    if code != 200:
        message = str(http_response.content)

        raise Exception(message)

    return

def list_files(config):
    endpoint, operation = gen_s3_obj('ListObjects')
    output_file = os.path.join(dirname,'../working/S3List.txt')

    paginator = botocore.paginate.Paginator(operation)
    iterator = paginator.paginate(
        endpoint,
        bucket=config[u'bucket']
    )

    open(output_file, 'w').close()

    with codecs.open(output_file,encoding='UTF-8',mode='a') as lfile:
        previous_folder = ''

        for result in iterator:
            response, data = result
            items = data['Contents']

            for item in items:
                name = item['Key']

                if item['Size'] == 0:
                    continue

                try:
                    folder = name[0:name.index('/')]

                    if folder != previous_folder:
                        print('      Listing files in %s...' % folder)
                except ValueError:
                    pass

                lfile.write('<>'.join([
                            name,
                            str(item['Size'])
                            ]))

                lfile.write(os.linesep)

                previous_folder = folder

def sync(config):
    config = common.get_config()
    endpoint, operation = gen_s3_obj('DeleteObject')
    input_file = os.path.join(dirname,'../working/TransferList.txt')

    addwc = subprocess.Popen(
        "cat " + input_file + " | grep ADD | wc -l",
        stdout=subprocess.PIPE,
        shell=True
        )
    (output,err) = addwc.communicate()
    addlines = int(output.decode('UTF-8').split(' ')[0])

    deletewc = subprocess.Popen(
        "cat " + input_file + " | grep DELETE | wc -l",
        stdout=subprocess.PIPE,
        shell=True)
    (output,err) = deletewc.communicate()
    deletelines = int(output.decode('UTF-8').split(' ')[0])

    with codecs.open(input_file,encoding='UTF-8',mode='r') as file:
        addcount = 1
        deletecount = 1

        for line in file:
            line = line.strip()
            line_list = line.split('<>')

            action = line_list[0]
            s3key = line_list[1]

            if action == 'ADD':
                file_name = line_list[2]
                rrs = line_list[3]
                encrypt = line_list[4]

                if rrs == '1':
                    rrs = True
                else:
                    rrs = False

                if encrypt == '1':
                    encrypt = True
                else:
                    encrypt = False

                print('      Uploading file (%d / %d) %s...' % (addcount,addlines,file_name))

                upload_file(s3key,file_name,rrs,encrypt)

                addcount = addcount + 1

            if action == 'DELETE':
                print('      Removing file (%d / %d) s3://%s...' % (deletecount,deletelines,s3key))

                response, data = operation.call(
                    endpoint,
                    bucket=config[u'bucket'],
                    key=s3key
                )

                if response.status_code != 204:
                    raise Exception(response.content)

                deletecount = deletecount + 1
