<?php

require_once dirname(__FILE__) . '/./common.php';
require_once dirname(__FILE__) . '/../composer/vendor/autoload.php';
use Aws\Common\Enum\Size;
use Aws\Common\Exception\MultipartUploadException;
use Aws\S3\S3Client;
use Aws\S3\Model\MultipartUpload\UploadBuilder;

$handle = fopen(dirname(__FILE__) . '/../working/TransferList.txt','r');
$config = getConfig();

try {
    $client = S3Client::factory(array(
        'key' => $config['access_key'],
        'secret' => $config['secret_key'],
        'region' => $config['region']
    ));

    $doptions = array(
        'Bucket' => $config['bucket']
    );

    while(!feof($handle)) {
        $line = trim(fgets($handle));

        if(strlen($line) > 0) {
            list($path,$key,$op,$rrs,$enc) = explode('<>',$line);

            $uploader = UploadBuilder::newInstance()
                ->setClient($client)
                ->setBucket($config['bucket']);

            if($rrs == 1) {
                $uploader = $uploader->setOption('StorageClass','REDUCED_REDUNDANCY');
            } else {
                $uploader = $uploader->setOption('StorageClass','STANDARD');
            }

            if($enc == 1) {
                $uploader = $uploader->setOption('ServerSideEncryption','AES256');
            }

            if($op === "ADD") {
                echo "Uploading : $path" . PHP_EOL;

                $uploader = $uploader->setSource($path)
                    ->setKey($key)
                    ->build();

                $uploader->upload( );
            } else if($op === "DELETE") {
                echo "Removing : $key" . PHP_EOL;

                $doptions['Key'] = $key;

                $client->deleteObject($doptions);
            }
        }
    }
} catch(Exception $e) {
    echo "Error: " . $e->getMessage() . PHP_EOL;
    exit(1);
}

fclose($handle);
