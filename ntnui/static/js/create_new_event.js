/**
 * When the document have loaded, add listener to create-event-button and send ajax.
 */
$(() => {
    $("#create-event-button").click(() => {
        const postData = $('#create-event-form').serialize()
        $.ajax({
            type: 'POST',
            url: '/ajax/events/add-event',
            data: postData,
            success: (data) => {
                //show success alert
                printMessage('success', data.message)
                slideUpAlert(true)
            }, error: (data) => {
                //show error alert
                printMessage('error', data.responseJSON.message)
                slideUpAlert(false)
            }
        })
    })
})

/**
 * Prints message to screen, using a dialog box
 * @param msgType
 * @param msg
 */
function printMessage(msgType, msg) {

    //checks the msgType, to get the right color for the alert
    let type = ''
    switch (msgType){
        case 'error':
            type = 'danger'
            break
        case 'success':
            type = 'success'
            break
    }
    //print message to screen
    $(".alert-message-container").html(() => {
        return "<div class=\"alert alert-"+type+" show fade \" role=\"alert\"> <strong>"+ msgType + ":</strong>" +
            " "+ msg +  "</div>"
    })
}

/**
 * Slides up the alert, if redirect set, the user will be returned to last page.
 * @param redirect
 */
function slideUpAlert(redirect) {

    //set timeout
    setTimeout( () => {
        //slide up the alert
    $(".alert")
    if(redirect){
        window.location.href = '/events'
    }
    //sets the amount of ms before the alert is closed
    })
}

var form = document.getElementById('create-event-form');
var name_no = document.getElementsByName("name_no")[0];
var name_en = document.getElementsByName("name_en")[0];
var start_date = document.getElementsByName("start_date")[0];
var end_date = document.getElementsByName("end_date")[0];
var description_text_no = document.getElementsByName("description_text_no")[0];
var description_text_en = document.getElementsByName("description_text_en")[0];


function validateName_no() {
    if (!name_no.checkValidity()) {

        document.getElementById("name_no_message").innerHTML = "Invalid input!";

    }
    else{
        document.getElementById("name_no_message").innerHTML = "";
    }
}

function validateName_en(){
    if (!name_en.checkValidity()) {

        document.getElementById("name_en_message").innerHTML = "Invalid input!";
    }
    else{
        document.getElementById("name_en_message").innerHTML = "";
    }
    }

function validateStart_date(){
    var today = new Date().toISOString();

    today = today.slice(0, -8);
    var input_End_date = end_date.value.toLocaleString();
    var input_Start_date = start_date.value.toLocaleString();

    if (!(input_Start_date > today)){
        start_date.setCustomValidity("Invalid date!");
        document.getElementById("start_date_message").innerHTML = start_date.validationMessage;
    }
    else if(!(input_End_date=="")) {
        if (!(input_End_date > input_Start_date)) {
            start_date.setCustomValidity("Start date is not before end date!");
            document.getElementById("start_date_message").innerHTML = start_date.validationMessage;
        }
    }
    else{
        document.getElementById("start_date_message").innerHTML = "";
    }
}

function validateEnd_date(){
    var today = new Date().toISOString();
    today = today.slice(0, -8);
    var input_Start_date = start_date.value.toLocaleString();
    var input_End_date = end_date.value.toLocaleString();
    if (!(input_Start_date > today)){
        end_date.setCustomValidity("Invalid date!");
        document.getElementById("end_date_message").innerHTML = start_date.validationMessage;
    }
    else if(!(input_End_date > input_Start_date)){
        end_date.setCustomValidity("End date is not after start date!");
        document.getElementById("end_date_message").innerHTML = end_date.validationMessage;
    }
    else{
        document.getElementById("end_date_message").innerHTML = "";
    }
}

function validateDescription_text_no() {
    if (!description_text_no.checkValidity()) {
        document.getElementById("description_no_message").innerHTML = "Empty field!";
    }
    else{
        document.getElementById("description_no_message").innerHTML = "";

    }
}

function validateDescription_text_en(){
    if (!description_text_en.checkValidity()) {
        document.getElementById("description_en_message").innerHTML = "Empty field";
    }
    else{
        document.getElementById("description_en_message").innerHTML = "";

    }
}
form.addEventListener("submit", function (event) {
  // Each time the user tries to send the data, we check
  // if the email field is valid.
  if (!(name_no.validity.valid || name_en.validity.valid || start_date.validity.valid || end_date.validity.valid
      || description_text_no.validity.valid || description_text_en.validity.valid )) {
    // And we prevent the form from being sent by canceling the event
    event.preventDefault();
  }
}, false);