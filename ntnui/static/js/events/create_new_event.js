// List of subEvents
let subEvents = [];

// list of categories
let categories = []

// subevent id counter
let idCounterSubEvent = 0;

// category id counter
let idCounterCategory = 1;

let csrftoken

let eventID;

// On document ready
$(() => {

    csrftoken = getCookie('csrftoken')
    /**
     * When clicking the create event button, validate all form fields, if they are not valid show alert, else
     * send ajax request
     */
    $("#create-event-button").click((e) => {
        e.preventDefault()

        form = $('#create-event-form *')
        let event = validateForm(form)
        if (event) {
            // Sends request to server to create event
            event.csrfmiddlewaretoken = csrftoken;
            $.ajax({
                type: 'POST',
                url: '/ajax/events/add-event',
                data: event,
                success: (data) => {
                    //show success alert
                    // printMessage('success', data.message)
                    eventID = data.id;
                    createCategories(data.id)
                },
                error: (data) => {
                    //show error alert
                    printMessage('error', data.responseJSON.message)
                }
            })
        }
    })

    // Show the subEvent modal
    $("#add-subEvent-button").click(function (e) {
        e.stopPropagation();
        $("#subEvent-modal").modal('show')
    });

    $("#add-category-button").click(function (e) {
        e.stopPropagation();
        $("#category-modal").modal('show')
    });

    $(".card-header").click(function (e) {
        const event = e || window.event
        const button = event.target
        let img = $(button).find(".collapse-header-title").find('img')
        if(img.attr("src") == "/static/img/chevron-bottom.svg") {
            img.attr("src", "/static/img/chevron-top.svg")
        }
        else {
            img.attr("src", "/static/img/chevron-bottom.svg")
        }
    });


    // add listener to all the from event form fields
    $(".form-input-create-event").blur(validateFormEvent);

    // add listener to all the subEvent from fields
    $(".form-input-create-subEvent").blur(validateFormEvent);

    // add listener to all the subEvent from fields
    $(".form-input-create-category").blur(validateFormEvent);

    $("#submit-sub-event-form").click((e) => {
        e.preventDefault()

        form = $('#subEvent-data-form *')
        let subEvent = validateForm(form)
        if (subEvent) {
            subEvent.id = idCounterSubEvent;
            idCounterSubEvent++;
            $("#subEvent-modal").modal('hide')
            subEvent.category = 0;
            addSubEvent(subEvent)
            subEvents.push(subEvent)
        }
    });

    $("#submit-category-form").click((e) => {
        e.preventDefault()
        let form = $('#category-data-form *');
        let category = validateForm(form);
        if (category) {
            $("#category-modal").modal('hide')
            category.id = idCounterCategory;
            addCategory(category)
            idCounterCategory++;
            categories.push(category)
        }

    })
});

async function createCategories(eventID) {
    categories = await Promise.all(categories.map(async (category) => {
        category.csrfmiddlewaretoken = csrftoken
        category.event = eventID
        try {
            let data = await $.ajax({
                type: 'POST',
                url: '/ajax/events/create-category',
                data: category
            })
            category.databaseCategoryId = data.id;
            return category

        } catch (error) {
            //show error alert
            printMessage('error', data.responseJSON.message)
            return category
        }
    }))
    createSubEvents(eventID)
}

async function createSubEvents(eventID) {
    subEventsCreated = await Promise.all(subEvents.map(async (subEvent) => {
        let category = categories.filter((category) => category.id == subEvent.category)
        subEvent.category = category.length ? category[0].databaseCategoryId : ""
        subEvent.csrfmiddlewaretoken = csrftoken
        subEvent.event = eventID
        try {
            let data = await $.ajax({
                type: 'POST',
                url: '/ajax/events/create-sub-event',
                data: subEvent,
            })
            return subEvent
        } catch (error) {
            //show error alert
            printMessage('error', data.responseJSON.message)
            return subEvent
        }
    }))
    if (subEventsCreated) {
        window.location.replace("/events/" + eventID +"/");
    }
}

/**
 * Checks each input in the set of elements
 * @param form
 */
function validateForm(formElements) {
    let valid = true
    formElements.filter(':input').each((e, input) => {
        if (!input.checkValidity()) {
            validateInput(input)
            valid = false;
        }
    })
    if (valid) {
        let element = {};
        formElements.filter(':input').each((e, input) => {
            if (input.name != "csrfmiddlewaretoken") {
                element[input.name] = input.value;
                // input.value = "";
            }
        });
        return element
    }
    return null
}

/**
 * Validate a given input in a form
 * @param e
 */
let validateFormEvent = (e) => {
    // Get the button that was pressed
    const event = e || window.event
    const button = event.target
    validateInput(button)

}

/**
 * Validates a given input
 * @param button
 */
function validateInput(input) {
    // Use to see if field is displaying error
    const dispError = $(input).next().length === 0;

    // If field is of type datetime-local
    if ($(input).attr("type") === 'datetime-local') {
        validateDate(input, dispError)
    }
    // if filed is not valid, and error is currently not displayed. Display error
    else if (!input.checkValidity()) {
        if (dispError) {
            $(input).after(getAlert(gettext('invalid input')));
        }
    } else {
        // If filed is valid, remove error
        $(input).next().remove()
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

    const startDateInput = $(button).parent().parent().find(".start-date")
    const endDateInput = $(button).parent().parent().find(".end-date")

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
        '<div id="subEvent-' + subEvent.id + '" class="subEvent-element card" data-id="' + subEvent.id + '" class="card" draggable="true" ondragstart="drag(event)">' +
        '<div class="sub-event-card-container card-body">' +
        '    <div class="sub-event-name"><b>' + subEvent.name_nb + '</b></div>' +
        '        <div class="center-content sub-event-dateime">' +
        '             <i>' + subEvent.start_date + ' - ' + subEvent.end_date + '</i>' +
        '        </div>\n' +
        '         <div class="sub-event-button-container">' +
        '          <div class="delete-sub-event-button center-content">' +
        '             <img class="img-cross" src="/static/img/circle-x.svg" alt="exit"></div>' +
        '         </div>' +
        '        </div>' + '</div>');


    $(".delete-sub-event-button").click((e) => {
        const event = e || window.event
        const value = $(event.target).closest(".subEvent-element").attr('data-id')
        subEvents = subEvents.filter(item => item.id != value)
        $(event.target).closest(".subEvent-element").remove()
    })

}

function addCategory(category) {
    $("#subEvents").append(
        '<div class=" collapse show" aria-labelledby="headingOne" >' +
        '   <div class="card-header">\n' + category.name_nb + '</div>' +
        '   <div class="drag-container card-body" data-id="' + category.id + '" ondrop="drop(event)"' +
        ' ondragover="allowDrop(event)" style="text-align: center; border: green dashed 1px;">' +
        '       Drop sub-event here' +
        '   </div>' +
        '     ' +
        '</div>')
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

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    const data = ev.dataTransfer.getData("text");
    const container = $(ev.target).closest('.drag-container');
    const subEventElement = $(("#" + data))
    container.append(subEventElement);
    const dataIDSubEvent = subEventElement.attr("data-id")

    subEvents.map((element) => {
        if (element.id == dataIDSubEvent) {
            element.category = container.attr("data-id");
        }
    })
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

