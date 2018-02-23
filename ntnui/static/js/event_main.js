const GET_URL = "/ajax/events/get-events";
let pageNr;
let pageCount;
let searchParams = new URLSearchParams(window.location.search)

// on document ready, send ajax request for the first page
$(() => {

    $("#search-field").val(searchParams.has("search") ? searchParams.get("search") : "")
    loadEvents(1);

    $("#load-more").click(() => {
        getNextPage();
    });

    $("#search").on('input',() => {

        searchParams.set('search', $("#search-field").val());
        history.replaceState('test', 'test', '?' + searchParams)
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
    console.log(searchParams)
    //get parms from url. if they dont exsits set em as blank
    const search = searchParams.has("search") ? searchParams.get("search") : "";
    const orderBy = searchParams.has("order_by")
        ? searchParams.get("order_by")
        : "";

    console.log(orderBy);
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
            displayEvents(data.events);
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
    priority = false
    if(event.priority == 'True') {
        priority = true
    }

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
