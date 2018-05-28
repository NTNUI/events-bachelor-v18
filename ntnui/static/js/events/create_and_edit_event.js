// List of subEvents
let subEvents = [];

// list of categories
let categories = [];

// sub-event id counter
let idCounterSubEvent = 0;

// category id counter, set to 1 as 0 is the default category
let idCounterCategory = 0;

// used for security, required by django in order to accept the request
let csrftoken;

// The edit container specify, what DOM element is currently being eddied
let editContainer = null;

// sets the current language
let lang

// If the event already exists it will have a eventID
let eventID = null;

// define URLS used to create and edit
const URL_EVENT_CREATE = "/ajax/events/create-event"
const URL_EVENT_EDIT = "/ajax/events/edit-event"

const URL_SUB_EVENT_CREATE = "/ajax/events/create-sub-event"
const URL_SUB_EVENT_EDIT = "/ajax/events/edit-sub-event"

const URL_CATEGORY_CREATE = "/ajax/events/create-category"
const URL_CATEGORY_EDIT = "/ajax/events/edit-category"

// On document ready
$(() => {

    // If this is a event that is going to be eddited, sub-event/ the event id
    eventID = $('#event-id').val()
    if (eventID) {
        getEventFromServer();
    }

    // get the language
    lang = $('html').attr('lang')

    // Sets the csrftoken
    csrftoken = getCookie('csrftoken')

    // Button used to create the event
    $("#create-event-button").click(sendRequestToCreateEvent);

    // Button to show the sub-event modal
    $("#add-subEvent-button").click(function (e) {
        e.stopPropagation();
        $("#subEvent-modal").modal('show')
    });

    // Button used to show the category modal
    $("#add-category-button").click(function (e) {
        e.stopPropagation();
        $("#category-modal").modal('show')
    });

    // Finds and set the subEvent container
    const subEventContainer = $('#subEvents')

    // Add listeners to delete and edit buttons
    subEventContainer.on('click', ".delete-sub-event", deleteSubEvent)
    subEventContainer.on('click', ".edit-subEvent", editSubEvent)
    subEventContainer.on('click', ".delete-category", deleteCategory)
    subEventContainer.on('click', ".edit-category", editCategory)

    // add listener to all the event form fields
    $(".form-input-create-event").blur(validateInputOnBlur);

    // add listener to all the subEvent form fields
    $(".form-input-create-subEvent").blur(validateInputOnBlur);

    // add listener to all the subEvent form fields
    $(".form-input-create-category").blur(validateInputOnBlur);

    // OnClick for submit subEvent button
    $("#submit-sub-event-form").click(validateAndCreateSubEvent);

    // onClick for submit category button
    $("#submit-category-form").click(validateAndCreateCategory);

    // If the user press the close button on a modal, delete its input values
    $(".close-modal").click((e) => {
        const event = e || window.event
        closeModal($(event.target).closest(".modal-content").find("form *"));
    })

    // Used to change the arrow on collapsible elements
    $(".card-header").click(updateArrow);

    // If the user press the x in the right corner, delete the modals content
    $(".close").click((e) => {
        const event = e || window.event
        closeModal($(event.target).closest(".modal-content").find("form *"));

    })

    // If the user presses outside the modal, delete is input content
    $(".modal").click((e) => {
        const event = e || window.event
        if (!$(event.target).closest(".modal-content").length) {
            closeModal($(event.target).find("form *"));
        }
    })

    $("#delete-event-button").click((e) => {
        $("#deleteModal").modal("show")
    })

    // Add eventlistener for delete event modal button
    $("#delete-event-button-modal").click(deleteEvent)

});

/**
 * Getts the eventInfo from the server
 * @returns {null}
 */
async function getEventFromServer() {
    try {
        // Get all the events data from the server
        let data = await $.ajax({
            type: 'GET',
            url: '/ajax/events/' + eventID,
        })
        idCounterCategory = 0;
        // Filter the categories such that they are on the decried format and add them to the categories list
        categories = data.categories.map((category) => {
            idCounterCategory++;
            const norwegianDescription = category.descriptions.filter((description) => description.language === 'nb')[0]
            const englishDescription = category.descriptions.filter((description) => description.language === 'en')[0]
            if (norwegianDescription.name === "Ikke kategorisert") {
                return null
            }
            return {
                serverID: category.id,
                id: idCounterCategory,
                name_nb: norwegianDescription.name,
                name_en: englishDescription.name,
            }
        }).filter((category) => category !== null)

        // filter and add the sub-events to the subevent list
        for (category of data.categories) {
            //Add subEvents to the subEvents list
            subEvents.push.apply(subEvents, category["sub-events"].map((subEvent) => {

                // Set the serverID equal to the id provided bt the sever, and set the id = to the clients id counter
                subEvent.serverID = subEvent.id
                subEvent.id = idCounterSubEvent;

                // Increment the id counter for the subEvent
                idCounterSubEvent++;

                // Get the descriptions
                const norwegianDescription = subEvent.descriptions.filter((description) => description.language === 'nb')[0]
                const englishDescription = subEvent.descriptions.filter((description) => description.language === 'en')[0]

                // Set subEvent data
                subEvent.name_nb = norwegianDescription.name
                subEvent.email_nb = norwegianDescription.custom_email_text
                subEvent.name_en = englishDescription.name
                subEvent.email_en = englishDescription.custom_email_text
                delete subEvent.descriptions
                return subEvent
            }))
        }

        // Show the content
        setInVisualContent()

    } catch
        (error) {
        //show error alert
        printMessage('error', error)
    }
}


/**
 * Deletes the given event
 * @returns {Promise.<void>}
 */
let deleteEvent = async () => {
    try {
        let result = await $.ajax({
            type: 'GET',
            url: '/ajax/events/delete/' + eventID,
        });
        if (result) {
            printMessage('success', result.message)
            setTimeout(() => {
                window.location.replace("/events");
            }, 2000)
        }
    } catch (error) {
        if (error.responseJSON) {
            printMessage('error', error.responseJSON.message)
        } else {
            printMessage('error', gettext("Your request could not be processed"))
        }
    }
}


/**
 * Displays the categories and sub-events currently in categories and subEvents
 */
function setInVisualContent() {
    for (category of categories) {
        showCategory(category)
    }

    for (subEvent of subEvents) {
        showSubEvent(subEvent, true)
    }
}

/**
 * Sends request to server, in order to create event
 * @param e
 */
let sendRequestToCreateEvent = (e) => {
    e.preventDefault()

    let form = $('#create-event-form *')
    let event = validateForm(form, true)
    if (event) {
        // Sends request to server to create event
        event.csrfmiddlewaretoken = csrftoken;
        $.ajax({
            type: 'POST',
            url: eventID ? URL_EVENT_EDIT : URL_EVENT_CREATE,
            data: event,
            success: (data) => {
                createCategories(data.id)
            },
            error: (data) => {
                //show error alert
                printMessage('error', data.responseJSON.message)
            }
        })
    }
}


/**
 * Updates the arrows in the collapsible menus
 * @param e
 */
let updateArrow = (e) => {
    // set event to e or window.event in order to support most browsers
    const event = e || window.event;

    // Find the container and the img tag
    const collapseHeader = $(event.target).closest(".collapse-header");
    const img = collapseHeader.find('img').first();

    // Set the arrow based on the aria-expanded attribute
    if (collapseHeader.attr("aria-expanded") === "false") {
        img.attr("src", "/static/img/chevron-top.svg");
    }
    else {
        img.attr("src", "/static/img/chevron-bottom.svg");
    }
}

/**
 * Takes in the modal form, and deletes its content
 * The function also replaces all the modal buttons to Create rather then save.
 * @param formElement
 */
function closeModal(formElement) {
    formElement.filter(':input').each((e, input) => {
        input.value = ""
    })
    // if the last state was edit( that is the editContainer is not null), change the button text
    if (editContainer) {
        $('#submit-category-form').text(gettext("Create category"))
        $('#submit-sub-event-form').text(gettext("Create sub-event"))
        editContainer = null;
    }
}


/**
 * Function used to add a new category to the categories list.
 * If the category already exists this function will also update it
 * @param e
 */
let validateAndCreateCategory = (e) => {
    e.preventDefault()

    // Find the form
    const form = $('#category-data-form *');

    // Validate the form inputs
    let category = validateForm(form);
    if (category) {
        // Check if the user is editing or creating a new category
        if (editContainer) {
            // Get the container id, that is the category id
            const id = editContainer.find('.drag-container').attr('data-id')

            category.id = id;
            editContainer.find('.category-title').text(lang === 'nb' ? category.name_nb : category.name_en)

            // Find and replace the old category with the new one
            categories = categories.map((item) => {
                if (item.id == id) {
                    category.serverID = item.serverID
                    return category
                }
                return item
            })

            // Reset the exit settings
            editContainer = null;
            $('#submit-category-form').text(gettext("Create category"))
        } else {
            // Increment the id counter
            idCounterCategory++;

            // set the category id
            category.id = idCounterCategory;

            // Show the new category
            showCategory(category)


            // Push the new category
            categories.push(category)
        }
        // Close the category modal
        $("#category-modal").modal('hide')
    }
}

/**
 * Function used to add a new subEvent to the subEvents list.
 * If the subEvent already exists this function will also update it
 * @param e
 */
let validateAndCreateSubEvent = (e) => {
    e.preventDefault()
    // Get the from and all its elements, thus the *
    form = $('#subEvent-data-form *')
    // Validate the form
    let subEvent = validateForm(form)
    if (subEvent) {

        // Check if the user is editing or creating a new sub-event
        if (editContainer) {
            // Get the container id, that is the sub-event id
            const id = editContainer.attr('data-id')

            // since we created a new subEvent from the form, we need to set the sub-event id equal to the old
            subEvent.id = id;

            // Updates the name based on the current language
            editContainer.find('.subEvent-title').text(lang === 'nb' ? subEvent.name_nb : subEvent.name_en)
            // Updates the date
            editContainer.find('.subEvent-date').text(formatDate(subEvent.start_date) + " - " + formatDate(subEvent.end_date))

            // Find the subEvent with the same id, and replace it with the new one
            subEvents = subEvents.map((item) => {
                if (item.id == id) {
                    subEvent.category = item.category
                    subEvent.serverID = item.serverID
                    return subEvent
                }
                return item
            })

            // Reset modal to create
            editContainer = null
            $('#submit-sub-event-form').text(gettext("Create sub-event"))
        } else {
            // Give the subEvent its unique id
            subEvent.id = idCounterSubEvent;

            // increment the idCounter
            idCounterSubEvent++;

            // Sets is category to default
            subEvent.category = 0;

            // Create the visible subEvent element
            showSubEvent(subEvent)

            // Add the subEvent to the list of subEvents
            subEvents.push(subEvent)
        }
        // Close the subEvent modal
        $("#subEvent-modal").modal('hide')
    }
}

/**
 * Sends a ajax request to the server, in order to create the categories
 * @param eventID
 * @returns {Promise.<void>}
 */
async function createCategories(eventID) {
    categories = await Promise.all(categories.map(async (category) => {
        category.csrfmiddlewaretoken = csrftoken
        category.event = eventID
        try {
            let url = URL_CATEGORY_CREATE
            let id = category.id
            if (category.serverID) {
                category.id = category.serverID
                url = URL_CATEGORY_EDIT
            }
            let data = await $.ajax({
                type: 'POST',
                url: url,
                data: category
            })
            if (data) {
                category.serverID = data.id;
                category.id = id;
                return category
            }
        } catch (error) {
            //show error alert
            printMessage('error', error.responseJSON.message)
            return category
        }
    }))
    createSubEvents(eventID)
}


/**
 * Sends a ajax request to the sever in order to create the subEvents
 * @param eventID
 * @returns {Promise.<void>}
 */
async function createSubEvents(eventID) {
    let subEventsCreated = await Promise.all(subEvents.map(async (subEvent) => {
        let category = categories.filter((category) => category.id == subEvent.category)
        subEvent.category = category.length ? category[0].serverID : ""
        subEvent.csrfmiddlewaretoken = csrftoken
        subEvent.event = eventID
        try {
            let url = URL_SUB_EVENT_CREATE
            if (subEvent.serverID) {
                url = URL_SUB_EVENT_EDIT
                subEvent.id = subEvent.serverID;
            }
            let data = await $.ajax({
                type: 'POST',
                url: url,
                data: subEvent,
            })
            return subEvent
        } catch (error) {
            //show error alert
            console.error(error)
        }
    }))
    if (subEventsCreated) {
        window.location.replace("/events/" + eventID + "/");
    }
}

/**
 * Deletes the subEvent with the given id
 * @param eventID
 * @returns {Promise.<void>}
 */
async function deleteSubEventFromServer(eventID) {
    try {
        let data = await $.ajax({
            type: 'POST',
            url: '/ajax/events/delete-sub-event',
            data: {
                id: eventID,
                csrfmiddlewaretoken: csrftoken,
            }
        })

    } catch (error) {
        //show error alert
        printMessage('error', error)
    }
}

/**
 * Deletes the category with the given id
 * @param categoryID
 * @returns {Promise.<void>}
 */
async function deleteCategoryFromServer(categoryID) {
    try {
        let data = await $.ajax({
            type: 'POST',
            url: '/ajax/events/delete-category',
            data: {
                id: categoryID,
                csrfmiddlewaretoken: csrftoken,
            }
        })

    } catch (error) {
        console.error(error)
        //show error alert
        printMessage('error', error)
    }
}

/**
 * Validate a given input in a form
 * @param e
 */
let validateInputOnBlur = (e) => {
    // Get the button that was pressed
    const event = e || window.event
    validateInput(event.target)
}

function validateForm(formElements, keepData) {
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
                if (!keepData) {
                    input.value = "";
                }

            }
        });
        return element
    }
    return null
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
    if ($(input).attr("type") === 'datetime-local' && $(input).attr("required")) {
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

function showSubEvent(subEvent, fromServer) {

    // Find the subEvent container
    let container = $("#subEvents")

    // If the event allready exists, place it in the right container
    if (fromServer) {
        // Find the category
        const category = categories.filter((category) => category.serverID == subEvent.category_id)
        if (category.length) {
            subEvent.category = category[0].id;
        } else {
            subEvent.category = 0;
        }

        subEvents = subEvents.map((subEventMap) => {
            if (subEventMap.id === subEvent.id) {
                return subEvent;
            }
            return subEventMap
        })
        // Use te category id to find the container, if the category dose not exist place it in the default container
        if (category.length) {
            const id = category[0].id
            container = $('.drag-container').filter(function () {
                return $(this).attr("data-id") === (id).toString()
            })
            // Remove drop-example
            container.closest('.drag-container').find('.drop-example').first().remove();
        }
    }

    // If the container contains a example text remove it
    container.find('p').remove()

    // find the right title
    const title = lang === 'nb' ? subEvent.name_nb : subEvent.name_en

    // Append the container with the sub-event element
    container.append(
        '<div id="subEvent-' + subEvent.id + '" class="subEvent-element card" data-id="' + subEvent.id + '" ' +
        'draggable="true" ondragstart="drag(event)">' +
        ' <div class="sub-event-card-container card-body">' +
        '    <div class="sub-event-name"><b class="subEvent-title">' + title + '</b></div>' +
        '        <div class="center-content sub-event-dateime">' +
        '             <i class="subEvent-date">' + formatDate(subEvent.start_date) + ' - ' + formatDate(subEvent.end_date) + '</i>' +
        '        </div>\n' +
        '         <div class="sub-event-button-container">' +
        '  <div class="btn-group" role="group" style="float:right;">' +
        '    <button type="button" class="center-content btn btn-warning edit-subEvent"><img class="img-cross" src="/static/img/pencil.svg" alt="edit"></button>' +
        '    <button type="button" class="center-content btn btn-danger delete-sub-event"><img class="img-cross" src="/static/img/x.svg" alt="exit"></button></div>' +
        '   </div>' +
        ' </div>' +
        '</div>');
}


//onClick for edit subevent
let editSubEvent = (e) => {
    const event = e || window.event


    // Set the edit container
    editContainer = $(event.target).closest(".subEvent-element")
    const id = editContainer.attr('data-id')

    // Find the given subevent
    let subEvent = subEvents.filter(item => item.id == id)

    // Set the form values
    $('#subEvent-data-form *').filter(':input').each((e, input) => {
        const value = subEvent[0][input.name]
        input.value = value;
    })

    // Update the button and show the form
    $('#submit-sub-event-form').text(gettext("Save"))
    $("#subEvent-modal").modal('show')
}


// onClick for the delete SubEvent button7
let deleteSubEvent = (e) => {
    e.stopPropagation()
    e.preventDefault()

    const event = e || window.event

    // Find the id
    const id = $(event.target).closest(".subEvent-element").attr('data-id')

    // Remove the given element from the list
    subEvents = subEvents.filter(item => {
        if (item.id != id) {
            return true
        } else {
            subEvent = item;
            return false
        }
    })

    // Remove the element
    $(event.target).closest(".subEvent-element").remove()

    // iF the container contains no elements, put the help text back
    const container = $("#subEvents");
    if (!container.find('div').length) {
        container.append(getContainerPlaceholder());
    }
    if (subEvent.serverID) {
        deleteSubEventFromServer(subEvent.serverID)
    }
}

function showCategory(category) {
    // Find the container to be appended
    let container = $("#subEvents")

    // Remove any help text that may be set
    container.find('p').remove()

    // find the right title
    const title = lang === 'nb' ? category.name_nb : category.name_en

    // Add the category
    container.append(
        '<div class="category-card collapse show" aria-labelledby="headingOne" >' +
        '   <div class="card-header category-header">' +
        '       <h5 class="category-title">' + title + '</h5>' +
        '       <div class="button-container-right">' +
        '          <div class="btn-group" role="group">' +
        '             <button type="button" class="center-content btn btn-warning edit-category">' +
        '                   <img class="img-cross" src="/static/img/pencil.svg" alt="edit"></button>' +
        '             <button type="button" class="center-content btn btn-danger delete-category">' +
        '                <img class="img-cross" src="/static/img/x.svg" alt="exit"></button>' +
        '           </div>' +
        '       </div>' +
        '   </div>' +
        '   <div class="drag-container card-body" data-id="' + category.id + '" ondrop="drop(event)"' +
        '       ondragover="allowDrop(event)" style="text-align: center; border: lightgrey solid 1px;">' +
        '       <div class="drop-example" ><i> Drop sub-event here </i>' +
        '       </div>' +
        '   </div>' +
        '</div>')
}


// onClick for delete category
let deleteCategory = (e) => {
    const event = e || window.event

    // Find the category id
    const id = $(event.target).closest(".category-card").find('.drag-container').attr('data-id')

    // Remove the category with the given id
    categories = categories.filter(item => {
        if (item.id != id) {
            return true;
        } else {
            category = item;
            return false;
        }
    })

    // Delete all subEvents in the category
    subEvents = subEvents.filter((subEvent) => subEvent.category != id)

    // Remove the visible category
    $(event.target).closest(".category-card").remove()

    const container = $("#subEvents");
    // IF the element no longer contains any elements, show the help text
    if (!container.find('div').length) {
        container.append(getContainerPlaceholder())
    }

    if (category.serverID) {
        deleteCategoryFromServer(category.serverID)
    }
}

// onClick for edit category
let editCategory = (e) => {
    const event = e || window.event

    // Set the edit container
    editContainer = $(event.target).closest(".category-card")

    // Find the category id
    const id = editContainer.find('.drag-container').attr('data-id')
    // Find the category with the given id
    const category = categories.filter(item => item.id == id)

    // Place the values in the form
    $('#category-data-form *').filter(':input').each((e, input) => {
        const value = category[0][input.name]
        input.value = value;
    })

    // Uodate the create button and show the form
    $('#submit-category-form').text(gettext("Save"))
    $("#category-modal").modal('show')
}

/**
 * Returnes the placeholder used in the subEvent container
 * @returns {string}
 */
function getContainerPlaceholder() {
    return '<p class="placeholder-container-text">' + gettext('Create a category or a sub-event to get started') + '</p>'
}

function formatDate(dateString) {
    return dateString.replace("T", " ")
}

function allowDrop(ev) {
    ev.preventDefault();
}

/**
 * On subEvent drag
 * @param ev
 */
function drag(ev) {
    ev.dataTransfer.setData("sub-event-id", ev.target.id);
}

/**
 * On subEvent drop
 * @param ev
 */
function drop(ev) {
    ev.stopPropagation()
    ev.preventDefault();

    const subEventID = ev.dataTransfer.getData("sub-event-id");
    const container = $(ev.target).closest('.drag-container');
    const subEventElement = $(("#" + subEventID))

    // Append the subEvent to the new container
    container.append(subEventElement);

    // Get the subEvent id
    const dataIDSubEvent = subEventElement.attr("data-id")

    // Remove drop-example
    subEventElement.closest('.drag-container').find('.drop-example').first().remove();

    //Update subEvents, with the new categoryID
    subEvents = subEvents.map((element) => {
        if (element.id == dataIDSubEvent) {
            element.category = container.attr("data-id");
        }
        return element;
    })
}

/**
 * from django website https://docs.djangoproject.com/en/2.0/ref/csrf/
 * @param name
 * @returns {*}
 */
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
