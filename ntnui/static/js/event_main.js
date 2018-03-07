const GET_URL = "/ajax/events/get-events";
let pageNr;
let pageCount;
let searchParams = new URLSearchParams(window.location.search)


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
            console.log("here")
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
        let updateString = filterHost.join()
        updateString = updateString.replace(",", "-")
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

    let start_date = new Date(event.start_date)
    let printeble_date = start_date.getDate() + "." + ((start_date.getMonth())+1) + "." + start_date.getFullYear()
    let hosts = event.host
    console.log(printeble_date)

    $("#event-container").append(
      '<a href="/events/' + event.id + '/' + event.name.replace(/\s+/g, '-').toLowerCase() + '"><div class="card-body">' +
        '<div class="card bg-light mb-3" >' +
            '<div class="card-element card-header">' +
                event.name +
            "</div>" +
            '<div class="card-element card-body">' +
            '<div class="card-element-container">' +
                '<h6 class="card-title">' +
                     event.description.substr(0, 100) + (event.description.length > 100 ? '...' : '') +
                    ' </h6>' +
                    '<b>Sted</b>: Gløshaugen </br>' +
                    '<b> Dato: </b>' + printeble_date +
                '</br> <p class="card-text"> <b>Arrangert av: </b> ' +
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
