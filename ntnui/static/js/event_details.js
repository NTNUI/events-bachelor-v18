/**
 * When the document have loaded, add listener to attend-event-button and send ajax.
 */
$(() => {

    $(".join-subevent-button").click( () => {
        const csrftoken = getCookie('csrftoken');
        const button = event.target
        if(button.value[0] === "-") {
            button.value = button.value.substring(1,)
            removeAttendSubEvent(button, csrftoken)
        }else {
            attendSubEvent(button, csrftoken)
        }
    })

    function attendSubEvent(button, csrftoken) {
        $.ajax({
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken,
                id: button.value
            },
            url: '/ajax/events/attend-sub-event',
            success: (data) => {
                button.innerHTML = "Meld meg av"
                button.setAttribute("class", "btn btn-danger")

            }, error: (data) => {
                printMessage('Error', data.responseJSON.message)
                slideUpAlert()
            }
        })
    }

    function removeAttendSubEvent(button, csrftoken) {
        $.ajax({
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken,
                id: button.value
            },
            url: '/ajax/events/remove-attend-sub-event',
            success: (data) => {
                button.innerHTML = "Meld meg på"
                button.value = "-"+button.value
                button.setAttribute("class", "btn btn-success")

            }, error: (data) => {
                printMessage('Error', data.responseJSON.message)
                slideUpAlert()
            }
        })
    }


    $("#attend-event-button").click(() => {
        const csrftoken = getCookie('csrftoken');
        const pathArray = window.location.pathname.split( '/' );
        const id = pathArray[3]
        $.ajax({
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken,
                id:id
            },
            url: '/ajax/events/attend-event',
            success: data => {
                button  = $("#attend-event-button")
                button.html( () => "Meld meg av")
                 $("#attend-event-button").removeClass("btn-success" )
                $("#attend-event-button").addClass("btn-danger" )
            }, error: data => {
                printMessage('Error', data.responseJSON.message)
                slideUpAlert()
            }
        })
    })
})


// from django website https://docs.djangoproject.com/en/2.0/ref/csrf/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/**
 * Prints message to screen, using a dialog box
 * @param msgType
 * @param msg
 */
function printMessage(msgType, msg) {

    //checks the msgType, to get the right color for the alert
    let type = ''
    switch (msgType){
        case 'Error':
            type = 'danger'
            break
        case 'Success':
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
function slideUpAlert() {

    //set timeout
    setTimeout(() => {
        //slide up the alert
    $(".alert").slideUp()
    //sets the amount of ms before the alert is closed
    }, 2000)
}

