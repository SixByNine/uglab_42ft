<html>
<head>
  <link rel="stylesheet" href="42ft.css">
</head>
<body>
<h1>JBO 42ft Undergraduate Lab Portal</h1>
<p>This is the data access portal for the 42ft telescope 3rd year lab experiment</p>
<p><a href='https://github.com/SixByNine/crab_42ft_jbo_templates'>Template codes</a></p>
<p><a href='2023_ssb.txt'>2023 Solar System Barycentre file</a></p>

<h2>Data Request Form</h2>
<form action='find.php' id='requestform'>
<label for='psr'>PSR</label><input type='text' name='psr' id='psr' placeholder='e.g. B0329+54'><br>
<label for='day'>Date</label><input type='text' name='day' id='day' placeholder='e.g. 20220428'> (YYYYMMDD)<br>
<label for='ut'>Hour</label><input type='text' name='ut' id='ut' placeholder='e.g. 14'> (UTC start of observation, 24h format)<br>
<input type='submit' value="Request data">
<p>Last heard from server: <?php
echo file_get_contents( "jobs/.atime");
?></p>
</form>



<h2>Data</h2>
<table>
<tr><th>Day</th><th>Time(UT)</th><th>PSR</th><th>URL/Status</th></tr>
<?php
$root="http://www.pulsars.eu.org/new/lab/42ft";

$jobs = scandir("jobs");
foreach ($jobs as $job) {
    if (substr($job,0,1)==".") {
        continue;
    }
    $f=fopen("jobs/$job","r");
    $line = fgets($f);
    //    print("--$job-$line---");
    $e=explode(" ",$line,4);
    print("<tr class='submitted'>");
    print("<td>$e[0]</td>");
    print("<td>$e[1]</td>");
    print("<td>$e[2]</td>");
    print("<td>$e[3]</td>");
    print("</tr>\n");
    fclose($f);
}

$data = scandir("data");
foreach ($data as $d) {
    if (substr($d,0,1)==".") {
        continue;
    }
    $day=substr($d,0,8);
    $time=substr($d,9,6);
    $psr=substr($d,16,strpos($d,".")-16);
    print("<tr class='data'>");
    print("<td>$day</td>");
    print("<td>$time</td>");
    print("<td>$psr</td>");
    print("<td><a href='data/$d'>$root/data/$d</a></td>");
    print("</tr>\n");
}

?>
</table>


</body>
</html>
