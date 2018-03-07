/**
 * When the document have loaded, add listener to attend-event-button and send ajax.
 */
$(() => {
    $("#attend-event-button").click(() => {
        $.ajax({
            type: 'POST',
            url: '/ajax/events/attend-event',
            success: (data) => {

            }, error: (data) => {

            }
        })
    })
})