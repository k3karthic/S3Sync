#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Originial Source: https://gist.github.com/dpetzold/510222

import os
import sys
import optparse
import progressbar
import time

pbar = None

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def progress_callback(current, total):
    try:
        pbar.update(current)
    except AssertionError, e:
        print e

def upload_file(key,filename,rrs,encrypt):
    global pbar

    size = os.stat(filename).st_size
    if size == 0:
        print 'Bad filesize for "%s"' % (filename)
        return 0

    widgets = [
        '      ',
        progressbar.FileTransferSpeed(),
        ' <<<', progressbar.Bar(), '>>> ',
        progressbar.Percentage(), ' ', progressbar.ETA()
    ]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=size)
    pbar.start()

    try:
        key.set_contents_from_filename(
            filename,
            cb=progress_callback,
            num_cb=100,
            reduced_redundancy=rrs,
            encrypt_key=encrypt
            )
    except IOError, e:
        print e
        return 0

    pbar.finish()
    return size
