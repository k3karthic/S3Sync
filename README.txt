S3Sync
======

S3Sync allows you to sync your files to `Amazon S3`_.

    S3Sync operates on an entire S3 bucket, it cannot be configured(as
    yet) to work in a subfolder.

Installation
------------

::

    python setup.py install

Usage
-----

::

    s3sync

    s3sync creates a sample configuration directory in your home folder
    if it doesn’t exist

Configuration
-------------

Credentials(credentials.json)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a file called ‘credentials.json’ in this directory, you can use
‘sample\_credentials.json’ as a template.

Region
^^^^^^

Valid S3 regions are:

-  us-east-1: Virginia
-  us-west-1: California
-  us-west-2: Oregon
-  eu-west-1: Ireland
-  sa-east-1: Sao Paulo
-  ap-southeast-1: Singapore
-  ap-southeast-2: Sydney
-  ap-northeast-1: Tokyo

Encrypt
^^^^^^^

| You can choose to enable SSE for your files. SSE can be enabled for all files by specifying it in credenetials.json or on a per-folder basis by specifiying it in files.json.

| For more information on SSE see `here`_.

RRS
^^^

| You can choos to use RRS storage instead of standard storage based on your durability needs. RRS can be enabled for all files by specifying it in credentials.json or on a per-folder basis by specifying it in files.json.

| For more information on RRS see here <http://aws.amazon.com/about-aws/whats-new/2010/05/19/announcing-amazon-s3-reduced-redundancy-storage/>.

Files(files.json)
~~~~~~~~~~~~~~~~~

Create a file called ‘files.json’ in this directory, you can use
‘sample\_files.json’ as a template.

Path
^^^^

Specify the path to the folder that you wish to Sync to S3.

Dir
^^^

The folder name in the path, this is used to create the folder in S3.
Example: If path is ‘F:\\Documents\\Programs’ then dir must be
‘Programs’.

RRS
^^^

Allows you to override the global settings in credentials.json for this
folder.

Encrypt
^^^^^^^

ALlows you to override the global settings in credentials.json for this
folder.

Exclude
^^^^^^^

Array of regex expressions for content that you do not want to sync to
S3.

Operation
---------

-  S3Sync uses the ListBucket API call allowing it to scan through an S3
   bucket a 1000 keys at a time.
-  S3Sync maintains a record of the modification times and stores in a
   file in S3 (LastSync.txt).

This allows S3Sync to sync based on size and modification time on a
large number of files very rapidly.

Screenshot
----------

|Python|

.. _Amazon S3: http://aws.amazon.com/s3/
.. _here: http://aws.amazon.com/about-aws/whats-new/2011/10/04/amazon-s3-announces-server-side-encryption-support/

.. |Python| image:: https://raw.github.com/k3karthic/S3Sync/master/docs/screenshots/python.png