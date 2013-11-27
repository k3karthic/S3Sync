#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import s3sync_lib
import os
import codecs

config = s3sync_lib.get_config()
files = s3sync_lib.get_files()
output_file = os.path.dirname(__file__) + '/../working/LocalList.txt'

# Clear file
open(output_file, 'w').close()

for file in files:
    dir_path = os.path.abspath(file[u'path'])
    dir_name = file[u'dir']
    rrs = config[u'rrs']
    encrypt = config[u'encrypt']
    alias = u''

    if u'rrs' in file:
        rrs = file[u'rrs']

    if u'encrypt' in file:
        encrypt = file[u'encrypt']

    if u'alias' in file:
        alias = file[u'alias']

    with codecs.open(output_file,encoding='UTF-8',mode='a') as lfile:
        for root,dir,files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root,file)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)

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
