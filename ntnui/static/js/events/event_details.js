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

// Used to know whether to use eventID or subEventid when performing a payment
let paymentSubEvent

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

// Defines the button to be updated when paying for an event
let paymentButton;

// defines what button to be updated when guestUser is active
let guestSubEventButton
let guestSubEventObject

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
        let subEvent = {id: parseInt(element.value)}
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


    /**
     * Sends a attend event request to the server
     */
    $("#attend-event-button").click((e) => {
        e.preventDefault()
        const button = getButton(e);
        if (!$(button).prop('disabled')) {
            if (isGuestUser) {
                if (state === States.UNATTEND || state === States.ON_WAITING_LIST) {
                    attendEventBasedOnState(button)
                } else {
                    showGuestModal();
                }


            } else {
                attendEventBasedOnState(button)
            }
        }
    })

    /**
     * Sends a attend subevet request
     */
    $(".join-subevent-button").click((e) => {
        const button = getButton(e)

        if (!$(button).prop('disabled')) {
            let subEvent = subEvents.filter((event) => event.id == parseInt(button.value))
            subEventIndex = subEvents.indexOf(subEvent[0])

            if (isGuestUser) {
                guestSubEventButton = button;
                guestSubEventObject = subEvent[0]
                if (guestSubEventObject.state === States.UNATTEND || guestSubEventObject.state === States.ON_WAITING_LIST) {
                    attendSubEventBasedOnState(guestSubEventButton, guestSubEventObject)
                    guestSubEventObject = null;
                    guestSubEventButton = null;
                } else {
                    showGuestModal();
                }
            } else {
                attendSubEventBasedOnState(button, subEvent[0])
            }
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
                const button = getSubEventButton(subEvents[subEventIndex])
                $(button).prop("disabled", true).addClass("disabled");
                removeAttendEvent(button, subEvents[subEventIndex])
                break;
        }
    })

    /**
     * On Click for the guest modal
     */
    $("#guest-data-form").on('submit', async (e) => {
        e.preventDefault();
        // Get all values from the modal
        firstName = $("#first-name").val();
        lastName = $("#last-name").val();
        phone = $("#phone").val();
        email = $("#input-email").val();

        if (guestSubEventObject) {
            attendSubEventBasedOnState(guestSubEventButton, guestSubEventObject)
            guestSubEventObject = null;
            guestSubEventButton = null;
        } else {
            attendEventBasedOnState($("#attend-event-button")[0])
        }
        hideGuestModal()
    })
})

/**
 * Returnes the button maching the subEvent id
 * @param subEvent
 */
function getSubEventButton(subEvent) {
    let button;
    $(".join-subevent-button").each((e, element) => {
        if (parseInt(element.value) === subEvent.id) {
            button = element;
            return false
        }
    })
    return button;
}

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
    } else {
        return States.ATTEND
    }
}


/**
 * Uses the state of the subEvent to figure out what action to perform
 * @param button
 * @param subEvent
 */
function attendSubEventBasedOnState(button, subEvent) {
    switch (subEvent.state) {
        case States.ATTEND:
            if (!$(button).closest(".sub-event-container").find(".price").length) {
                $(button).prop("disabled", true).addClass("disabled");
                attendEvent(button, subEvent)
            } else {
                attendPayedEvent(button, subEvent)
            }
            break;
        case States.UNATTEND:
            modalType = ModalTypes.UNATTEND_SUB_EVENT
            $("#deleteModal").modal("show");
            break;
        case States.ON_WAITING_LIST:
            $(button).prop("disabled", true).addClass("disabled");
            removeAttendEvent(button, subEvent)
            break;
        case States.WAIT_LIST:
            $(button).prop("disabled", true).addClass("disabled");
            attendWaitingList(button, subEvent)
            break;
    }
}

/**
 * Uses the state of the vent button to figure out what action to perform
 * @param button
 */
function attendEventBasedOnState(button) {
    switch (state) {
        case States.UNATTEND:
            modalType = ModalTypes.UNATTEND_EVENT
            $("#deleteModal").modal("show");
            break;
        case States.ATTEND:
            if (hasNoPrice) {
                $(button).prop("disabled", true).addClass("disabled");
                attendEvent(button)
            } else {
                attendPayedEvent(button)
            }
            break;
        case States.WAIT_LIST:
            $(button).prop("disabled", true).addClass("disabled");
            attendWaitingList(button)
            break;
        case States.ON_WAITING_LIST:
            $("#deleteModal").modal("show");
            modalType = ModalTypes.UNATTEND_EVENT
            break;
    }
}


/**
 * Sends a ajax request with the given data, and a given url and type(POST; GET)
 * @param data
 * @param url
 * @param type
 * @param button
 * @returns {Promise.<*>}
 */
async function sendAjax(data, url, type, button) {
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
        } else {
            printMessage(MsgType.ERROR, gettext("Your request could not be processed"))
        }
        if (button) {
            $(button).find('.loader').remove();
            if ($(button).prop('disabled')) {
                $(button).prop("disabled", false).removeClass("disabled");
            }
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
    const element = event.target
    return $(element).closest("button")[0]
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
        stripeEmail: token.email,
    }

    let subEvent = paymentSubEvent
    if (paymentSubEvent) {
        data.sub_event_id = subEvent.id;
        let button = getSubEventButton(subEvent)
        setButtonLoader(button)
        $(button).prop("disabled", true).addClass("disabled");
    }
    else {
        data.event_id = eventID;
        let button = $("#attend-event-button")[0]
        setButtonLoader(button)
        $(button).prop("disabled", true).addClass("disabled");
    }
    paymentSubEvent = null;
    if (isGuestUser) {
        data.email = email
        data.first_name = firstName
        data.last_name = lastName
        data.phone = phone;
    }

    let result = await sendAjax(data, '/ajax/events/attend-payment-event')
    if (result) {
        let participantText = result.number_of_participants + (result.attendance_cap ? ("/" + result.attendance_cap) : "")
        if (subEvent) {
            updateParticipantTextSubEvent(getSubEventButton(subEvent), participantText)
            subEvent.state = States.UNATTEND;
            updateButton(getSubEventButton(subEvent), gettext('Unattend'), States.UNATTEND, subEvent)
            subEvents = subEvents.map(listSubEvent => listSubEvent.id === subEvent.id ? subEvent : listSubEvent)
        } else {
            $("#attendance").html(participantText)
            state = States.UNATTEND
            updateButton($("#attend-event-button")[0], gettext('Unattend'), States.UNATTEND)
        }
        printMessage(MsgType.SUCCESS, result.message)
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
function updateButton(button, title, state, subEvent) {
    $(button).find(".button-title-container").html(title);
    switch (state) {
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
            button.setAttribute("class", "btn btn-secondary")
            break;
    }
    if (subEvent) {
        button.setAttribute("class", ("join-subevent-button " + button.getAttribute("class")))
    }
    $(button).find(".loader").remove();

    if ($(button).prop('disabled')) {
        $(button).prop("disabled", false).removeClass("disabled");
    }
}

function setButtonLoader(button, color) {
    if (!$(button).find(".loader").length) {
        button.innerHTML = ('<div style="border: .1rem solid ' + color + '; border-top: .1rem solid white" class="loader"></div>')
            + button.innerHTML;
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
    const event = await sendAjax({id: (subEvent ? subEvent.id : eventID)}, URL, 'POST', button)
    if (event) {
        let user = {}
        if (!isGuestUser) {
            user = await sendAjax({}, '/ajax/accounts', 'GET')
            if (!user) {
                return
            }
        } else {
            user.email = email
        }
        if (subEvent) {
            paymentSubEvent = subEvent
        }
        handler.open({
            amount: parseInt(event.price) * 100,
            currency: "nok",
            name: event.host,
            description: event.name,
            email: user.email,
        });
    }
}

/**
 * Gather information and send a request to the server in order to let the user attend a given event
 * @param button
 * @param subEvent
 * @returns {Promise.<void>}
 */
async function attendEvent(button, subEvent) {
    setButtonLoader(button, '#00AA00')
    let response;
    let context = {}
    if (isGuestUser) {
        context = {first_name: firstName, last_name: lastName, email: email, phone: phone}
    }
    if (subEvent) {
        context.sub_event_id = subEvent.id
        response = await sendAjax(context, '/ajax/events/attend-event', 'POST', button);
    } else {
        context.event_id = eventID
        response = await sendAjax(context, '/ajax/events/attend-event', 'POST', button);
    }
    if (response) {
        let participantText = response.number_of_participants + (response.attendance_cap ? ("/" + response.attendance_cap) : "")
        updateButton(button, gettext('Unattend'), States.UNATTEND, subEvent)
        if (subEvent) {
            updateParticipantTextSubEvent(getSubEventButton(subEvent), participantText)
            subEvents[subEvents.indexOf(subEvent)].state = States.UNATTEND
        } else {
            $("#attendance").html(participantText)
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
    setButtonLoader(button, '#0000AA')
    let response;
    let context = {}
    if (isGuestUser) {
        context = {first_name: firstName, last_name: lastName, email: email, phone: phone}
    }
    if (subEvent) {
        context.sub_event_id = subEvent.id
        response = await sendAjax(context, '/ajax/events/waiting-list', 'POST', button);
    } else {
        context.event_id = eventID
        response = await sendAjax(context, '/ajax/events/waiting-list', 'POST', button);
    }
    if (response) {
        let participantText = response.number_of_participants + (response.attendance_cap ? ("/" + response.attendance_cap) : "")
        updateButton(button, gettext('Remove me from the wait list'), States.ON_WAITING_LIST, subEvent)
        if (subEvent) {
            updateParticipantTextSubEvent(getSubEventButton(subEvent), participantText)
            subEvents[subEvents.indexOf(subEvent)].state = States.ON_WAITING_LIST
        } else {
            $("#attendance").html(participantText)
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
    if (subEvent && subEvent.state === States.ON_WAITING_LIST) {
        setButtonLoader(button, '#AAAAAA')
    } else if (state == States.ON_WAITING_LIST) {
        setButtonLoader(button, '#AAAAAA')
    } else {
        setButtonLoader(button, '#AA0000')
    }
    let context = {}
    if (isGuestUser) {
        context = {first_name: firstName, last_name: lastName, email: email, phone: phone}
    }
    let response;
    if (subEvent) {
        context.sub_event_id = subEvent.id
        response = await sendAjax(context, '/ajax/events/unattend-event', 'POST', button)
    } else {
        context.event_id = eventID
        response = await sendAjax(context, '/ajax/events/unattend-event', 'POST', button)
    }
    if (response) {
        let participantText = response.number_of_participants + (response.attendance_cap ? ("/" + response.attendance_cap) : "")
        if (parseInt(response.number_of_participants) >= parseInt(response.attendance_cap)) {

            updateButton(button, gettext('Put me on the wait list'), States.WAIT_LIST, subEvent)

            if (subEvent) {
                updateParticipantTextSubEvent(getSubEventButton(subEvent), participantText)
                subEvents[subEvents.indexOf(subEvent)].state = States.WAIT_LIST
            } else {
                $("#attendance").html(participantText)
                state = States.WAIT_LIST
            }
        } else {
            updateButton(button, gettext('Attend event'), States.ATTEND, subEvent)
            if (subEvent) {
                updateParticipantTextSubEvent(getSubEventButton(subEvent), participantText)
                subEvents[subEvents.indexOf(subEvent)].state = States.ATTEND
            } else {
                $("#attendance").html(participantText)
                state = States.ATTEND
            }
            printMessage(MsgType.SUCCESS, response.message)
        }
    }
}

// Close Checkout on page navigation:
window.addEventListener('popstate', function () {
    handler.close();
});


function updateParticipantTextSubEvent(button, text) {
    $(button).closest(".sub-event-container").find(".attendance").html(text)
}


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
    let msgIdentifier;
    switch (msgType) {
        case MsgType.ERROR:
            type = 'danger'
            msgIdentifier = gettext('Error')
            break
        case MsgType.SUCCESS:
            type = 'success'
            msgIdentifier = gettext('Success')
            break
    }
    //print message to screen
    $(".alert-message-container").html(() => {
        return "<div class=\"alert alert-" + type + " show fade \" role=\"alert\"> <strong>" + msgIdentifier + ":</strong>" +
            " " + msg + "</div>"
    })

    //set timeout
    setTimeout(() => {
        //slide up the alert
        $(".alert").slideUp()
        //sets the amount of ms before the alert is closed
    }, 2000)
}