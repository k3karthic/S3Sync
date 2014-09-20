#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

import datetime
import os
import shutil

from . import common
from . import local
from . import s3 as cloud

dirname = os.path.dirname(__file__)
sample_config_dir = os.path.join(dirname, 'config')

#===========
# Functions
#===========


def check_configuration():
    first_time = False
    directory = common.dirname
    config_dir = os.path.join(directory, 'config')
    working_dir = os.path.join(directory, 'working')

    if not os.path.exists(directory):
        first_time = True
        os.makedirs(directory)

    if not os.path.exists(config_dir):
        first_time = True
        shutil.copytree(sample_config_dir, config_dir)

    if not os.path.exists(working_dir):
        first_time = True
        os.makedirs(working_dir)

    return first_time


def sync_files():
    print('Getting FileList From S3...')
    cloud.get_last_sync()

    print('')

    print('------Listing files in local system------')
    start = datetime.datetime.now()
    local.list_files()
    stop = datetime.datetime.now()
    elapsed = stop - start
    print('------Elapsed Time: %s------' % elapsed)

    print('')

    print('------Listing files stored in S3------')
    start = datetime.datetime.now()
    cloud.list_files()
    stop = datetime.datetime.now()
    elapsed = stop - start
    print('------Elapsed Time: %s------' % elapsed)

    print('')

    print('------Calculating differences------')
    start = datetime.datetime.now()
    local.calc_diff()
    stop = datetime.datetime.now()
    elapsed = stop - start
    print('------Elapsed Time: %s------' % elapsed)

    print('')

    print('------Syncing changes------')
    start = datetime.datetime.now()
    cloud.sync()
    stop = datetime.datetime.now()
    elapsed = stop - start
    print('------Elapsed Time: %s------' % elapsed)

    print('')

    print('Uploading FileList to S3...')
    cloud.save_last_sync()

    print('')

    print('Clearing working directory...')
    common.clear_working()

#======
# Main
#======


def main():
    first_time = check_configuration()

    if first_time is False:
        sync_files()
    else:
        print(
            'Sample confiuration has been placed in %s' %
            common.dirname
        )

    return 0
