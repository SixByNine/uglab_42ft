<?php
header("Content-Type: application/json");
require_once "row_helper.php";

$user = "";
if (array_key_exists("user", $_GET)) {
    $user = preg_replace('/[\W]/', '_', $_GET['user']);
}

$atime = trim(file_get_contents("jobs/.atime"));
$rows = render_user_rows($user);

echo json_encode(["atime" => $atime, "rows" => $rows]);

