#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# Python 2-3 Compat
import six

from six import iterkeys
from six import itervalues
from six import iteritems
from six import iterlists

import os
import sys
import codecs
import hashlib
import six

from . import common

import botocore.session
import botocore.paginate

#===========
# Constants
#===========

MIN_PROG_SIZE = 1024 * 1024
BUFFSIZE = 1024 * 8
dirname = common.dirname

#============
#  Classes
#============


class ProxyFP:
    def __init__(self, filename):
        self.filename = filename
        self.size = os.path.getsize(filename)
        self.curr_size = 0
        self.fp = open(filename, 'rb')
        self.start = True
        self.percent = 0
        self.np = 20

    def __len__(self):
        return int(self.size)

    __nonzero__ = __len__

    def seek(self, pos):
        self.fp.seek(pos)

    def read(self, size):
        if self.start is True:
            six.print_('      Progress:    ', end="")
            sys.stdout.flush()
            self.start = False

        content = self.fp.read(size)
        size = len(content)
        self.curr_size = self.curr_size + size
        # Force floating point division in python 2
        percent = float(self.curr_size) / float(self.size)
        percent = percent * 100
        percent = int(percent)

        if self.percent != percent:
            self.percent = percent

            if percent > 9:
                six.print_('\b' * 4, end='')
            else:
                six.print_('\b' * 3, end='')

            six.print_(' ' + str(percent) + '%', end="")
            sys.stdout.flush()

        return content

#====================
#  Utility Functions
#====================


def convert_to_s3key(file_name, dir_name, alias):
    dir_pos = file_name.index(dir_name)
    key = file_name[dir_pos::]
    alias = alias.strip()

    if len(alias) > 0:
        key = key.replace(dir_name, alias)

    # Replace \ with / for windows paths
    key = key.replace('\\', '/')

    return key


def create_digest(key):
    m = hashlib.md5()
    m.update(key.encode('utf-8'))

    return m.hexdigest()


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


def gen_s3_obj(method):
    config = common.get_config()
    session = botocore.session.get_session()
    session.set_credentials(config['access_key'], config['secret_key'])

    s3 = session.get_service('s3')
    operation = s3.get_operation(method)
    endpoint = s3.get_endpoint(config['region'])

    return [endpoint, operation]

#  #
#  # S3 Functions
#  #


def upload_file(key, filename, rrs, encrypt):
    config = common.get_config()
    endpoint, operation = gen_s3_obj('PutObject')
    size = os.stat(filename).st_size
    storage_class = 'STANDARD'
    encryption = ''

    if size == 0:
        print('Bad file size for "%s"' % (filename))
        return 0

    if rrs == 1:
        storage_class = 'REDUCED_REDUNDANCY'

    if encrypt == 1:
        encryption = 'AES256'

    try:
        fsize = os.stat(filename).st_size

        if fsize < MIN_PROG_SIZE:
            fp = open(filename, 'rb')
        else:
            fp = ProxyFP(filename)

        http_response, _ = operation.call(
            endpoint,
            bucket=config[u'bucket'],
            key=key,
            body=fp,
            storage_class=storage_class,
            server_side_encryption=encryption
        )

        if fsize < MIN_PROG_SIZE:
            fp.close()

        code = http_response.status_code

        if code != 200:
            raise IOError(http_response.content)

        print(os.linesep)
    except IOError as e:
        print(e)
        return 0

    return size


def download_file(key, filename, file_mtime):
    config = common.get_config()
    endpoint, operation = gen_s3_obj('GetObject')
    size = os.stat(filename).st_size

    if size == 0:
        print('Bad file size for "%s"' % (filename))
        return 0

    try:
        http_response, data = operation.call(
            endpoint,
            bucket=config[u'bucket'],
            key=key
        )

        code = http_response.status_code

        if code != 200:
            raise IOError(http_response.content)

        with open(filename, 'wb') as f:
            b = data['Body'].read(BUFFSIZE)

            while b:
                f.write(b)
                b = data['Body'].read(BUFFSIZE)

        os.utime(
            filename, (
                os.path.getatime(filename),
                int(float(file_mtime))
            )
        )

        print(os.linesep)
    except IOError as e:
        print(e)
        return 0

    return size


def get_last_sync():
    config = common.get_config()
    endpoint, operation = gen_s3_obj('GetObject')
    file_name = os.path.join(dirname, 'working', 'LastSync.txt')

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
        open(file_name, 'w').close()

    return


def save_last_sync():
    config = common.get_config()
    endpoint, operation = gen_s3_obj('PutObject')

    sync_file = os.path.join(dirname, 'working', 'LastSync.txt')
    local_file = os.path.join(dirname, 'working', 'LocalList.txt')

    with codecs.open(sync_file, encoding='UTF-8', mode='w') as sync_fileh:
        with codecs.open(local_file, encoding='UTF-8', mode='r') as sfile:
            for line in sfile:
                line_list = line.split('<>')
                dir_name = line_list[0]
                file_name = line_list[1]
                file_mtime = line_list[3]
                alias = line_list[6]
                file_key = convert_to_s3key(file_name, dir_name, alias)

                sync_fileh.write('<>'.join([file_key, file_mtime]))

                sync_fileh.write(os.linesep)

    fp = open(sync_file, 'rb')

    http_response, _ = operation.call(
        endpoint,
        bucket=config[u'bucket'],
        key='LastSync.txt',
        body=fp
    )

    fp.close()

    code = http_response.status_code

    if code != 200:
        message = str(http_response.content)

        raise Exception(message)

    return


def list_files():
    config = common.get_config()
    endpoint, operation = gen_s3_obj('ListObjects')
    output_file = os.path.join(dirname, 'working', 'S3List.txt')

    paginator = botocore.paginate.Paginator(operation)
    iterator = paginator.paginate(
        endpoint,
        bucket=config[u'bucket']
    )

    open(output_file, 'w').close()

    with codecs.open(output_file, encoding='UTF-8', mode='a') as lfile:
        previous_folder = ''

        for result in iterator:
            _, data = result
            items = data['Contents']

            for item in items:
                name = item['Key']

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


def sync():
    config = common.get_config()
    endpoint, operation = gen_s3_obj('DeleteObject')
    input_file = os.path.join(dirname, 'working', 'TransferList.txt')

    # Count number of add and delete commands
    addlines = 0
    downlines = 0
    deletelines = 0
    with codecs.open(input_file, encoding='UTF-8', mode='r') as input_fileh:
        for line in input_fileh:
            if line.find('ADD') == 0:
                addlines = addlines + 1
            elif line.find('DOWN') == 0:
                downlines = downlines + 1
            else:
                deletelines = deletelines + 1

    with codecs.open(input_file, encoding='UTF-8', mode='r') as input_fileh:
        addcount = 1
        downcount = 1
        deletecount = 1

        for line in input_fileh:
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

                print(
                    '      Uploading file (%d / %d) %s...' %
                    (addcount, addlines, file_name.encode('utf-8'))
                )

                upload_file(s3key, file_name, rrs, encrypt)

                addcount = addcount + 1

            if action == 'DOWN':
                file_name = line_list[2]
                file_mtime = line_list[3]

                print(
                    '      Downloading file (%d / %d) %s...' %
                    (downcount, downlines, file_name.encode('utf-8'))
                )

                download_file(s3key, file_name, file_mtime)

                downcount = downcount + 1

            if action == 'DELETE':
                print(
                    '      Removing file (%d / %d) s3://%s...' %
                    (deletecount, deletelines, s3key.encode('utf-8'))
                )

                response, _ = operation.call(
                    endpoint,
                    bucket=config[u'bucket'],
                    key=s3key
                )

                if response.status_code != 204:
                    raise Exception(response.content)

                deletecount = deletecount + 1
