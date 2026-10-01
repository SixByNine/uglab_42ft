<?php
header("Content-Type: application/json");

$user = "";
if (array_key_exists("user", $_GET)) {
    $user = preg_replace('/[\W]/', '_', $_GET['user']);
}

$atime = trim(file_get_contents("jobs/.atime"));
$rows = "";

if (!empty($user) && is_dir("users/$user")) {
    $root = "http://psrweb.jb.man.ac.uk/lab/42ft";
    $files = scandir("users/$user");
    foreach ($files as $fl) {
        if (substr($fl, 0, 1) == ".") {
            continue;
        }

        if (file_exists("data/$fl.npz")) {
            $d = "$fl.npz";
            $day = substr($d, 0, 8);
            $time = substr($d, 9, 6);
            $psr = substr($d, 16, strpos($d, ".") - 16);

            $rows .= "<tr class='data'>";
            $rows .= "<td>$day</td>";
            $rows .= "<td>$time</td>";
            $rows .= "<td>$psr</td>";
            $rows .= "<td><a href='data/$d'>$d</a></td>";
            $rows .= "</tr>\n";
        } else if (file_exists("jobs/$fl")) {
            $job = $fl;
            $f = fopen("jobs/$job", "r");
            $line = fgets($f);
            $e = explode(" ", $line, 4);
            $rows .= "<tr class='submitted'>";
            $rows .= "<td>$e[0]</td>";
            $rows .= "<td>$e[1]</td>";
            $rows .= "<td>$e[2]</td>";
            $rows .= "<td>$e[3]</td>";
            $rows .= "</tr>\n";
            fclose($f);
        } else {
            $f = fopen("users/$user/$fl", "r");
            $line = fgets($f);
            $e = explode(" ", $line, 3);
            $rows .= "<tr class='submitted'>";
            $rows .= "<td>$e[0]</td>";
            $rows .= "<td>$e[1]</td>";
            $rows .= "<td>$e[2]</td>";
            $rows .= "<td>Error -- Lost?</td>";
            $rows .= "</tr>\n";
            fclose($f);
        }
    }
}

echo json_encode(["atime" => $atime, "rows" => $rows]);
