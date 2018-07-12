$(document).keypress(function (e) {
    if (e.which == 13) {
        $("#resultForm").submit();
    }
});

$(document).ready(
    search_list_events(".poke", "#pokeSelected", "#pokeSearch", "#pokeList button"),
    search_list_events(".rcp", "#rcpSelected", "#rcpSearch", "#rcpList button"),
    search_list_events(".qlt", "#qltSelected", "#qltSearch", "#qltList button"),
    $("#resultForm").submit(function () {
        var pokeMissing = $("#pokeSelected").val() === ""
        if (pokeMissing) {
            $("#PokeMissing").removeClass("hide")
            $("#PokeMissing").fadeIn()
        } else {
            $("#PokeMissing").fadeOut()
        }

        var rcpMissing = $("#rcpSelected").val() === ""
        if (rcpMissing) {
            $("#RcpMissing").removeClass("hide")
            $("#RcpMissing").fadeIn()
        } else {
            $("#RcpMissing").fadeOut()
        }

        var qltMissing = $("#qltSelected").val() === ""
        if (qltMissing) {
            $("#QltMissing").removeClass("hide")
            $("#QltMissing").fadeIn()
        } else {
            $("#QltMissing").fadeOut()
        }

        result = pokeMissing || rcpMissing || qltMissing

        if (result) {
            $(window).scrollTop(0);
        }

        return !result
    })
);

function search_list_events(btn_id, indicator_id, query_id, list_id) {
    $(query_id).on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $(list_id).filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
    $(btn_id).click(function () {
        $(btn_id).removeClass("active");
        $(this).addClass("active");
        $(indicator_id).val($(this).val());
    });
};
