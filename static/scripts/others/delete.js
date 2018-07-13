$(document).ready(
    $(".del-icon").click(function () {
        if (confirm("確定要刪除這筆資料嗎？")) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', Flask.url_for('frontend.delete_record_user'));
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
    })
)