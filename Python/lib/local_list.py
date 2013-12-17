#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import s3sync_lib
import os
import codecs
import re

config = s3sync_lib.get_config()
files = s3sync_lib.get_files()
output_file = os.path.dirname(__file__) + '/../working/LocalList.txt'

# Clear file
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

    with codecs.open(output_file,encoding='UTF-8',mode='a') as lfile:
        dir_name = os.path.basename(dir_path)
        print('Listing files in %s...' % dir_name)

        for root,dir,files in os.walk(dir_path):
            for file in files:
                skip = False
                file_path = os.path.join(root,file)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)

                for restr in exclude:
                    if re.match(restr,file):
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
