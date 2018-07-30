$(document).ready(
    $("#submitPokemon").submit(handleFormSubmit),
    $(".poke-list").change(handlePokeListChange),
    $(".bingoList").change(function () {
        handleListChange($(this), "bingo");
    }),
    $(".skillList").change(function () {
        handleListChange($(this), "skill");
    }),
    $("#hasMore").click(function () {
        $(this).toggleClass("active");
        $("input[name=submitMore]").val($(this).hasClass("active") ? "TRUE" : "FALSE");
    })
).keypress(function (e) {
    if (e.which == 13) {
        let form = $("#submitPokemon");

        form.validate();
        if (form.valid()) {
            form.submit();
        }
    }
});

function handlePokeListChange() {
    let id = $(this).find("option:selected").data("tokens").split("|")[0];

    $(".bingoList").find("option").remove().end().attr("disabled", "").selectpicker("refresh");
    $(".skillList").find("option").remove().end().attr("disabled", "").selectpicker("refresh");
    $(".param").attr("disabled", "");

    $("#entry-group").find("poke-field, .bingo-field, .skill-field").val(-1);
    $("input[name=pokename]").val("").attr("disabled", "");
    if (id > 0) {
        $.getJSON(Flask.url_for("api.get_data_for_add_poke", { "id": id }), function (json) {
            bingoLoadedCallback(json["bingo"]);
            skillLoadedCallback(json["skill"]);
            paramLoadedCallback(json["param"]);
            $(".param").removeAttr("disabled");
            $("input[name=pokename]").val(json["name"]).removeAttr("disabled");
        });
    }

    $("#entry-group > .poke-field").val(id);
}

function handleFormSubmit() {
    let failed = false;
    let slotSum = 0;

    if ($(".poke-field").val() == -1) {
        $(".poke-field").addClass("incomplete-field");
        failed = true;
    }

    $("input[name^=slot]").each(function () {
        let slotCount = parseInt($(this).val());
        slotSum += isNaN(slotCount) ? 0 : slotCount;
    });
    if (!(slotSum == 9 || slotSum == 0)) {
        failed = true;
        $("#slotSumIncorrect").removeClass("hide");
    }

    if (failed) {
        $(window).scrollTop(0);
        $("#incomplete").removeClass("hide");
    }

    return !failed;
}

function handleListChange(obj, category) {
    let id = obj.find("option:selected").data("tokens");
    
    let _name = obj.attr("id");
    let idx = _name.substr(_name.length - 1);
    
    $("input[name=" + category + idx + "]").val(id);
}

function bingoLoadedCallback(json) {
    let bingo1_list = json.slice(0, 3);
    let bingo2_list = json.slice(3, 6);
    let bingo3_list = json.slice(6, 9);

    $("select[id^='bingoList']").each(function () {
        $(this).find("option").remove().end().removeAttr("disabled");
    })

    for (i = 1; i <= 3; i++) {
        json.slice((i - 1) * 3, i * 3).forEach(function (entry, idx) {
            if (idx == 0) { $("input[name=bingo" + i + "]").val(entry[0]); }

            $("#bingoList" + i).append($("<option>", {
                "data-tokens": entry[0],
                "text": entry[1]
            })).selectpicker("refresh");
        });
    }
}

function skillLoadedCallback(json) {
    $("select[id^='skillList']").each(function () {
        $(this).find("option").remove().end().removeAttr("disabled");
    })

    $("#skillList2").append($("<option>", {
        "data-tokens": -1,
        "text": "- 無 -"
    }));
    json.forEach(function (entry, idx) {
        if (idx == 0) { $("input[name=skill1]").val(entry[0]); }

        $("select[id^='skillList']").each(function () {
            $(this).append($("<option>", {
                "data-tokens": entry[0],
                "text": "(" + entry[1] + ") " + entry[2]
            })).selectpicker("refresh");
        });
    });
}

function paramLoadedCallback(json) {
    $("input[name=hp]").attr("min", json.min.hp).attr("max", json.max.hp).removeAttr("disabled");
    $("input[name=atk").attr("min", json.min.atk).attr("max", json.max.atk).removeAttr("disabled");
    $("input[name=lv]").removeAttr("disabled");
}