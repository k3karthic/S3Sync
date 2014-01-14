#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import datetime

import lib.s3sync_lib as lib
import lib.local as local
import lib.s3 as cloud

config = lib.get_config()
files = lib.get_files()

print('Getting FileList From S3...')
lib.get_last_sync(config)

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
lib.save_last_sync(config)

print('')

print('Clearing working directory...')
lib.clear_working()
