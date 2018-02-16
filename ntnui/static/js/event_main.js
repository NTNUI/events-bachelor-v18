const URL = '/ajax/events/get-events'
let pageNr
let pageCount

// on document ready, send ajax request for the first page
$( () => {
    loadEvents(1)
})


// ajax for requesting events from server
function loadEvents(page) {
    $.ajax({
      dataType: "json",
      url: URL,
      data: {page: page},
      success: (data) => {
          console.log(data)
          pageNr = data.page_nr
          pageCount = data.page_count
          displayEvents(data.events)
      },
      error: (data) => {
          displayError(data.message)
      }
    })
}

// for each event dispay event
function displayEvents(events) {
    events.map((event) => {
        displayEvent(event)
    })
}

// display one event
function displayEvent(event) {
    $('#event-container').append(
        "<div>" + event.name + "<div/>"
    )
}

// display error if something went wrong
function displayError(msg) {
    $('#event-container').html(
        "<div>" + msg + "<div/>"
    )
}

