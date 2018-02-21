const URL = "/ajax/events/get-events";
let pageNr;
let pageCount;

// on document ready, send ajax request for the first page
$(() => {
    loadEvents(1);
    $("#load-more").click(() => {
        getNextPage();
    });
});

function getNextPage() {
    if (pageNr < pageCount) {
        pageNr = pageNr + 1;
        loadEvents(pageNr);
    } else {
        removeButton();
    }
}

// ajax for requesting events from server
function loadEvents(page) {
    let searchParams = new URLSearchParams(window.location.search);

    //get parms from url. if they dont exsits set em as blank
    const search = searchParams.has("search") ? searchParams.get("search") : "";
    const orderBy = searchParams.has("order_by")
        ? searchParams.get("order_by")
        : "";

    console.log(orderBy);
    $.ajax({
        dataType: "json",
        url: URL,
        data: {
            page: page,
            search: search,
            order_by: orderBy
        },
        success: data => {
            console.log(data);
            pageNr = parseInt(data.page_number);
            pageCount = data.page_count;
            displayEvents(data.events);
        },
        error: data => {
            displayError(data.message);
        }
    });
}

// for each event dispay event
function displayEvents(events) {
    events.map(event => {
        displayEvent(event);
    });
}

// display one event
function displayEvent(event) {
    $("#event-container").append(
        '<div class="card bg-light mb-3">' +
            '<div class="card-header">' +
            event.host +
            "</div>" +
            '<div class="card-body">' +
            '<h5 class="card-title">' +
            event.name +
            " | " +
            event.start_date.substr(0, 10) +
            "</h5>" +
            '<p class="card-text">' +
            event.description.substr(0, 100) +
            "..." +
            "</p>" +
            "</div>" +
            "</div>"
    );
}

// display error if something went wrong
function displayError(msg) {
    $("#event-container").html("<div>" + msg + "<div/>");
}

function removeButton() {
    $("#load-more").hide();
}
