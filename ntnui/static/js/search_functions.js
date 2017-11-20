/*
# This function can be used if only titles are to be searched!
function groupSearch() {
    let input = document.getElementById("group-search");
    let filter = input.value.toLowerCase();
    let allGroups = document.getElementById("all-groups");
    let groupCards = allGroups.getElementsByClassName("group-card");
    let cardInfos = allGroups.getElementsByClassName("group-card-info");

    for (let i = 0; i < groupCards.length; i++) {
        let title = cardInfos[i].getElementsByTagName("h2")[0];

        if (title) {
            if (title.innerHTML.toLowerCase().indexOf(filter) > -1) {
                groupCards[i].style.display = "";
            } else {
                groupCards[i].style.display = "none";
            }
        }
    }
}*/

let $groupRows = $('#all-groups').find('.group-card-all-groups');
$('#group-search').keyup(function () {
    let val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();

    $groupRows.show().filter(function () {
        let text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        return !~text.indexOf(val);
    }).hide();
});

let $memberRows = $('.group-table-row');
$('#member-search').keyup(function () {
    let val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();

    $memberRows.show().filter(function () {
        let text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        return !~text.indexOf(val);
    }).hide();
});

