<?php

require_once dirname(__FILE__) . '/./common.php';

$config = getConfig();
$files = getFiles();
$handle = fopen(dirname(__FILE__) . '/../working/LocalList.txt','w');

function recurse_directory($it,$file,$rrs,$encrypt) {
    global $handle;
    $dirsub = $file['dir'];
    $excludes = array();
    $alias = "";

    if(isset($file['exclude'])) {
        $excludes = $file['exclude'];
    }

    if(isset($file['alias'])) {
        $alias = $file['alias'];
    }

    try {
        while($it->valid()) {
            if($it->hasChildren()) {
                recurse_directory($it->getChildren(),$file,$rrs,$encrypt);
            } else if(!$it->isDot()) {
                $key = $it->key();
                $valid = true;

                foreach($excludes as $e) {
                    $check = "%$e%";

                    if(substr($e,0,1) === '/') {
                        $check = '%' . $dirsub . $e . '%';
                    }

                    if(preg_match($check,$key)) {
                        $valid = false;
                        break;
                    }
                }

                $size = filesize($key);
                if($valid && $size > 0) {
                    fwrite($handle,$dirsub . "<>$key<>" . $size . '<>' . filemtime($key) . "<>$rrs<>$encrypt<>$alias" .PHP_EOL);
                }
            }

            $it->next();
        }
    } catch(Exception $e) {
        throw $e;
    }
}

try {
    foreach($files as $file) {
        $rrs = $config['rrs'];
        $encrypt = $config['encrypt'];

        $it = new RecursiveDirectoryIterator(
            $file['path'],
            FilesystemIterator::UNIX_PATHS
        );

        if(isset($file['rrs'])) {
            $rrs = $file['rrs'];
        }

        if(isset($file['encrypt'])) {
            $encrypt = $file['encrypt'];
        }

        recurse_directory($it,$file,$rrs,$encrypt);
    }
} catch(Exception $e) {
    echo "Error: " . $e->getMessage();
    exit(1);
}

fclose($handle);
