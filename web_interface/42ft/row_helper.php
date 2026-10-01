<?php
// Shared row-generation logic for index.php and status.php.

function render_user_rows($user) {
    $rows = "";
    if (empty($user) || !is_dir("users/$user")) {
        return $rows;
    }

    $files = scandir("users/$user");
    foreach ($files as $fl) {
        if (substr($fl, 0, 1) == ".") {
            continue;
        }

        // a job file still present means it's queued/being processed
        if (file_exists("jobs/$fl")) {
            $f = fopen("jobs/$fl", "r");
            $line = fgets($f);
            fclose($f);
            $e = explode(" ", $line, 4);
            $rows .= "<tr class='submitted'>";
            $rows .= "<td>$e[0]</td><td>$e[1]</td><td>$e[2]</td><td>-</td><td>$e[3]</td>";
            $rows .= "</tr>\n";
            continue;
        }

        $f = fopen("users/$user/$fl", "r");
        $line = fgets($f);
        fclose($f);
        $e = explode(" ", $line, 3);
        $day = $e[0];
        $ut = $e[1];
        $psr = trim($e[2]);
        $reprocess_link = "launch.php?user=" . urlencode($user) . "&day=" . urlencode($day)
            . "&ut=" . urlencode($ut) . "&psr=" . urlencode($psr);
        $reprocess_link_html = "<a class='reprocess' href='$reprocess_link' title='Request re-processing'>&#8635; reprocess</a>";

        if (file_exists("data/$fl.npz")) {
            $type_label = "Unknown";
            $show_reprocess = true;
            if (file_exists("data/$fl.type")) {
                $type = trim(file_get_contents("data/$fl.type"));
                if ($type == "clean") {
                    $type_label = "Cleaned";
                    $show_reprocess = false;
                } else if ($type == "auto_clean") {
                    $type_label = "Auto-cleaned";
                } else if ($type == "raw") {
                    $type_label = "Raw";
                }
            }
            $rows .= "<tr class='data'>";
            $rows .= "<td>$day</td><td>$ut</td><td>$psr</td><td>$type_label</td>";
            $rows .= "<td><a href='data/$fl.npz'>$fl.npz</a>";
            if ($show_reprocess) {
                $rows .= " $reprocess_link_html";
            }
            $rows .= "</td></tr>\n";
        } else if (file_exists("data/$fl.failed")) {
            $rows .= "<tr class='failed'>";
            $rows .= "<td>$day</td><td>$ut</td><td>$psr</td><td>-</td>";
            $rows .= "<td>Processing failed $reprocess_link_html</td>";
            $rows .= "</tr>\n";
        } else {
            $rows .= "<tr class='submitted'>";
            $rows .= "<td>$day</td><td>$ut</td><td>$psr</td><td>-</td><td>Error -- Lost?</td>";
            $rows .= "</tr>\n";
        }
    }

    return $rows;
}
