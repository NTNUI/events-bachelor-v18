// defines variables that will be used
let buttonValue
let button
let csrftoken
let url
let buttonText
let modalType

// used for guest users
let isGuestUser = false;
let email, firstName, lastName, phone

/**
 * When the document have loaded, add listener to attend-event-button and send ajax.
 */
$(() => {
        if ($('#guestUserModal').length) {
            isGuestUser = true;
        }

        csrftoken = getCookie('csrftoken')

        /**
         * Configure stripe
         */
        let handler = StripeCheckout.configure({
            key: 'pk_test_TagT9jGDj7CN9NOQfTnueTxz',
            image: "/static/img/ntnui2.svg",
            locale: 'auto',
            token: (token) => {
                processStripeToken(token);
            }
        });

        function processStripeToken(token) {
            if (isGuestUser) {
                $.ajax({
                    dataType: "json",
                    type: "POST",
                    url: '/ajax/events/' + buttonValue + 'attend_payment_event_guest',
                    data: {
                        csrfmiddlewaretoken: csrftoken,
                        stripeToken: token.id,
                        id: buttonValue,
                        stripEmail: token.email,
                        first_name: firstName,
                        last_name: lastName,
                        phone: phone,
                    },
                    success: (data) => {
                        button.innerHTML = gettext("Do not attend event")
                        button.value = '-' + button.value
                        button.setAttribute("class", "btn btn-danger")
                        printMessage('Success', data.message)
                        slideUpAlert()
                    },
                    error: (data) => {
                        printMessage('Error', data.responseJSON.message)
                        slideUpAlert()
                    }
                });

            }
            $.ajax({
                dataType: "json",
                type: "POST",
                url: '/ajax/events/' + buttonValue + '/attend_payment_event_user',
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    stripeToken: token.id,
                    stripEmail: token.email
                },
                success: (data) => {
                    button.innerHTML = gettext("Do not attend event")
                    button.value = '-' + button.value
                    button.setAttribute("class", "btn btn-danger")
                    printMessage('Success', data.message)
                    slideUpAlert()
                },
                error: (data) => {
                    printMessage('Error', data.responseJSON.message)
                    slideUpAlert()
                }
            });
        }


        /**
         * Sends a attend subevet request
         */
        $(".join-subevent-button").click((e) => {
            const event = e || window.event
            button = event.target
            // IF the first sign is a - we want to remove attending event
            if (button.value[0] === "-") {
                url = '/ajax/events/remove-attend-sub-event'
                buttonText = gettext('attend event')
                openModal("removeAttendanceSubEvent")
            } else {
                url = '/ajax/events/attend-sub-event'
                attendEvent()
            }
        })
        /**
         * Sends a attend event request to the server
         */
        $("#attend-event-button").click((e) => {
            const event = e || window.event
            button = event.target
            buttonValue = button.value
            if (button.value[0] === "-") {
                buttonText = gettext('attend event')
                if ($("#price").length === 0) {
                    url = '/ajax/events/remove_attendance_event_user'
                } else {
                    url = '/ajax/events/refund_event'
                    buttonText = gettext('Pay using card')
                }
                openModal("removeAttendanceEvent")
            } else {
                if (isGuestUser) {
                    showGuestModal();
                } else {
                    if ($("#price").length === 0) {
                        url = '/ajax/events/attend-event-user'
                        attendEvent()
                    } else {
                        attendPayedEvent(e)
                    }
                }
            }
        })


        $("#guest-data-form").on('submit', (e) => {
            firstName = $("#first-name").val()
            lastName = $("#last-name").val()
            phone = $("#phone").val()
            email = $("#input-email").val()
            if ($("#price").length > 0) {
                $.ajax({
                    dataType: "json",
                    url: '/ajax/events/' + button.value,
                    success: event => {
                        handler.open({
                            amount: parseInt(event.price) * 100,
                            currency: "nok",
                            name: event.host,
                            description: event.name,
                            email: email,
                        });

                        e.preventDefault();
                    },
                    error: data => {
                        printMessage('Error', gettext('Could not get userinfo'))
                        slideUpAlert()
                    }
                });
            } else {
                let postData = $("#guest-data-form").serialize();
                postData = postData + '&csrfmiddlewaretoken=' + csrftoken;
                postData = postData + '&id=' + buttonValue;
                $.ajax({
                    type: 'POST',
                    url: '/ajax/events/attend-event-guest',
                    data: postData,
                    success: (data) => {
                        printMessage('success', data.message)
                        slideUpAlert(true)
                        hideGuestModal()
                    },
                    error:
                        (data) => {
                            printMessage('error', data.responseJSON.message)
                            slideUpAlert(false)
                        }
                })
            }

            e.preventDefault();
        })


        $("#show-confirm-delete-div-button").click(() => {
            openModal("deleteEvent");
        });

        function openModal(type) {
            $("#modal-content").hide();
            if (type === "removeAttendanceEvent") {
                $("#modal-content").text("Are you sure you wanna unattand this event?")
                $("#modal-content").show();
                modalType = "removeEventAttendance";
            } else if (type === "removeAttendanceSubEvent") {
                $("#modal-content").text("Are you sure you wanna unattand this subevent?")
                $("#modal-content").show();
                modalType = "removeEventAttendance";
            } else if (type === "deleteEvent") {
                $("#modal-content").text("Are you sure you wanna delete this event, " +
                    "if this is a payed event all attendees will be refunded ?")
                $("#modal-content").show();
                modalType = "deleteEvent";
            }
            $("#deleteModal").modal("show");
        }


        function showGuestModal() {
            $("#guestUserModal").modal('show')
        }

        function hideGuestModal() {
            $("#guestUserModal").modal('hide')
        }

        $("#remove-attend-event-button").click(() => {
            if (modalType === "removeEventAttendance") {
                removeAttendEvent()
            } else if (modalType === "deleteEvent") {
                // Get eventID, if event id contains - remove it
                eventID = $("#attend-event-button").val()
                eventID = eventID.replace('-', '')
                window.location.href = '/events/delete/' + eventID;
            }
        })

        function attendEvent() {
            $.ajax({
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    id: button.value,
                },
                url: url,
                success: (data) => {
                    button.innerHTML = gettext("Do not attend event")
                    button.value = '-' + button.value
                    button.setAttribute("class", "btn btn-danger")
                    printMessage('Success', data.message)
                    slideUpAlert()

                }, error: (data) => {
                    printMessage('Error', data.responseJSON.message)
                    slideUpAlert()
                }
            })
        }

        function attendPayedEvent(e) {
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
                                amount: parseInt(event.price) * 100,
                                currency: "nok",
                                name: event.host,
                                description: event.name,
                                email: user.email,
                            });

                            e.preventDefault();
                        },
                        error: data => {
                            printMessage('Error', gettext('Could not get userinfo'))
                            slideUpAlert()
                        }
                    });
                },
                error: data => {
                    printMessage('Error', gettext('Could not get event info'))
                    slideUpAlert()
                }
            })
        }

        /**
         * Sends a remove attended request to the server
         * @param button
         * @param csrftoken
         */
        function removeAttendEvent() {
            button.value = button.value.substring(1,)
            $.ajax({
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    id: button.value
                },
                url: url,
                success: (data) => {
                    button.innerHTML = buttonText
                    button.setAttribute("class", "btn btn-success")
                    printMessage('Success', data.message)
                    slideUpAlert()

                }, error: (data) => {
                    printMessage('Error', data.responseJSON.message)
                    slideUpAlert()
                }
            })
        }

    }
)

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

