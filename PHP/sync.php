<?php

require_once dirname(__FILE__) . '/./lib/common.php';

ob_implicit_flush(true);

function display_error(&$output) {
    foreach($output as $line) {
        echo $line;
    }

    exit(1);
}

write_trace("----Traverse Local System----");
$stime = time();
exec("php ./lib/LocalList.php",$output,$return);
if($return === 1) {
    display_error($output);
}
$etime = time() - $stime;
write_trace("----(" . humanTiming($etime) . ")----");
echo PHP_EOL;

write_trace("----Traverse S3 Bucket----");
$stime = time();
exec("php ./lib/S3List.php",$output,$return);
if($return === 1) {
    display_error($output);
}
$etime = time() - $stime;
write_trace("----(" . humanTiming($etime) . ")----");
echo PHP_EOL;

write_trace("----Compute Differences----");
$stime = time();
exec("php ./lib/TransferList.php",$output,$return);
if($return === 1) {
    display_error($output);
}
$etime = time() - $stime;
write_trace("----(" . humanTiming($etime) . ")----");
echo PHP_EOL;

write_trace("----Transfer To S3----");
$stime = time();
system("php ./lib/UploadS3.php");
$etime = time() - $stime;
write_trace("----(" . humanTiming($etime) . ")----");
echo PHP_EOL;
