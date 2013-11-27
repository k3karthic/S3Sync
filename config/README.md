Credentials(credentials.json)
=============================

Create a file called 'credentials.json' in this directory, you can use 'sample_credentials.json' as a template.

Region
------
Valid S3 regions are:

* us-east-1: Virginia
* us-west-1: California
* us-west-2: Oregon
* eu-west-1: Ireland
* sa-east-1: Sao Paulo
* ap-southeast-1: Singapore
* ap-southeast-2: Sydney
* ap-northeast-1: Tokyo

Encrypt
-------
You can choose to enable SSE for your files. SSE can be enabled for all files by specifying it in credenetials.json or on a per-folder basis by specifiying it in files.json.
For more information on SSE see [here](http://aws.amazon.com/about-aws/whats-new/2011/10/04/amazon-s3-announces-server-side-encryption-support/).

RRS
---
You can choos to use RRS storage instead of standard storage based on your durability needs. RRS can be enabled for all files by specifying it in credentials.json or on a per-folder basis by specifying it in files.json.
For more information on RRS see [here](http://aws.amazon.com/about-aws/whats-new/2010/05/19/announcing-amazon-s3-reduced-redundancy-storage/).

Files(files.json)
=================

Create a file called 'files.json' in this directory, you can use 'sample_files.json' as a template.

Path
----
Specify the path to the folder that you wish to Sync to S3.

Dir
---
The folder name in the path, this is used to create the folder in S3. Example: If path is 'F:\Documents\Programs' then dir must be 'Programs'.

RRS
---
Allows you to override the global settings in credentials.json for this folder.

Encrypt
---
ALlows you to override the global settings in credentials.json for this folder.

Exclude
---
Array of regex expressions for content that you do not want to sync to S3.
