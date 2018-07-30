// TODO: Submit result -> Preload data

$(document).ready(
    function () {
        $('#myPokemon').DataTable({
            "columnDefs": [
                {
                    "targets": [2, 7],
                    "visible": false
                }
            ]
        });
    },
    $(".clickable-row").click(function () {
        window.location = $(this).data("href");
    }),
    $(".del-icon").click(handleDeleteRecord)
);

function handleDeleteRecord() {
    if (confirm("確定要刪除這筆資料嗎？")) {
        let xhr = new XMLHttpRequest();
        xhr.open('POST', Flask.url_for('frontend_user.delete_owned_pokemon'));
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send('dataId=' + $(this).attr("data-id"));
        xhr.onload = function () {
            if (xhr.responseText === "PASS") {
                window.location.reload();
                $(window).scrollTop(0);
            } else {
                $("#msg").removeClass("hide").text(" " + xhr.responseText);
            }
        }
    }
}