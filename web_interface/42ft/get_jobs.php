<?php
header("Content-Type: text/plain");

$d = date('Y-m-d H:i:s', time());
$f = fopen("jobs/.atime","w");
fwrite($f,"$d\n");
fclose($f);

$jobs = scandir("jobs");
foreach ($jobs as $job) {
    if (substr($job,0,1)==".") {
        continue;
    }
    $f=fopen("jobs/$job","r");
    $line = fgets($f);
    $e=explode(" ",$line,4);
    print("$e[0] $e[1] $e[2] $job\n");
    fclose($f);

    $f=fopen("jobs/$job","w");
    fwrite($f,"$e[0] $e[1] $e[2] Fetched for processing ($d)");
    fclose($f);
}

?>
