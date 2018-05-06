// Define enum use to set the state of the button
const States = {
    ATTEND: 'ATTEND',
    UNATTEND: 'UNATTEND',
    WAIT_LIST: 'WAIT_LIST'
}

// Set the currentState, defaultis ADD
let state

// Used to set the right modal content
const ModalTypes = {
    UNATTEND_EVENT: 'UNATTEND_EVENT',
    UNATTEND_PAYED_EVENT: 'UNATTEND_PAYED_EVENT',
    UNATTEND_SUB_EVENT: 'UNATTEND_SUB_EVENT',
    UNATTEND_PAYED_SUB_EVENT: 'UNATTEND_PAYED_SUB_EVENT',
}

let modalType;

// defines variables that will be used
let csrftoken

// properties used by the modal, in order to preform the right action
let lastPressedButton = null;
let buttonText
let url

// Sets the id of the given event
let eventID

// Event has price
let hasNoPrice;

// used for guest users
let isGuestUser = false;
let email, firstName, lastName, phone


// used to define the current language
let lang;

// define handler used to access stripeCheckout
let handler = null;

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

    const type = attendEventButton.attr("data-state")
    if (type === "wait-list") {
        state = States.WAIT_LIST
    } else if (type === "unattend") {
        state = States.UNATTEND
    } else {
        state = States.ATTEND
    }

    hasNoPrice = $("#price").length === 0;

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
                    attendEvent('/ajax/events/attend-event', button)
                } else {
                    attendPayedEvent()
                }
            }
            break;
    }
})

/**
 * Sends a attend subevet request
 */
$(".join-subevent-button").click((e) => {
    const event = e || window.event
    button = event.target
    // IF the first sign is a - we want to remove attending event
    if (button.value[0] === "-") {
        url = '/ajax/events/user-unattend-sub-event'
        buttonText = gettext('attend event')
        openModal()
    } else {
        url = '/ajax/events/attend-event'
        attendEvent()
    }
})

$("#remove-attend-event-button-modal").click(() => {
    switch (modalType) {
        case ModalTypes.UNATTEND_EVENT:
            removeAttendEvent('/ajax/events/user-unattend-event')
            break;
        case ModalTypes.UNATTEND_PAYED_EVENT:
            // ('/ajax/events/user-unattend-payment-event', gettext('Pay using card'))
            break;
    }
})

$("#guest-data-form").on('submit', async (e) => {
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
        postData = postData + '&id=' + buttonValue;
        let result = await sendAjax(postData, '/ajax/events/attend-event')
        if (result) {
            printMessage('success', result.message)
        }
        hideGuestModal()
        e.preventDefault();
    }
})


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
            printMessage('Error', error.responseJSON.message)
        }
    }
}

function getButton(e) {
    const event = e || window.event
    return event.target
}

async function processStripeToken(token) {
    if (isGuestUser) {
        const data = {
            csrfmiddlewaretoken: csrftoken,
            stripeToken: token.id,
            id: buttonValue,
            stripEmail: token.email,
            email: email,
            first_name: firstName,
            last_name: lastName,
            phone: phone,
        }
    } else {
        const data = {
            csrfmiddlewaretoken: csrftoken,
            id: buttonValue,
            stripeToken: token.id,
            stripEmail: token.email
        }
    }
    let result = await sendAjax(data, '/ajax/events/attend-payment-event')
    if (result) {
        button.innerHTML = gettext("Do not attend event")
        button.value = '-' + button.value
        button.setAttribute("class", "btn btn-danger")
        printMessage('Success', data.message)
    }
    hideGuestModal()
}

function showGuestModal() {
    $("#guestUserModal").modal('show')
}

function hideGuestModal() {
    $("#guestUserModal").modal('hide')
}

async function attendEvent(url, button) {
    let response = await sendAjax({event_id: button.value}, url);
    if (response) {
        updateButton(button, gettext('Do not attend event'), States.UNATTEND)
        state = States.UNATTEND
        printMessage('Success', response.message);
    }
}

async function removeAttendEvent(url) {
    const button = $("#attend-event-button")[0]
    const result = await sendAjax({id: button.value}, url)
    if (result) {
        updateButton(button, gettext('attend event'), States.ATTEND)
        printMessage('Success', data.message)
    }
}

function updateButton(button, title, type) {
    button.innerHTML = title;
    switch (type) {
        case States.UNATTEND:
            button.setAttribute('class', 'btn btn-danger');
            break;
        case States.ATTEND:
            button.setAttribute("class", "btn btn-success")
            break;
    }
}

async function attendPayedEvent() {
    const URL = '/ajax/events/' + eventID
    const event = await sendAjax(null, URL)
    if (event) {
        const user = await sendAjax(null, '/ajax/accounts')
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

    //set timeout
    setTimeout(() => {
        //slide up the alert
        $(".alert").slideUp()
        //sets the amount of ms before the alert is closed
    }, 2000)
}