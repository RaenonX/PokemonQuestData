(function ($) {
    var darken_diff = 50;

    $.fn.darken = function (diff = darken_diff) {
        rgb_str = this.css("background-color");

        try {
            rgb = rgb_str.match(/\d+/g);
            var r = Math.max(parseInt(rgb[0]) - diff, 0);
            var g = Math.max(parseInt(rgb[1]) - diff, 0);
            var b = Math.max(parseInt(rgb[2]) - diff, 0);

            $(this).css("background-color", "rgb(" + r + ", " + g + ", " + b + ")");
            if (diff > 0) {
                this.addClass("darkened");
            }
        } catch (TypeError) {
        }

        return this;
    };

    $.fn.recoverDarken = function () {
        this.each(function () {
            if ($(this).hasClass("darkened")) {
                $(this).darken(-darken_diff);
                $(this).removeClass("darkened");
            }
        })
        return this;
    };
}(jQuery));

$(document).ready(
    function () {
        $("#pokeSearch").on("keyup", handle_filter),
            $(".poke-button").hover(
                function () {
                    temp = $(this).css("background-color");
                    $(this).darken();
                },
                function () {
                    $(this).recoverDarken();
                }
            ).click(
                function () {
                    $("#elemClicked").val($(this).val());
                    $(".poke-button-activated").removeClass("poke-button-activated");
                    $(this).addClass("poke-button-activated");
                    handle_filter();
                }
            ),
            $(document).mousedown(
                function (e) {
                    if (e.which === 3) {
                        $("#elemClicked").val(-1);
                        $(".poke-button-activated").removeClass("poke-button-activated");
                        $(".poke-no").addClass("poke-button-activated");
                        handle_filter();
                    }
                }
            )
    }
).contextmenu(function () { return false; });

function handle_filter() {
    $(".poke").filter(function () {
        var value = $("#pokeSearch").val().toLowerCase();
        var elem = $("#elemClicked").val()

        var word = (value == "") || (
            $(this).attr("zh").toLowerCase().indexOf(value) > -1 ||
            $(this).attr("jp").toLowerCase().indexOf(value) > -1 ||
            $(this).attr("en").toLowerCase().indexOf(value) > -1 ||
            $(this).attr("poke_id").indexOf(value) > -1)
        var element = (elem == -1) || ($(this).attr("elem").split(" ").includes(elem))

        if (word && element) {
            $(this).removeClass("hide");
        } else {
            $(this).addClass("hide");
        }
    });
}

function get_darken_rgb_str(rgb_str) {
    var DIFF = 50;

    rgb = rgb_str.match(/\d+/g);
    var r = Math.max(parseInt(rgb[0]) - DIFF, 0);
    var g = Math.max(parseInt(rgb[1]) - DIFF, 0);
    var b = Math.max(parseInt(rgb[2]) - DIFF, 0);

    return "rgb(" + r + ", " + g + ", " + b + ")";
}
