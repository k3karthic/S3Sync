<?php


function write_trace($message) {
    echo date('Y-m-d H:i:s');
    echo "::$message";
    echo "\n";
}

function humanTiming($time) {
    $tokens = array (
        31536000 => 'year',
        2592000 => 'month',
        604800 => 'week',
        86400 => 'day',
        3600 => 'hour',
        60 => 'minute',
        1 => 'second'
    );

    foreach ($tokens as $unit => $text) {
        if ($time < $unit) continue;
        $numberOfUnits = floor($time / $unit);
        return $numberOfUnits.' '.$text.(($numberOfUnits>1)?'s':'');
    }
}

function getConfig() {
    $json = file_get_contents(dirname(__FILE__) . '/../../config/credentials.json');

    return json_decode($json,true);
}

function getFiles() {
    $json = file_get_contents(dirname(__FILE__) . '/../../config/files.json');

    return json_decode($json,true);
}
