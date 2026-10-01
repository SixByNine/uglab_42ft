<html>
    <head>
        <title>42ft Data Portal</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="42ft.css">
    </head>
    <body>

<?php
$day=$_GET['day'];
$psr=str_replace(" ","+",$_GET['psr']);
$ut=$_GET['ut'];

$user=preg_replace( '/[\W]/', '_', $_GET['user']);

if (strlen($ut) < 2) {
    $ut = "0$ut";
}
if (strlen($ut) > 2) {
    $ut = substr($ut,0,2);
}


$index = file_get_contents("index.txt");
$obs=explode("\n",$index);
print("<h2>Matching observations</h2>");
print("<p class='helptext'>The following observations match your search criteria. Click the link to request processing of the data.</p>");
print("<ul>");
$i=0;
foreach ($obs as $o) {
    $a=explode(" ",$o);
    if ($a[0] == $day && $a[2] == $psr){
        if (substr($a[1],0,2)==$ut){
            print("<li><a href='launch.php?user=$user&psr=$a[2]&day=$a[0]&ut=$a[1]'>PSR $a[2]; Day: $a[0]; UT:$a[1]</a></li>");
            $i = $i + 1;
        }
    }
}
print("</ul>");
print("<p><strong>Total $i observations found</strong> (matching Day=$day; PSR=$psr; UT=${ut}****)</p>");


?>
</body>
</html>
