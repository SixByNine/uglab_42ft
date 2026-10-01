<?php
if (array_key_exists("user",$_GET)) {
    $user=preg_replace( '/[\W]/', '_', $_GET['user']);
}
require_once "row_helper.php";
?>

<html>
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="42ft.css">
  <script src="42ft.js"></script>
</head>
<body data-user="<?php echo htmlspecialchars($user ?? ''); ?>">
<h1>JBO 42ft Undergraduate Lab Data</h1>
<p class='helptext'>This is the data access portal for the 42ft telescope 3rd year lab experiment</p>
<h2>Useful Links and Solar System Ephemerdies</h2>
<ul>
  <li><a href='https://github.com/SixByNine/crab_42ft_jbo_templates'>Template codes</a></li>
  <li><strong><a href='2026_ssb.txt'>2026 Solar System Barycentre file</a></strong></li>
</ul>
<h2>Data Request Form</h2>
<?php
if (empty($user)) {
    print "<p class='helptext'>Please enter a user ID. This can be anything but should be unique to your pair of students, e.g. use your initials.</p>";
    print "<form action='index.php' id='requestform'>";
    print "<label for='user'>User ID</label><input type='text' name='user' id='user' placeholder='e.g. initials'><br>";
    print "<input type='submit' value='Ok'>";

} else {
    print ("User ID: '$user' (<a href='index.php'>logout</a>)<br>");
        print "<p class='helptext'>Enter the details of the observation to look up, then you can select files for processing on the next page.</p>";

print "
<form action='find.php' id='requestform'>
<input type='hidden' name='user' value='$user'>
<label for='psr'>PSR</label><input type='text' name='psr' id='psr' placeholder='e.g. B0329+54'><br>
<label for='day'>Date</label><input type='text' name='day' id='day' placeholder='e.g. 20220428'> (YYYYMMDD)<br>
<label for='ut'>Hour</label><input type='text' name='ut' id='ut' placeholder='e.g. 14'> (UTC start of observation, 24h format)<br>
<input type='submit' value='Request data'>
<p>Last heard from server: <span id='atime'>";
echo file_get_contents( "jobs/.atime");
print "</span></p>
</form>";



print " <h2>Data Access</h2>";
print("<p class='helptext'>The table below shows the data you have submitted and the data that has been processed. The 'URL/Status' column will either contain a link to the processed data or a status message.</p>");
    print ("User ID: '$user' (<a href='index.php'>logout</a>)<br>");
    print "<table><thead><tr><th>Day</th><th>Time(UT)</th><th>PSR</th><th>Type</th><th>URL/Status</th></tr></thead><tbody id='data-rows'>";

print render_user_rows($user);

print "</tbody></table>";
}

?>


</body>
</html>
