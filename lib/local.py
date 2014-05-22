#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

import os
import codecs
import re

from lib import s3
from lib import common

dirname = os.path.dirname(__file__)


def list_files():
    config = common.get_config()
    files = common.get_files()
    output_file = os.path.join(dirname, '../working/LocalList.txt')

    open(output_file, 'w').close()

    for file in files:
        dir_path = os.path.abspath(file[u'path'])
        exclude = []
        rrs = config[u'rrs']
        encrypt = config[u'encrypt']
        alias = u''

        if u'rrs' in file:
            rrs = file[u'rrs']

        if u'encrypt' in file:
            encrypt = file[u'encrypt']

        if u'alias' in file:
            alias = file[u'alias']

        if u'exclude' in file:
            exclude = file[u'exclude']

        with codecs.open(output_file, encoding='UTF-8', mode='a') as lfile:
            dir_name = os.path.basename(dir_path)
            print('      Listing files in %s...' % dir_name)

            for root, _, files in os.walk(dir_path):
                for file in files:
                    skip = False
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_mtime = os.path.getmtime(file_path)

                    for restr in exclude:
                        if re.search(restr, file_path):
                            skip = True
                            break

                    if skip == True:
                        continue

                    if file_size == 0:
                        continue

                    lfile.write('<>'.join([
                        dir_name,
                        file_path,
                        str(file_size),
                        str(file_mtime),
                        str(rrs),
                        str(encrypt),
                        str(alias)
                    ]))

                    lfile.write(os.linesep)


def calc_diff():
    local_list_file = os.path.join(dirname,'..','working','LocalList.txt')
    s3_list_file = os.path.join(dirname, '..','working','S3List.txt')
    last_sync_file = os.path.join(dirname, '..','working','LastSync.txt')
    output_file = os.path.join(dirname, '..','working','TransferList.txt')

    s3_files = {}
    local_files = {}
    mtime_files = {}

    open(output_file, mode='w').close()

    with codecs.open(s3_list_file, encoding='UTF-8', mode='r') as sfile:
        for line in sfile:
            line = line.strip()
            s3key, size = line.split('<>')

            s3key_hash = s3.create_digest(s3key)

            s3_files[s3key_hash] = [s3key, size]

    with codecs.open(local_list_file, encoding='UTF-8', mode='r') as lfile:
        for line in lfile:
            line = line.strip()
            line_list = line.split('<>')
            dir_name = line_list[0]
            file_name = line_list[1]
            alias = line_list[6]

            file_key = s3.convert_to_s3key(file_name, dir_name, alias)
            file_key_hash = s3.create_digest(file_key)

            line_list.append(file_key)
            local_files[file_key_hash] = line_list

    with codecs.open(last_sync_file, encoding='UTF-8', mode='r') as sfile:
        for line in sfile:
            line = line.strip()
            key, mtime = line.split('<>')

            key_hash = s3.create_digest(key)

            mtime_files[key_hash] = [key, mtime]

    with codecs.open(output_file, encoding='UTF-8', mode='w') as ofile:
        for key in local_files:
            file_list = local_files[key]
            file_name = file_list[1]
            file_size = file_list[2]
            file_mtime = file_list[3]
            file_key = file_list[7]

            if key in s3_files:
                add_file = False
                s3key, s3size = s3_files[key]
                s3mtime = 0

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
                                file_key,
                                file_name,
                                file_list[4],
                                file_list[5]
                                ]))

                    ofile.write(os.linesep)
            else:
                ofile.write('<>'.join([
                            'ADD',
                            file_key,
                            file_name,
                            file_list[4],
                            file_list[5]
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
