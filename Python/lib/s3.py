#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import s3sync_lib
import os
import codecs
import sys
import subprocess

import s3_upload as upload

from boto.s3.connection import S3Connection
from boto.s3.key import Key

def list_files(config):
    output_file = os.path.dirname(__file__) + '/../working/S3List.txt'
    
    s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
    bucket = s3conn.get_bucket(config[u'bucket'])
    
    open(output_file, 'w').close()
    
    with codecs.open(output_file,encoding='UTF-8',mode='a') as lfile:
        previous_folder = ''
    
        for key in bucket.list():
            if key.size == 0:
                continue
    
            name = key.name

            try:
                folder = name[0:name.index('/')]
        
                if folder != previous_folder:
                    print('      Listing files in %s...' % folder)
            except ValueError:
                pass
    
            lfile.write('<>'.join([
                        name,
                        str(key.size)
                        ]))
    
            lfile.write(os.linesep)
    
            previous_folder = folder

def sync(config):
    input_file = os.path.dirname(__file__) + '/../working/TransferList.txt'
    
    s3conn = S3Connection(config[u'access_key'],config[u'secret_key'])
    bucket = s3conn.get_bucket(config[u'bucket'])

    addwc = subprocess.Popen(
        "cat " + input_file + " | grep ADD | wc -l",
        stdout=subprocess.PIPE,
        shell=True
        )
    (output,err) = addwc.communicate()
    addlines = int(output.split(' ')[0])

    deletewc = subprocess.Popen(
        "cat " + input_file + " | grep DELETE | wc -l",
        stdout=subprocess.PIPE,
        shell=True)
    (output,err) = deletewc.communicate()
    deletelines = int(output.split(' ')[0])
    
    with codecs.open(input_file,encoding='UTF-8',mode='r') as file:
        addcount = 1
        deletecount = 1

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
    
                if rrs == '1':
                    rrs = True
                else:
                    rrs = False
    
                if encrypt == '1':
                    encrypt = True
                else:
                    encrypt = False
    
                print('      Uploading file (%d / %d) %s...' % (addcount,addlines,file_name))
    
                upload.upload_file(k,file_name,rrs,encrypt)

                addcount = addcount + 1
    
            if action == 'DELETE':
                print('      Removing file (%d / %d) s3://%s...' % (deletecount,deletelines,s3key))
    
                bucket.delete_key(k)

                deletecount = deletecount + 1
