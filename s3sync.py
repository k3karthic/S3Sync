#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys
import datetime

from lib import common
from lib import local
from lib import s3 as cloud

config = common.get_config()
files = common.get_files()

print('Getting FileList From S3...')
cloud.get_last_sync(config)

print('')

print('------Listing files in local system------')
start = datetime.datetime.now()
local.list_files(config,files)
stop = datetime.datetime.now()
elapsed = stop - start
print('------Elapsed Time: %s------' % elapsed)

print('')

print('------Listing files stored in S3------')
start = datetime.datetime.now()
cloud.list_files(config)
stop = datetime.datetime.now()
elapsed = stop - start
print('------Elapsed Time: %s------' % elapsed)

print('')

print('------Calculating differences------')
start = datetime.datetime.now()
local.calc_diff(config)
stop = datetime.datetime.now()
elapsed = stop - start
print('------Elapsed Time: %s------' % elapsed)

print('')

print('------Syncing changes to S3------')
start = datetime.datetime.now()
local.calc_diff(config)
cloud.sync(config)
stop = datetime.datetime.now()
elapsed = stop - start
print('------Elapsed Time: %s------' % elapsed)

print('')

print('Uploading FileList to S3...')
cloud.save_last_sync(config)

print('')

print('Clearing working directory...')
common.clear_working()
