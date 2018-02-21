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
    $.ajax({
        dataType: "json",
        url: URL,
        data: { page: page },
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
        "<div>" + event.name + ": " + event.start_date + "<div/>"
    );
}

// display error if something went wrong
function displayError(msg) {
    $("#event-container").html("<div>" + msg + "<div/>");
}

function removeButton() {
    $("#load-more").hide();
}
