$(document).ready(
    sortOnClick("#sortPwr", "pwr"),
    sortOnClick("#sortCd", "cd"),
    sortOnClick("#sortOrg", "id", false)
)

function sortOnClick(btnId, sortKey, HtoL=true) {
    console.log(sortKey);
    $(btnId).click(function () {
        $('.skill-wrapper').sort(function (a, b) {
            let comparison = (parseInt($(b).data(sortKey)) - parseInt($(a).data(sortKey)));

            if (comparison == 0) {
                return (parseInt($(a).data("id") - parseInt($(b).data("id"))))
            }

            return comparison * (HtoL ? 1 : -1);
        }).appendTo('.skills-container');
    });
}