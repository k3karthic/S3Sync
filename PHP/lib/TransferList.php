<?php

require_once dirname(__FILE__) . '/./common.php';
require_once dirname(__FILE__) . '/../composer/vendor/autoload.php';
use Aws\S3\S3Client;

$s3_file = fopen(dirname(__FILE__) . '/../working/S3List.txt','r');
$local_file = fopen(dirname(__FILE__) . '/../working/LocalList.txt','r');
$trans_file = fopen(dirname(__FILE__) . '/../working/TransferList.txt','w');
$last_sync = @fopen(dirname(__FILE__) . '/../working/LastSync.txt','r');
$hash_algo = 'sha512';

function convertS3Key($dirsub,$path,$alias) {
    $subpath = substr($path,strpos($path,$dirsub));

    if(strlen($alias) > 0) {
        $subpath = str_replace($dirsub,$alias,$subpath);
    }

    return $subpath;
}

try {
    $rootdirs = array();
    $s3files = array();

    while(!feof($s3_file)) {
        $line = trim(fgets($s3_file));

        if(strlen($line) > 0) {
            list($key,$size) = explode('<>',$line);
            $s3files[hash($hash_algo,$key)] = array($key,$size,"");
        }
    }

    if($last_sync !== false) {
        while(!feof($last_sync)) {
            $line = trim(fgets($last_sync));

            if(strlen($line) > 0) {
                list($dirsub,$path,$mtime,$alias) = explode('<>',$line);
                $key = convertS3Key($dirsub,$path,$alias);
                $hash = hash($hash_algo,$key);

                if(isset($s3files[$hash])) {
                    $s3files[$hash][2] = $mtime;
                }
            }
        }

        fclose($last_sync);
    }

    $last_sync = fopen(dirname(__FILE__) . '/../working/LastSync.txt','w');

    while(!feof($local_file)) {
        $line = trim(fgets($local_file));

        if(strlen($line) > 0) {
            list($dirsub,$path,$size,$mtime,$rrs,$enc,$alias) = explode('<>',$line);
            fwrite($last_sync,"$dirsub<>$path<>$mtime<>$alias" . PHP_EOL);

            $rootdirs[$dirsub] = 1;
            $subpath = convertS3Key($dirsub,$path,$alias);

            $hash = hash($hash_algo,$subpath);

            if(isset($s3files[$hash])) {
                list($s3key,$s3size,$s3mtime) = $s3files[$hash];

                if(strlen($s3mtime) === 0) {
                    $s3mtime = $mtime;
                }

                if($size !== $s3size || $mtime !== $s3mtime) {
                    fwrite(
                        $trans_file,
                        realpath($path) . '<>' .
                        $subpath . '<>' .
                        'ADD' . '<>' .
                        $rrs . '<>' .
                        $enc .
                        PHP_EOL
                    );
                }

                unset($s3files[$hash]);
            } else {
                fwrite(
                    $trans_file,
                    realpath($path) . '<>' .
                    $subpath . '<>' .
                    'ADD' . '<>' .
                    $rrs . '<>' .
                    $enc .
                    PHP_EOL
                );
            }
        }
    }

    foreach($s3files as $key => $val) {
        if(isset($rootdirs[substr($key,0,-1)])) {
            continue;
        }

        fwrite($trans_file,"DELETE<>".$val[0]."<>DELETE<>1<>1" . PHP_EOL);
    }
} catch(Exception $e) {
    echo "Error: " . $e->getMessage();
    exit(1);
}

fclose($s3_file);
fclose($local_file);
fclose($trans_file);
fclose($last_sync);
