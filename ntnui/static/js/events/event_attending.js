const GET_URL = "/ajax/events/get-attending-events";
let pageNr;
let pageCount;
let searchParams = new URLSearchParams(window.location.search);


// on document ready, send ajax request for the first page
$(() => {

    // Sets the search filed to the same search that is in the url
    $("#search-field").val(searchParams.has("search") ? searchParams.get("search") : "")

    // Sets the sort by filed to the same sort by that is in the url
    $("#sorted-list").val(searchParams.has("sort-by") ? searchParams.get("sort-by") : "start_date")

    $("#sorted-list").val() != null && !searchParams.has("sort-by") ? history.replaceState('test', 'test', '?sort-by=' + $("#sorted-list").val() ): ""
    const hostedBy = searchParams.has("filter-host") ? searchParams.get("filter-host") : ""
    const hostedBy_list = hostedBy.split("-")


    $(".host-checkbox").each( (i, checkbox) => {
        if(hostedBy_list.includes(checkbox.value)){
            checkbox.checked = true
            }
        })

    // Load the first page
    loadEvents(1);

    // On click
    $("#load-more").click(() => {
        getNextPage();
    });


    $(".host-checkbox").change( () => {
        let filterHost = []
        $(".host-checkbox").each( (i, checkbox) => {
            if(checkbox.checked){
                filterHost.push(checkbox.value)
        }
        })
        // update parms
        let updateString = filterHost.join("-")
        searchParams.set('filter-host', updateString)
        //update current url
        history.replaceState({}, 'filter', '?' + searchParams)
        // Load events
        loadEvents(1)
    })

    // on change in the search field
    $("#search").on('input',() => {

        // update parms
        searchParams.set('search', $("#search-field").val());
        //update current url
        history.replaceState({}, 'search', '?' + searchParams)
        // Load events
        loadEvents(1)
    })

    $("#sorted-list").on('change', () => {
        // update parms
        searchParams.set('sort-by', $("#sorted-list").val())
        //update current url

        history.replaceState({}, 'sort-by', '?' + searchParams)
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
    const sortBy = searchParams.has("sort-by") ? searchParams.get("sort-by") : "";
    const filterHost = searchParams.has("filter-host") ? searchParams.get("filter-host") : "";


    $.ajax({
        dataType: "json",
        url: GET_URL,
        data: {
            'page': page,
            'search': search,
            'sort-by': sortBy,
            'filter-host': filterHost
        },
        success: data => {
            pageNr = parseInt(data.page_number);
            pageCount = data.page_count;
            displayEvents(data.events, page===1);
            if (pageNr === pageCount) {
                removeButton();
            }else {
                showButton();
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

    if(events.length > 0) {
        events.map(event => {
            displayEvent(event);
    });
    }else {
        $("#event-container").html(
            '<div style="text-align: center"><i>' + gettext('No more events to display!') + '</i></div>'
        )
    }

}

// display one event
function displayEvent(event) {

    let start_date = new Date(event.start_date)
    let printeble_date = start_date.getDate() + "." + ((start_date.getMonth())+1) + "." + start_date.getFullYear()
    let hosts = event.host


    $("#event-container").append(
        '<a href="/events/' + event.id + '/' + event.name.replace(/\s+/g, '-').toLowerCase() + '"><div class="card-body card-body-container">' +
        '<div class=" card bg-light mb-3" >' +
            '<div class="card-element card-header"> <h5>' +
                event.name +
            "</h5> </div>" +
            '<div class="card-element card-body">' +
            '<div class="card-element-container">' +
                '<h6 class="card-title">' +
                     event.description.substr(0, 100) + (event.description.length > 100 ? '...' : '') +
                    ' </h6>' +
                    '<b>' + gettext('Place') + ': ' + '</b>' + event.place + '</br>' +
                    '<b>' + gettext('Date') +': ' + '</b> ' + printeble_date +
                '</br> <p> <b> ' + gettext('Hosted by ') + ': ' + '</b> ' +
                    hosts +
                "</p>" +
                "</div>" +
            "</div>" +
        "</div></a>"
    );
}

// display error if something went wrong
function displayError(msg) {
    $("#event-container").html("<div>" + msg + "<div/>");
}

function removeButton() {
    $("#load-more").hide();
}
function showButton() {
    $("#load-more").show();
}
