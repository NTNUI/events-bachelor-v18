// List of subEvents
let subEvents = [];

// list of categories
let categories = []

// subevent id counter
let idCounter = 0;
// On document ready
$(() => {

    /**
     * When clicking the create event button, validate all form fields, if they are not valid show alert, else
     * send ajax request
     */
    $("#create-event-button").click(function (e) {
        let inputs = $(".form-input-create-event")
        for (let i = 0; i < inputs.length; i++) {
            if (!inputs[i].validity.valid) {
                printMessage('error', gettext('Please validate all fields'))
                slideUpAlert(false)
                return;
            }
        }

        // Sends request to server to create event
        $.ajax({
            type: 'POST',
            url: '/ajax/events/add-event',
            data: $('#create-event-form').serialize(),
            success: (data) => {
                //show success alert
                printMessage('success', data.message)
            },
            error: (data) => {
                //show error alert
                printMessage('error', data.message)
                slideUpAlert(false)
            }
        })
        e.preventDefault();
    })

    // Show the subEvent modal
    $("#add-subEvent-button").click(function (e) {
        $("#subEvent-modal").modal('show')
    });

    $("#add-category-button").click(function (e) {
        $("#category-modal").modal('show')
    });

    // add listener to all the from fields
    $(".form-input-create-event").blur(validateForm);

    $("#submit-sub-event-form").click((e) => {
        e.preventDefault()
        let subEvent = {};
        $('#subEvent-data-form *').filter(':input').each((e, input) => {
            subEvent[input.name] = input.value;
        });
        subEvent.id = idCounter;


        $("#subEvent-modal").modal('hide')
        addSubEvent(subEvent)
        subEvents.push(subEvent)
    });

    $("#submit-category-form").click((e) => {
        e.preventDefault()
        $("#category-data-form")[0].checkValidity()

    })

    $(".testing").each((e, container) => {
        container.addEventListener("dragover", dragover)
        container.addEventListener("dragenter", dragenter)
        container.addEventListener("drop", drop)
    })


    function dragover(e) {
        e.preventDefault()
    }

    function dragenter(e) {
        e.preventDefault()
    }

    function drop() {
        this.append($("#subEvent-element")[0])
    }
})
;

/**
 * Validate a given input in a form
 * @param e
 */
let validateForm = (e) => {
    // Get the button that was pressed
    const event = e || window.event
    const button = event.target

    // Use to see if field is displaying error
    const dispError = $(button).next().length === 0;

    // If field is of type datetime-local
    if ($(button).attr("type") === 'datetime-local') {
        validateDate(button, dispError)
    }
    // if filed is not valid, and error is currently not displayed. Display error
    else if (!button.checkValidity()) {
        if (dispError) {
            $(button).after(getAlert(gettext('invalid input')));
        }
    } else {
        // If filed is valid, remove error
        $(button).next().remove()
    }
}

/**
 * Gives the HTML code for a given error message
 * @param text
 * @returns {string}
 */
function getAlert(text) {
    return '<div class="error-input alert alert-danger collapse"> ' +
        '<p>' + text + '</p> ' +
        '</div>';
}


/**
 * Validates a date inpur
 * @param button
 * @param dispError
 */
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
        // remove display error
        $(button).next().remove()
    }
}


function addSubEvent(subEvent) {
    $("#subEvents").append(
        '<div class="subEvent-element" class="card" draggable="true">' +
        '<div class="sub-event-card-container card-body">' +
        '    <div class="sub-event-name"><b>' + subEvent.name_nb + '</b></div>' +
        '        <div class="center-content sub-event-dateime">' +
        '             <i>' + subEvent.start_date + ' - ' + subEvent.end_date + '</i>' +
        '        </div>\n' +
        '         <div class="sub-event-button-container">' +
        '          <div class="delete-sub-event-button center-content" data-id="' + idCounter + '">' +
        '             <img class="img-cross" src="/static/img/circle-x.svg" alt="exit"></div>' +
        '         </div>' +
        '        </div>' + '</div>');

    idCounter++;

    
    $(".delete-sub-event-button").click((e) => {
        const event = e || window.event
        const value = $(event.target).closest(".delete-sub-event-button").attr('data-id')
        subEvents = subEvents.filter(item => item.id != value)
        $(event.target).closest(".subEvent-element").remove()
    })
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
        return "<div class=\"slide-up alert alert-" + type + " show fade \" role=\"alert\"> <strong>" + msgType + ":</strong>" +
            " " + msg + "</div>"
    })

    //set timeout
    setTimeout(() => {
        //slide up the alert
        $(".slide-up").slideUp()
        //sets the amount of ms before the alert is closed
    }, 2000)
}


