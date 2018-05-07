// Define enum use to set the state of the button
const States = {
    ATTEND: 'ATTEND',
    UNATTEND: 'UNATTEND',
    WAIT_LIST: 'WAIT_LIST',
    ON_WAITING_LIST: 'ON_WAITING_LIST'
}

// Used to set the modal functionality
const ModalTypes = {
    UNATTEND_EVENT: 'UNATTEND_EVENT',
    UNATTEND_SUB_EVENT: 'UNATTEND_SUB_EVENT',
}

// Used to set what kind of message alert to show
const MsgType = {
    SUCCESS: "SUCSESS",
    ERROR: "ERROR"
}

// Set the currentState, defaultis ADD
let state

// Keeps the current modal state
let modalType;

// defines variables that will be used
let csrftoken

// EventId sets the id for a given event, the has price sets whether the event has a price
let eventID
let hasNoPrice;

// used for guest users
let isGuestUser = false;
let email, firstName, lastName, phone

// Defines the button to be updated when payting for an event
let paymentButton;

// used to define the current language
let lang;

// define handler used to access stripeCheckout
let handler = null;

// Array containing all the subEvents for this event
let subEvents = []

// index of current subEvent
let subEventIndex

/**
 * When the document have loaded, add listener to attend-event-button and send ajax.
 */
$(() => {
    // get the language
    lang = $('html').attr('lang')

    if (lang === 'nb' || lang === 'nn') {
        lang = 'no';
    }

    // Get the eventID
    const attendEventButton = $("#attend-event-button")
    eventID = attendEventButton.val()

    // Get the state from the button
    const type = attendEventButton.attr("data-state")
    state = getState(type);

    hasNoPrice = $("#price").length === 0;

    // FInd all the subEvents
    $(".join-subevent-button").each((e, element) => {
        let subEvent = {id: element.value}
        subEvent.state = getState(element.getAttribute("data-state"))
        subEvents.push(subEvent)
    })

    // get the csrf token
    csrftoken = getCookie('csrftoken')

    // if user is guest, set guest user to true
    if ($('#guestUserModal').length) {
        isGuestUser = true;
    }

    /**
     * Configure stripe
     */
    handler = StripeCheckout.configure({
        key: 'pk_test_TagT9jGDj7CN9NOQfTnueTxz',
        image: "/static/img/ntnui2.svg",
        locale: lang,
        token: (token) => {
            processStripeToken(token);
        }
    });
})

/**
 * Finds the state for a given string
 * @param type
 * @returns {*}
 */
function getState(type) {
    if (type === "wait-list") {
        return States.WAIT_LIST
    } else if (type === "unattend") {
        return States.UNATTEND
    } else if (type === "on-waiting-list") {
        return States.ON_WAITING_LIST
    }else {
        return States.ATTEND
    }
}

/**
 * Sends a attend event request to the server
 */
$("#attend-event-button").click((e) => {
    e.preventDefault()
    const button = getButton(e);

    switch (state) {
        case States.UNATTEND:
            modalType = (hasNoPrice) ? ModalTypes.UNATTEND_EVENT : ModalTypes.UNATTEND_PAYED_EVENT
            $("#deleteModal").modal("show");
            break;
        case States.ATTEND:
            if (isGuestUser) {
                showGuestModal();
            } else {
                if (hasNoPrice) {
                    attendEvent(button)
                } else {
                    attendPayedEvent(button)
                }
            }
            break;
        case States.WAIT_LIST:
            attendWaitingList(button)
            break;
        case States.ON_WAITING_LIST:
            break;
    }
})

/**
 * Sends a attend subevet request
 */
$(".join-subevent-button").click((e) => {
    const button = getButton(e)
    let subEvent = subEvents.filter((event) => event.id === button.value)
    subEventIndex = subEvents.indexOf(subEvent[0])
    // IF the first sign is a - we want to remove attending event
    if (subEvent[0].state === States.UNATTEND) {
        modalType = ModalTypes.UNATTEND_SUB_EVENT
        $("#deleteModal").modal("show");
    } else {
        attendEvent(button, subEvent[0])
    }
})

/**
 * onClick for the remove button on the delete modal
 */
$("#remove-attend-event-button-modal").click(() => {
    switch (modalType) {
        case ModalTypes.UNATTEND_EVENT:
            removeAttendEvent($("#attend-event-button")[0])
            break;
        case ModalTypes.UNATTEND_SUB_EVENT:
            $(".join-subevent-button").each((e, element) => {
                if (element.value = subEvents[subEventIndex].id) {
                    removeAttendEvent(element, subEvents[subEventIndex])
                }
            })
            break;
    }
})

/**
 * On Click for the guest modal
 */
$("#guest-data-form").on('submit', async (e) => {
    // Get all values from the modal
    firstName = $("#first-name").val()
    lastName = $("#last-name").val()
    phone = $("#phone").val()
    email = $("#input-email").val()
    if ($("#price").length > 0) {
        const result = await sendAjax(data, ('/ajax/events/' + button.value), 'GET')
        if (result) {
            handler.open({
                amount: parseInt(event.price) * 100,
                currency: "nok",
                name: event.host,
                description: event.name,
                email: email,
            });
        }
        e.preventDefault();
    } else {
        let postData = $("#guest-data-form").serialize();
        postData = postData + '&csrfmiddlewaretoken=' + csrftoken;
        postData = postData + '&id=' + eventID;
        let result = await sendAjax(postData, '/ajax/events/attend-event')
        if (result) {
            printMessage(MsgType.SUCCESS, result.message)
        }
        hideGuestModal()
        e.preventDefault();
    }
})


/**
 * Sends a ajax request with the given data, and a given url and type(POST; GET)
 * @param data
 * @param url
 * @param type
 * @returns {Promise.<*>}
 */
async function sendAjax(data, url, type) {
    data.csrfmiddlewaretoken = csrftoken;
    try {
        let result = await $.ajax({
            type: type || 'POST',
            data: data,
            url: url
        })
        return result;
    } catch (error) {
        if (error.responseJSON) {
            printMessage(MsgType.ERROR, error.responseJSON.message)
        }
    }
}

/**
 * Returnes the button press from a event
 * @param e
 * @returns {*}
 */
function getButton(e) {
    const event = e || window.event
    const target = event.target
    return $(target).closest("button")[0]
}

/**
 * Possess a given strope tokenn, before its sendt to the server
 * @param token
 * @returns {Promise.<void>}
 */
async function processStripeToken(token) {
    let data = {
        csrfmiddlewaretoken: csrftoken,
        stripeToken: token.id,
        event_id: eventID,
        stripEmail: token.email,
    }
    if (isGuestUser) {
        data.email = email
        data.first_name = firstName
        data.last_name = lastName
        data.phone = phone;
    }

    let result = await sendAjax(data, '/ajax/events/attend-payment-event')
    if (result) {
        button.innerHTML = gettext("Do not attend event")
        button.value = '-' + button.value
        button.setAttribute("class", "btn btn-danger")
        printMessage(MsgType.SUCCESS, data.message)
    }
    hideGuestModal()
}

/**
 * Opens the guest modal
 */
function showGuestModal() {
    $("#guestUserModal").modal('show')
}

/**
 * hides the guest modal
 */
function hideGuestModal() {
    $("#guestUserModal").modal('hide')
}

/**
 * Updates the tilte and the style of a button
 * @param button
 * @param title
 * @param type
 */
function updateButton(button, title, type) {
    button.innerHTML = title;
    switch (type) {
        case States.UNATTEND:
            button.setAttribute('class', 'btn btn-danger');
            break;
        case States.ATTEND:
            button.setAttribute("class", "btn btn-success")
            break;
        case States.WAIT_LIST:
            button.setAttribute("class", "btn btn-info")
            break;
        case States.ON_WAITING_LIST:
            button.setAttribute("class", "btn btn-secondary disabled")
            break;
    }
}

/**
 * Function used to get the infromation needed to attend a payed event
 * @param button
 * @param subEvent
 * @returns {Promise.<void>}
 */
async function attendPayedEvent(button, subEvent) {
    const URL = !subEvent ? ('/ajax/events/' + eventID) : ('/ajax/events/sub-event/' + subEvent.id)
    paymentButton = button;
    const event = await sendAjax({id: (subEvent ? subEvent.id : eventID) }, URL)
    if (event) {
        const user = await sendAjax({}, '/ajax/accounts', 'GET')
        if (user) {
            handler.open({
                amount: parseInt(event.price) * 100,
                currency: "nok",
                name: event.host,
                description: event.name,
                email: user.email,
            });
        }
    }
}

/**
 * Gather information and send a request to the server in order to let the user attend a given event
 * @param button
 * @param subEvent
 * @returns {Promise.<void>}
 */
async function attendEvent(button, subEvent) {
    let response;
    if (subEvent) {
        response = await sendAjax({sub_event_id: subEvent.id}, '/ajax/events/attend-event');
    } else {
        response = await sendAjax({event_id: eventID}, '/ajax/events/attend-event');
    }
    if (response) {
        updateButton(button, gettext('Do not attend event'), States.UNATTEND)
        if (subEvent) {
            subEvent.state = States.UNATTEND
        } else {
            state = States.UNATTEND
        }
        printMessage(MsgType.SUCCESS, response.message);
    }
}

/**
 * Gather information and send a request to the server in order to let the user be place on the waiting
 * @param button
 * @param subEvent
 * @returns {Promise.<void>}
 */
async function attendWaitingList(button, subEvent) {
    let response;
    if (subEvent) {
        response = await sendAjax({event_id: eventID}, 'waiting-list-event');
    } else {
        response = await sendAjax({sub_event_id: subEvent.id}, 'waiting-list-event');
    }
    if (response) {
        updateButton(button, gettext('you are on the wailing list'), States.ON_WAITING_LIST)
        if (subEvent) {
            subEvent.state = States.ON_WAITING_LIST
        } else {
            state = States.ON_WAITING_LIST
        }
        printMessage(MsgType.SUCCESS, response.message);
    }
}

/**
 * Removes the user from attending a given event
 * @param button
 * @param subEvent
 * @returns {Promise.<void>}
 */
async function removeAttendEvent(button, subEvent) {
    let response;
    if (subEvent) {
        response = await sendAjax({sub_event_id: subEvent.id}, '/ajax/events/unattend-event')
    } else {
        response = await sendAjax({event_id: eventID}, '/ajax/events/unattend-event')
    }
    if (response) {
        if (response.number_of_participance >= response.maximum_number_of_participants) {
            updateButton(button, gettext('waitlist'), States.WAIT_LIST)
            if (subEvent) {
                subEvent.state = States.WAIT_LIST
            } else {
                state = States.WAIT_LIST
            }
        }
        updateButton(button, gettext('attend event'), States.ATTEND)
        if (subEvent) {
            subEvent.state = States.ATTEND
        } else {
            state = States.ATTEND
        }
        printMessage(MsgType.SUCCESS, data.message)
    }
}

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
        case MsgType.ERROR:
            type = 'danger'
            break
        case MsgType.SUCCESS:
            type = 'success'
            break
    }
    //print message to screen
    $(".alert-message-container").html(() => {
        return "<div class=\"alert alert-" + type + " show fade \" role=\"alert\"> <strong>" + type + ":</strong>" +
            " " + msg + "</div>"
    })

    //set timeout
    setTimeout(() => {
        //slide up the alert
        $(".alert").slideUp()
        //sets the amount of ms before the alert is closed
    }, 2000)
}