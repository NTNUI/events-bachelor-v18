/**
 * When the document have loaded, add listener to attend-event-button and send ajax.
 */
let buttonValue

$(() => {
    let handler = StripeCheckout.configure({
    key: 'pk_test_TagT9jGDj7CN9NOQfTnueTxz',
    image: "/static/img/ntnui2.svg",
    locale: 'auto',
    token: (token) => {
        const csrftoken = getCookie('csrftoken');
        $.ajax({
        dataType: "json",
        type: "POST",
        url: '/ajax/events/' + buttonValue + '/payment',
        data: {
            csrfmiddlewaretoken: csrftoken,
            stripeToken: token.id,
            stripEmail:token.email
        },
        success: (data) => {
            button = $("#attend-event-button")
            printMessage('Success', data.message)
            button.text(gettext("Do not attend event"))
            button.val( '-' + button.val())
            button.attr("class", "btn btn-danger")
            slideUpAlert()
        },
        error: (data) => {
            printMessage('Error', data.message)
            slideUpAlert()
        }
        });
    }
    });


    /**
     * Sends a attend subevet request
     */
    $(".join-subevent-button").click(() => {
        const csrftoken = getCookie('csrftoken');
        const button = event.target

        // IF the first sign is a - we want to remove attending event
        if (button.value[0] === "-") {
            button.value = button.value.substring(1,)
            const URL = '/ajax/events/remove-attend-sub-event'
            removeAttendEvent(button, csrftoken, URL)
        } else {
            const URL = '/ajax/events/attend-sub-event'
            attendEvent(button, csrftoken, URL)
        }
    })

    /**
     * Sends a attend event request to the server
     */
    $("#attend-event-button").click((e) => {

        const csrftoken = getCookie('csrftoken')

        const pathArray = window.location.pathname.split('/');
        const button = event.target

        if (button.value[0] === "-") {
            button.value = button.value.substring(1,)
            let URL = ""
            let buttonText = gettext('attend event')
            if ($("#price").length === 0) {
                URL = '/ajax/events/remove-attend-event'
            } else {
                URL = '/ajax/events/refund'
                buttonText = gettext('Pay using card')
            }
            removeAttendEvent(button, csrftoken, URL, buttonText)
        } else {
            if ($("#price").length === 0) {
                const URL = '/ajax/events/attend-event'
                console.log("here")
                attendEvent(button, csrftoken, URL)
            } else {
                attendPayedEvent(csrftoken, e, button)
            }
        }
})

    function attendEvent(button, csrftoken, URL) {
        $.ajax({
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken,
                id: button.value
            },
            url: URL,
            success: (data) => {
                button.innerHTML = gettext("Do not attend event")
                button.value = '-' + button.value
                button.setAttribute("class", "btn btn-danger")
                printMessage('Success', data.message)
                slideUpAlert()

            }, error: (data) => {
                printMessage('Error', data.message)
                slideUpAlert()
            }
        })
    }

    function attendPayedEvent(csrftoken, e, button) {
        const URL = '/ajax/events/' + button.value
        buttonValue = button.value
        $.ajax({
            dataType: "json",
            url: URL,
            success: event => {
                $.ajax({
                dataType: "json",
                url: '/ajax/accounts',
                success: user => {
                    handler.open({
                    amount: parseInt(event.price)*100,
                    currency: "nok",
                    name: event.host,
                    description: event.name,
                    email: user.email,
                    });

                    e.preventDefault();
                },
                error: data => {
                    printMessage('Error', 'Could not get userinfo')
                    slideUpAlert()
                }
                });
            },
            error: data => {
                printMessage('Error', 'Could not get event info')
                slideUpAlert()
             }
            })
    }

    /**
     * Sends a remove attended request to the server
     * @param button
     * @param csrftoken
     */
    function removeAttendEvent(button, csrftoken, URL, buttonText) {
        $.ajax({
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken,
                id: button.value
            },
            url: URL,
            success: (data) => {
                button.innerHTML = buttonText
                button.setAttribute("class", "btn btn-success")
                printMessage('Success', data.message)
                slideUpAlert()

            }, error: (data) => {
                printMessage('Error', data.message)
                slideUpAlert()
            }
        })
    }


})



// Close Checkout on page navigation:
window.addEventListener('popstate', function () {
    handler.close();
});



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
    switch (msgType) {
        case 'Error':
            type = 'danger'
            break
        case 'Success':
            type = 'success'
            break
    }
    //print message to screen
    $(".alert-message-container").html(() => {
        return "<div class=\"alert alert-" + type + " show fade \" role=\"alert\"> <strong>" + msgType + ":</strong>" +
            " " + msg + "</div>"
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

