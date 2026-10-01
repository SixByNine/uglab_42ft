<?php
header("Content-Type: text/plain");
$jid=$_GET['jid'];

$jobs = scandir("jobs");
foreach ($jobs as $job) {
    if (substr($job,0,1)==".") {
        continue;
    }
    if($job==$jid) {
        unlink("jobs/$job");
        print("jobs/$job");
    }
}

?>
