<?php

require_once dirname(__FILE__) . '/./common.php';
require_once dirname(__FILE__) . '/../composer/vendor/autoload.php';
use Aws\S3\S3Client;

$handle = fopen(dirname(__FILE__) . '/../working/S3List.txt','w');
$config = getConfig();

try {
    $client = S3Client::factory(array(
        'key' => $config['access_key'],
        'secret' => $config['secret_key'],
        'region' => $config['region']
    ));

    $iterator = $client->getIterator('ListObjects',array(
        'Bucket' => $config['bucket']
    ));

    foreach($iterator as $object) {
        $size = $object['Size'];
        $key = $object['Key'];

        if(substr($key,-1) === '/') {
            continue;
        }

        fwrite($handle,$key . '<>' . $size . PHP_EOL);
    }
} catch(Exception $e) {
    echo "Error: " . $e->getMessage();
    exit(1);
}

fclose($handle);
