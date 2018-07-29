$(document).ready(
    $("#pokeList1").change(handlePokeListChange),
    $(".bingoList1").change(function () {
        handleListChange("bingo");
    }),
    $(".skillList1").change(function () {
        handleListChange("skill");
    }),
    $("#addBlock").click(handleAddBlockClick),
    $("#delBlock").click(handleDelBlockClick),
    $("#submitPokemon").submit(handleFormSubmit)
)

function handleAddBlockClick() {
    let new_count = parseInt($("#count").val()) + 1;
    let clone = $("#entry-group").clone();
    
    clone.attr("data-index", new_count);
    clone.find("#pokeField").attr("name", "pokemon" + new_count);
    clone.find("#pokename").attr("name", "pokename" + new_count);
    for (i = 1; i <= 3; i++) {
        clone.find("#bingoField" + i).attr("name", "bingo" + i + "_" + new_count);
    }
    for (i = 1; i <= 2; i++) {
        clone.find("#skillField" + i).attr("name", "skill" + i + "_" + new_count);
    }
    clone.find(".bingoList, .skillList").data("group", new_count);
    clone.find("#hp").attr("name", "hp" + new_count);
    clone.find("#atk").attr("name", "atk" + new_count);
    clone.find("#lv").attr("name", "lv" + new_count);
    clone.find("#slotHp").attr("name", "slotHp" + new_count);
    clone.find("#slotAtk").attr("name", "slotAtk" + new_count);
    clone.find("#slotDuo").attr("name", "slotDuo" + new_count);

    clone.appendTo("#entry-area");

    $("#count").val(new_count);

    updateDelBlockButton();
}

function handleDelBlockClick() {
    let org_val = $("#count").val();

    $("#entry-group[data-index='" + org_val + "']").remove();
    $("#count").val(org_val - 1);

    updateDelBlockButton();
}

function updateDelBlockButton() {
    $("#delBlock").toggleClass("hide", $("#count").val() <= 1)
}

function handlePokeListChange() {
    let groupId = getGroupId($(this).attr("id"))
    let id = $(this).find("option:selected").data("tokens");

    if (id > 0) {
        $.getJSON(Flask.url_for("api.get_pokemon_bingos", { "id": id }), function (json) {
            bingoLoadedCallback(json, groupId);
        }); 
        $.getJSON(Flask.url_for("api.get_pokemon_skills", { "id": id }), function (json) {
            skillLoadedCallback(json, groupId);
        });
        $.getJSON(Flask.url_for("api.get_pokemon_params", { "id": id }), function (json) {
            paramLoadedCallback(json, groupId);
        });
        $.getJSON(Flask.url_for("api.get_pokemon_name_zh", { "id": id }), function (json) {
            $("input[name=pokename" + groupId + "]").val(json).removeAttr("disabled");
        });
    } else {
        $("select[id^='bingoList" + groupId + "']").find("option").remove().end().attr("disabled", "").selectpicker("refresh");
        $("select[id^='skillList" + groupId + "']").find("option").remove().end().attr("disabled", "").selectpicker("refresh");
        $(".param").attr("disabled", "");

        $("#entry-group[data-index=" + groupId + "] > (.poke-field, .bingo-field, .skill-field)" + groupId).val(-1);
        $("input[name=pokename" + groupId + "]").val("").attr("disabled", "");
    }

    $("#entry-group[data-index=" + groupId + "] > .poke-field").val(id);
}

function handleFormSubmit() {
    let failed = false;
    let slotSum = 0;

    $(".poke-field, .bingo-field, #skillField1").each(function () {
        if ($(this).val() == -1) {
            $(this).addClass("incomplete-field");
            failed = true;
        }
    });

    $("input[id^=slot]").each(function () {
        let slotCount = parseInt($(this).val());
        slotSum += isNaN(slotCount) ? 0 : 9;
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

function handleListChange(category) {
    let idx = $(this).find("option:selected").data("tokens");
    let groupId = $(this).data("group");
    
    $("#entry-group[data-index=" + groupId + "] > #" + category + "Field" + getGroupId($(this).attr("id"))).val(idx);
}

function bingoLoadedCallback(json, groupId) {
    let bingo1_list = json.slice(0, 3);
    let bingo2_list = json.slice(3, 6);
    let bingo3_list = json.slice(6, 9);

    $("select[id^='bingoList'][data-group=" + groupId + "]").each(function () {
        $(this).find("option").remove().end().removeAttr("disabled");
    })

    for (i = 1; i <= 3; i++) {
        json.slice((i - 1) * 3, i * 3).forEach(function (entry, idx) {
            if (idx == 0) { $("input[name=bingo" + i + "_" + groupId + "]").val(entry[0]); }

            $("#bingoList" + i + "[data-group=" + groupId + "]").append($("<option>", {
                "data-tokens": entry[0],
                "text": entry[1]
            })).selectpicker("refresh");
        });
    }
}

function skillLoadedCallback(json, groupId) {
    $("select[id^='skillList'][data-group=" + groupId + "]").each(function () {
        $(this).find("option").remove().end().removeAttr("disabled");
    })

    $("#skillList2[data-group=" + groupId + "]").append($("<option>", {
        "data-tokens": -1,
        "text": "- 無 -"
    }));
    json.forEach(function (entry, idx) {
        if (idx == 0) { $("input[name=skill1_" + groupId + "]").val(entry[0]); }

        $("select[id^='skillList'][data-group=" + groupId + "]").each(function () {
            $(this).append($("<option>", {
                "data-tokens": entry[0],
                "text": "(" + entry[1] + ") " + entry[2]
            })).selectpicker("refresh");
        });
    });
}

function paramLoadedCallback(json, groupId) {
    $("input[name=hp" + groupId + "]").attr("min", json.min.hp).attr("max", json.max.hp).removeAttr("disabled");
    $("input[name=atk" + groupId + "]").attr("min", json.min.atk).attr("max", json.max.atk).removeAttr("disabled");
    $("input[name=lv" + groupId + "]").removeAttr("disabled");
}

function getGroupId(txt) {
    return txt.substr(txt.length - 1);
}