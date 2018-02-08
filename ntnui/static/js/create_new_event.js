//When document is ready, return from using post, and print message
$( () => {
    $("#create-event-button").click(() => {
        $(".alert").alert()
        const postData = $('#create-event-form').serialize()
        $.ajax({
            type: 'POST',
            url: '/events/api/create-event',
            data: postData,
            success: (data) => {
                console.log(data.message)
                const msg = data.message
                //Print the message to screen
                $(".alert-message-container").html(() => {
                    return "<div class=\"alert alert-success show fade \" role=\"alert\"> <strong>Sucsess:</strong> "+
                        msg +  "</div>"
                })
                //remove the alert box after 2 sec
                setTimeout( () => {
                    $(".alert").slideUp(500)
                    //redirects back to events
                    window.location.href = '../'
                    }, 1500)
            }, error: (data) => {
                //If error print the error msg in an alert box
                const msg = data.responseJSON.message
                $(".alert-message-container").html(() => {
                    return "<div class=\"alert alert-danger show fade \" role=\"alert\"> <strong>Error:</strong> " +
                        msg +  "</div>"
                })
                //remove the alert box after 2 sec
                setTimeout( () => {
                    $(".alert").slideUp(500)
                    }, 2000)
            }
        })
    })
})