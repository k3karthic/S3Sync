S3Sync
=========

S3Sync allows you to sync your files to [Amazon S3](http://aws.amazon.com/s3/). 

> S3Sync operates on an entire S3 bucket, it cannot be configured(as yet) to work in a subfolder.

Modules Required
----------------
* Botocore

Configuration
-------------
Please look at the readme in the [config](https://github.com/k3karthic/S3Sync/tree/master/config) folder for details on how to configure S3Sync.

Operation
---------
* S3Sync uses the ListBucket API call allowing it to scan through an S3 bucket a 1000 keys at a time.
* S3Sync maintains a record of the modification times and stores in a file in S3 (S3Sync.txt).

This allows S3Sync to sync based on size and modification time on a large number of files very rapidly.

Screenshot
----------

[![PHP](https://raw.github.com/k3karthic/S3Sync/master/screenshots/python.png)]()
