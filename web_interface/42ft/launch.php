<?php



$day=$_GET['day'];
$psr=str_replace(" ","+",$_GET['psr']);
$ut=$_GET['ut'];
$user=preg_replace( '/[\W]/', '_', $_GET['user']);

header("Location: index.php?user=$user");
#print("Location: index.php?user=$user");
#$uid = uniqid();

$uid = $day."_".$ut."_".$psr;

$d = date('m/d/Y h:i:s a', time());
$f = fopen("jobs/$uid","w");
fwrite($f,"$day $ut $psr Submitted for processing ($d)");
fclose($f);

if (!is_dir("users/$user")) {
    mkdir("users/$user");
}
$f = fopen("users/$user/$uid","w");
fwrite($f,"$day $ut $psr");
fclose($f);





?>
