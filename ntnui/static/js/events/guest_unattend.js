// Used to set what kind of message alert to show
const MsgType = {
    SUCCESS: "SUCSESS",
    ERROR: "ERROR"
}

// On document ready
$(() => {
    $("#unattend-event-by-token-button").click(async (e) => {
        e.preventDefault()
        const button = getButton(e)
        if (!$(button).prop('disabled')) {
            $(button).prop("disabled", true).addClass("disabled");
            setButtonLoader(button, '#AA0000')
            response = await sendAjax({}, ("/ajax/events/unattend-event_by_token/" + button.value ), 'GET', button)
            if(response) {
                $("#container").html("<i>" + gettext("You will now be redirected to the main event page") + "</i")
                printMessage(MsgType.SUCCESS, response.message)
                setTimeout( () => {
                    window.location.replace('/events')
                }, 2000)
            }
        }
    })
})

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
 * Setts the button loader
 * @param button
 * @param color
 */
function setButtonLoader(button, color) {
    if (!$(button).find(".loader").length) {
        button.innerHTML = ('<div style="border: .1rem solid ' + color + '; border-top: .1rem solid white" class="loader"></div>')
            + button.innerHTML;
    }
}


async function sendAjax(data, url, type, button) {
    data.csrfmiddlewaretoken = getCookie('csrftoken');
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
}
