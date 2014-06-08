#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

import datetime

from . import common
from . import local
from . import s3 as cloud


#===========
# Functions
#===========


def check_configuration():
    return

#======
# Main
#======


def main():
    print('Ok')
    return 0
    check_configuration()

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

    print('------Syncing changes to S3------')
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

    return 0
