const GET_URL = "/ajax/events/get-events";
let pageNr;
let pageCount;
let searchParams = new URLSearchParams(window.location.search)

// on document ready, send ajax request for the first page
$(() => {

    // Sets the search filed to the same search that is in the url
    $("#search-field").val(searchParams.has("search") ? searchParams.get("search") : "")

    // Load the first page
    loadEvents(1);

    // On click
    $("#load-more").click(() => {
        getNextPage();
    });

    // on change in the search field
    $("#search").on('input',() => {

        // update parms
        searchParams.set('search', $("#search-field").val());
        //update current url
        history.replaceState('test', 'test', '?' + searchParams)
        // Load events
        loadEvents(1)

    })
});

function getNextPage() {
    if (pageNr < pageCount) {
        pageNr = pageNr + 1;
        loadEvents(pageNr);
    }
}

// ajax for requesting events from server
function loadEvents(page) {
    //get parms from url. if they dont exsits set em as blank
    const search = searchParams.has("search") ? searchParams.get("search") : "";
    const orderBy = searchParams.has("order_by") ? searchParams.get("order_by") : "";

    $.ajax({
        dataType: "json",
        url: GET_URL,
        data: {
            page: page,
            search: search,
            order_by: orderBy
        },
        success: data => {
            console.log(data);
            pageNr = parseInt(data.page_number);
            pageCount = data.page_count;
            displayEvents(data.events, page==1);
            if (pageNr === pageCount) {
                removeButton();
            }
        },
        error: data => {
            console.log(data.message);
        }
    });
}

// for each event dispay event
function displayEvents(events, reload) {
    if(reload) {
        $("#event-container").empty()
    }

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
            '<a href=""><div class="card-body">' +
            '<h5 class="card-title">' +
            event.name +
            " | " +
            event.start_date.substr(0, 10) +
            "</h5>" +
            '<p class="card-text">' +
            event.description.substr(0, 100) +
            "..." +
            "</p>" +
            "</div></a>" +
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
