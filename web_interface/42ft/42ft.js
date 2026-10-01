function refreshStatus() {
    var user = document.body.dataset.user;
    if (!user) {
        return;
    }
    fetch("status.php?user=" + encodeURIComponent(user))
        .then(function (r) { return r.json(); })
        .then(function (d) {
            document.getElementById("atime").textContent = d.atime;
            document.getElementById("data-rows").innerHTML = d.rows;
        });
}

document.addEventListener("DOMContentLoaded", function () {
    if (document.body.dataset.user) {
        setInterval(refreshStatus, 5000);
    }
});
