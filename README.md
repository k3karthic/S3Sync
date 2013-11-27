S3Sync
=========

S3Sync allows you to sync your files to [Amazon S3](http://aws.amazon.com/s3/). 

> S3Sync is of alpha quality and should not be used for critical files.

> S3Sync operates on an entire S3 bucket, it cannot be configured(as yet) to work in a subfolder.

Configuration
-------------
Please look at the readme in the [config](https://github.com/k3karthic/S3Sync/tree/master/config) folder for details on how to configure S3Sync.

Operation
---------
S3 charges you per request and if you tend to store many files, it can lead to a significant charge. To overcome this S3Sync works using S3 batch operations to reduce the number of requests(upto 1000 files in a single request).

To decide what files need to be updated S3Sync comares the size and modification time; size attribute is retreived from S3 whereas the modification time is stored locally(working/LastSync.txt).

S3Sync uses multipart file upload with resume support. In case the program quits for any reason, rerun the program and it will pick up from where it left off.

Screenshot
----------

[![PHP](https://raw.github.com/k3karthic/S3Sync/master/screenshots/php.png)]()
