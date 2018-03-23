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
//get form inputs
var form = document.getElementById('create-event-form');
var name_no = document.getElementsByName("name_no")[0];
var name_en = document.getElementsByName("name_en")[0];
var start_date = document.getElementsByName("start_date")[0];
var end_date = document.getElementsByName("end_date")[0];
var description_text_no = document.getElementsByName("description_text_no")[0];
var description_text_en = document.getElementsByName("description_text_en")[0];

//check whether name_no input is valid and make a message pop up if invalid
function validateName_no() {

    if (!name_no.checkValidity()) {
        document.getElementById("name_no_message").innerHTML = gettext("Invalid input!");
        $("#name-no-alerter").show();
    }
    else{
        document.getElementById("name_no_message").innerHTML = "";
        $("#name-no-alerter").hide();
    }
}

//check whether name_en input is valid and make a message pop up if invalid
function validateName_en(){
    if (!name_en.checkValidity()) {

        document.getElementById("name_en_message").innerHTML = gettext("Invalid input!");
        $("#name-en-alerter").show();
    }
    else{
        document.getElementById("name_en_message").innerHTML = "";
        $("#name-en-alerter").hide();
    }
    }

//check whether start_date input is valid and make a message pop up if invalid
function validateStart_date(){
    //create date today
    var today = new Date().toISOString();
    //slice seconds and timezone
    today = today.slice(0, -8);
    //get end date and start date
    var input_End_date = end_date.value.toLocaleString();
    var input_Start_date = start_date.value.toLocaleString();

    //check whether start_date is after current date
    if (!(input_Start_date > today)){
        start_date.setCustomValidity(gettext("Invalid date!"));
        document.getElementById("start_date_message").innerHTML = start_date.validationMessage;
        $("#start-date-alerter").show();
    }
    //if end date is already entered, check whether start date is before it
    else if(!(input_End_date=="") && !(input_End_date > input_Start_date)) {
            start_date.setCustomValidity(gettext("Start date is not before end date!"));
            document.getElementById("start_date_message").innerHTML = start_date.validationMessage;
            $("#start-date-alerter").show();
    }
    else{
        start_date.setCustomValidity("");
        document.getElementById("start_date_message").innerHTML = "";
        $("#start-date-alerter").hide();
    }
}
////check whether end_date input is valid and make a message pop up if invalid
function validateEnd_date(){
    //create date today
    var today = new Date().toISOString();
    //slice seconds and timezone
    today = today.slice(0, -8);
    //get start date and end date
    var input_Start_date = start_date.value.toLocaleString();
    var input_End_date = end_date.value.toLocaleString();
    //check whether end date is before today
    if (!(input_End_date > today)){
        end_date.setCustomValidity(gettext("Invalid date!"));
        document.getElementById("end_date_message").innerHTML = start_date.validationMessage;
        $("#end-date-alerter").show();
    }

    //check whether end date is after start date
    else if(!(input_End_date > input_Start_date)){
        end_date.setCustomValidity(gettext("End date is not after start date!"));
        document.getElementById("end_date_message").innerHTML = end_date.validationMessage;
        $("#end-date-alerter").show();
    }
    else{
        end_date.setCustomValidity("");
        document.getElementById("end_date_message").innerHTML = "";
        $("#end-date-alerter").hide();
    }
}

//check whether description_text_no is valid and make a message pop up if invalid
function validateDescription_text_no() {
    if (!description_text_no.checkValidity()) {
        document.getElementById("description_no_message").innerHTML = gettext("Empty field!");
        $("#description-no-alerter").show();
    }
    else{
        document.getElementById("description_no_message").innerHTML = "";
        $("#description-no-alerter").hide();

    }
}

//check whether description_text_en is valid and make a message pop up if invalid
function validateDescription_text_en(){
    if (!description_text_en.checkValidity()) {
        document.getElementById("description_en_message").innerHTML = gettext("Empty field!");
        $("#description-en-alerter").show();

    }
    else{
        document.getElementById("description_en_message").innerHTML = "";
        $("#description-en-alerter").hide();

    }
}

//when clicking on create event at the end of the form, check if all fields are valid
//if they are valid, create the event
$(document).ready(function() {
    $("#create-event-button").click(function(e) {
        e.preventDefault();
        if (!name_no.validity.valid || !name_en.validity.valid || !start_date.validity.valid || !end_date.validity.valid
      || !description_text_no.validity.valid || !description_text_en.validity.valid ){
        $("div.alert-message-container").html("<p>Please validate all fields</p>");


        }
        else{
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
                    printMessage('error', data.responseJSON.message)
                    slideUpAlert(false)
                }
            })
        }}
    )
});