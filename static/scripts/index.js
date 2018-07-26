$(document).ready(
    $("#insiteSearch").on("keyup",
        function () {
            $("#insiteBtn").attr("href", Flask.url_for('frontend.insite_search', { "q": $("#insiteSearch").val() }))
        }
    )
).keypress(function (e) {
    if (e.which == 13) {
        window.open($("#insiteBtn").attr('href'))
    }
});