// List of subEvents
let subEvents = [];

// list of categories
let categories = []

// subevent id counter
let idCounterSubEvent = 0;

// category id counter
let idCounterCategory = 1;

// used for security
let csrftoken

let eventID;


// used to know what element to edit
let editContainer = null;

// On document ready
$(() => {

    csrftoken = getCookie('csrftoken')


    $("#create-event-button").click((e) => {
        e.preventDefault()
        createEvent()
    })

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

        let img = $(button).closest(".collapse-header").find('img').first()
        if (img.attr("src") == "/static/img/chevron-bottom.svg") {
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
            if (editContainer) {
                let id = editContainer.attr('data-id')
                subEvent.id = id;
                editContainer.find('.subEvent-title').text(subEvent.name_nb)
                editContainer.find('.subEvent-date').text(subEvent.start_date + " - " + subEvent.end_date)

                subEvents = subEvents.map((item) => {
                    return item.id == id ? subEvent : item
                })
                editContainer = null
                $('#submit-sub-event-form').text(gettext("Create sub-event"))
            } else {
                subEvent.id = idCounterSubEvent;
                idCounterSubEvent++;
                subEvent.category = 0;
                addSubEvent(subEvent)
                subEvents.push(subEvent)
            }
            $("#subEvent-modal").modal('hide')
        }
    });


    $(".close-modal").click((e) => {
        const event = e || window.event
        const form = $(event.target).closest(".modal-content").find("form *")
        form.filter(':input').each((e, input) => {
            input.value = ""
        })
        editContainer = null;
        $('#submit-category-form').text(gettext("Create category"))
        $('#submit-sub-event-form').text(gettext("Create sub-event"))

    })

    $(".modal").click((e) => {
        const event = e || window.event
        const form = $(event.target).find("form *")
        form.filter(':input').each((e, input) => {
            input.value = ""
        })
        editContainer = null;
        $('#submit-category-form').text(gettext("Create category"))
        $('#submit-sub-event-form').text(gettext("Create sub-event"))

    })

    $("#submit-category-form").click((e) => {
        e.preventDefault()

        let form = $('#category-data-form *');
        let category = validateForm(form);
        if (category) {
            $("#category-modal").modal('hide')
            if (editContainer) {
                let id = editContainer.find('.drag-container').attr('data-id')
                category.id = id;
                editContainer.find('.category-title').text(category.name_nb)

                categories = categories.map((item) => {
                    return item.id == id ? category : item
                })
                editContainer = null;
                $('#submit-category-form').text(gettext("Create category"))
            } else {
                category.id = idCounterCategory;
                addCategory(category)
                idCounterCategory++;
                categories.push(category)
            }

        }

    })
});

function createEvent() {
    let form = $('#create-event-form *')
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
}

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
    let subEventsCreated = await Promise.all(subEvents.map(async (subEvent) => {
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
        window.location.replace("/events/" + eventID + "/");
    }
}


function validateForm(formElements) {
    let valid = true
    formElements.filter(':input').each((e, input) => {
        if (!validateInput(input)) {
            valid = false;
        }
    })
    if (valid) {
        let element = {};
        formElements.filter(':input').each((e, input) => {
            if (input.name != "csrfmiddlewaretoken") {
                element[input.name] = input.value;
                input.value = "";
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
    const input = event.target
    validateInput(input)

}

/**
 * Validates a given input field
 * @param input
 * @returns {boolean}
 */
function validateInput(input) {
    // Use to see if field is displaying error
    const dispError = $(input).next().length === 0;

    // If field is of type datetime-local
    if ($(input).attr("type") === 'datetime-local' && $(input).attr("required") ) {
        return validateDate(input, dispError)
    }
    // if filed is not valid, and error is currently not displayed. Display error
    else if (!input.checkValidity()) {
        if (dispError) {
            $(input).after(getAlert(gettext('invalid input')));
        }
    } else {
        // If filed is valid, remove error
        $(input).next(".error-input").remove()
        return true;
    }
    return false;
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
        return true;
    }
    return false;
}


function addSubEvent(subEvent) {
    let container = $("#subEvents")
    container.find('p').remove()
    container.append(
        '<div id="subEvent-' + subEvent.id + '" class="subEvent-element card" data-id="' + subEvent.id + '" class="card" draggable="true" ondragstart="drag(event)">' +
        '<div class="sub-event-card-container card-body">' +
        '    <div class="sub-event-name"><b class="subEvent-title">' + subEvent.name_nb + '</b></div>' +
        '        <div class="center-content sub-event-dateime">' +
        '             <i class="subEvent-date">' + subEvent.start_date + ' - ' + subEvent.end_date + '</i>' +
        '        </div>\n' +
        '         <div class="sub-event-button-container">' +
        '<div class="btn-group" role="group" style="float:right;">' +
        '  <button type="button" class="center-content btn btn-warning edit-subEvent"><img class="img-cross" src="/static/img/pencil.svg" alt="edit"></button>\n' +
        '  <button type="button" class="center-content btn btn-danger delete-sub-event"><img class="img-cross" src="/static/img/x.svg" alt="exit"></button></div>\n' +
        '</div>' +
        '        </div>' + '</div>');

    $(".delete-sub-event").click((e) => {
        const event = e || window.event
        const value = $(event.target).closest(".subEvent-element").attr('data-id')
        subEvents = subEvents.filter(item => item.id != value)
        $(event.target).closest(".subEvent-element").remove()
        if (!container.find('div').length) {
            container.append('<p style="text-align: center; padding:2rem;">Create a category or a sub-event to get' +
                '            started!</p>')
        }
    })

    $(".edit-subEvent").click((e) => {
        const event = e || window.event
        editContainer = $(event.target).closest(".subEvent-element")
        const id = editContainer.attr('data-id')
        subEvent = subEvents.filter(item => item.id == id)


        $('#subEvent-data-form *').filter(':input').each((e, input) => {
            const value = subEvent[0][input.name]
            input.value = value;
        })
        $('#submit-sub-event-form').text(gettext("Save"))
        $("#subEvent-modal").modal('show')
    })

}

function addCategory(category) {
    let container = $("#subEvents")
    container.find('p').remove()
    container.append(
        '<div class="category-card collapse show" aria-labelledby="headingOne" >' +
        '   <div class="card-header category-header"><h5 class="category-title">' + category.name_nb +
        '</h5><div class="button-container-right">' +
        '<div class="btn-group" role="group">' +
        '  <button type="button" class="center-content btn btn-warning edit-category"><img class="img-cross" src="/static/img/pencil.svg" alt="edit"></button>' +
        '  <button type="button" class="center-content btn btn-danger delete-category"><img class="img-cross" src="/static/img/x.svg" alt="exit"></button></div>' + '</div></div>' +
        '   <div class="drag-container card-body" data-id="' + category.id + '" ondrop="drop(event)"' +
        ' ondragover="allowDrop(event)" style="text-align: center; border: lightgrey solid 1px;">' +
        '<div class="drop-example" ><i> Drop sub-event here </i></div>' +
        '   </div>' +
        '     ' +
        '</div>')


    $(".delete-category").click((e) => {
        const event = e || window.event
        const value = $(event.target).closest(".category-card").find('.drag-container').attr('data-id')
        categories = categories.filter(item => item.id != value)
        subEvents = subEvents.filter((subEvent) => subEvent.category != value)
        $(event.target).closest(".category-card").remove()
        if (!container.find('div').length) {
            container.append('<p style="text-align: center; padding:2rem;">Create a category or a sub-event to get' +
                '          started!</p>')
        }
    })
    $(".edit-category").click((e) => {
        const event = e || window.event
        editContainer = $(event.target).closest(".category-card")
        const value = editContainer.find('.drag-container').attr('data-id')
        category = categories.filter(item => item.id == value)


        $('#category-data-form *').filter(':input').each((e, input) => {
            const value = category[0][input.name]
            input.value = value;
        })

        $('#submit-category-form').text(gettext("Save"))

        $("#category-modal").modal('show')
    })
}

function showSubEventPlaceholder() {
    return '<div class="drop-example" ><i> Drop sub-event here </i></div>'
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
    ev.stopPropagation()
    ev.preventDefault();

    const data = ev.dataTransfer.getData("text");
    const container = $(ev.target).closest('.drag-container');
    const subEventElement = $(("#" + data))
    container.append(subEventElement);

    const dataIDSubEvent = subEventElement.attr("data-id")

    subEventElement.closest('.drag-container').find('.drop-example').first().remove();
    subEvents = subEvents.map((element) => {
        if (element.id == dataIDSubEvent) {
            element.category = container.attr("data-id");
        }
        return element;
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

