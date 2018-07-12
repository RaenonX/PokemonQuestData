let pot_data = [
    { "id": 0, "name": "鐵鍋", "bonus": 0, "iv": 10 },
    { "id": 1, "name": "銅鍋", "bonus": 50, "iv": 50 },
    { "id": 2, "name": "銀鍋", "bonus": 150, "iv": 100 },
    { "id": 3, "name": "金鍋", "bonus": 300, "iv": 100 }
]

$(document).ready(
    initialize,
    $("#lvSlider").on("input", update_min_max),
    immUpdateVal("#hpValue", "#hpSlider"),
    immUpdateVal("#atkValue", "#atkSlider"),
    immUpdateVal("#lvValue", "#lvSlider"),
    $(".pot-btn").click(function () {
        let ix = $(this).val();
        $("#potId").attr("data-value", ix).text(pot_data[ix].name);
        update_min_max();
        update_ui();
    })
)

function initialize() {
    console.log("init");
    update_min_max();
    update_ui();
}

function immUpdateVal(valId, sliderId) {
    $(sliderId).on("input", function () {
        $(valId).text($(this).val());
        
        update_ui();
    })
}

function update_min_max() {
    let current_pot = pot_data[$("#potId").attr("data-value")]

    let lv = parseInt($("#lvValue").text())

    let hpMin = parseInt($("#baseHp").val()) + lv
    let hpMax = hpMin + current_pot.iv

    $("#hpMin").text(hpMin)
    $("#hpMax").text(hpMax)
    $("#hpValue").text($("#hpSlider").attr("min", hpMin).attr("max", hpMax).val())

    let atkMin = parseInt($("#baseAtk").val()) + lv
    let atkMax = atkMin + current_pot.iv

    $("#atkMin").text(atkMin)
    $("#atkMax").text(atkMax)
    $("#atkValue").text($("#atkSlider").attr("min", atkMin).attr("max", atkMax).val())
}

function update_ui() {
    let current_pot = pot_data[$("#potId").attr("data-value")]
    let hp = parseInt($("#hpValue").text())
    let atk = parseInt($("#atkValue").text())

    $("#hpPct").text(((hp - parseInt($("#hpMin").text())) / current_pot.iv * 100).toFixed())
    $("#atkPct").text(((atk - parseInt($("#atkMin").text())) / current_pot.iv * 100).toFixed())
}