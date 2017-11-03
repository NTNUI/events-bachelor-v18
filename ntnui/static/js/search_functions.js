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
}

function memberSearch() {
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
}