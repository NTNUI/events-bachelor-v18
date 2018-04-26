let name_no = $("#name_no")[0];
let name_en = document.getElementsByName("name_en")[0];
let start_date = document.getElementsByName("start_date")[0];
let end_date = document.getElementsByName("end_date")[0];
let description_text_no = document.getElementsByName("description_text_no")[0];
let description_text_en = document.getElementsByName("description_text_en")[0];
let email_text_no = document.getElementsByName("email_text_no")[0];
let email_text_en = document.getElementsByName("email_text_en")[0];
let attendance_cap = document.getElementsByName("attendance_cap")[0];
let price = document.getElementsByName("price")[0];


$(() => {
    $("#create-event-button").click(function (e) {
        if (!name_no.validity.valid || !name_en.validity.valid || !start_date.validity.valid || !end_date.validity.valid
            || !description_text_no.validity.valid || !description_text_en.validity.valid || !email_text_no.validity.valid
            || !email_text_en.validity.valid || !attendance_cap.validity.valid || !price.validity.valid) {
            $("div.alert-message-container").html("<p>Please validate all fields</p>");
        }
        else {
            const postData = $('#create-event-form').serialize()
            $.ajax({
                type: 'POST',
                url: '/ajax/events/add-event',
                data: postData,
                success: (data) => {
                    //show success alert
                    printMessage('success', data.message)
                    slideUpAlert(true)
                },
                error: (data) => {
                    //show error alert
                    printMessage('error', data.message)
                    slideUpAlert(false)
                }
            })
        }
        e.preventDefault();
    })
    $("#add-subEvent-button").click(function (e) {
        $("#subEvent-modal").show();
    });

    $(".form-input-create-event").blur(validateForm);

});

let validateForm = (e) => {
    const event = e || window.event
    const button = event.target
    const dispError = $(button).next().length === 0;

    if ($(button).attr("type") === 'datetime-local') {
        validateDate(button, dispError)
    }
    else if (!button.checkValidity()) {
        if (dispError) {
            $(button).after(getAlert(gettext('invalid input')));
        }
    } else {
        $(button).next().remove()
    }
}

function getAlert(text) {
    return '<div style="display: block" class="alert alert-danger collapse"> ' +
        '<p>' + text + '</p> ' +
        '</div>';
}

function validateDate(button, dispError) {
    //create date today
    let today = new Date().toISOString();
    //slice seconds and timezone
    today = today.slice(0, -8);

    const startDateInput = $("#start-date")
    const endDateInput = $("#end-date")

    //get end date and start date
    const input_End_date = endDateInput.val();
    const input_Start_date = startDateInput.val();

    //check whether start_date is after current date
    if (!(input_Start_date > today)) {
        if (dispError) {
            $(button).after(getAlert(gettext("Invalid date!")));
        }
    }
    //if end date is already entered, check whether start date is before it
    else if (!(input_End_date === "") && !(input_End_date > input_Start_date)) {
        if (dispError) {
            $(button).after(getAlert($(button).attr("id") === "start-date" ?
                gettext("Start date is not before end date!") : gettext("End date is not after start date!")));
        }
    } else {
        $(button).next().remove()
    }
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
        case 'error':
            type = 'danger'
            break
        case 'success':
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
function slideUpAlert(redirect) {

    //set timeout
    setTimeout(() => {
        //slide up the alert
        $(".alert")
        if (redirect) {
            window.location.href = '/events'
        }
        //sets the amount of ms before the alert is closed
    })
}