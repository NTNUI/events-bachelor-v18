/**
 * When the document have loaded, add listener to create-event-button and send ajax.
 */
$(() => {
    $("#create-event-button").click(() => {
        const postData = $('#create-event-form').serialize()
        console.log(postData)
        $.ajax({
            type: 'POST',
            url: '/ajax/events/add-event',
            data: postData,
            success: (data) => {
                //show success alert
                printMessage('success', data.message)
                slideUpAlert(true)
            }, error: (data) => {
                //show error alert
                printMessage('error', data.responseJSON.message)
                slideUpAlert(false)
            }
        })
    })
})

/**
 * Prints message to screen, using a dialog box
 * @param msgType
 * @param msg
 */
function printMessage(msgType, msg) {

    //checks the msgType, to get the right color for the alert
    let type = ''
    switch (msgType){
        case 'error':
            type = 'danger'
            break
        case 'success':
            type = 'success'
            break
    }
    //print message to screen
    $(".alert-message-container").html(() => {
        return "<div class=\"alert alert-"+type+" show fade \" role=\"alert\"> <strong>"+ msgType + ":</strong>" +
            " "+ msg +  "</div>"
    })
}

/**
 * Slides up the alert, if redirect set, the user will be returned to last page.
 * @param redirect
 */
function slideUpAlert(redirect) {

    //set timeout
    setTimeout( () => {
        //slide up the alert
    $(".alert").slideUp(500)
    if(redirect){
        window.location.href = '/events'
    }
    //sets the amount of ms before the alert is closed
    }, 1500)
}