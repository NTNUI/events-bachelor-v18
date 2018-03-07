/**
 * When the document have loaded, add listener to attend-event-button and send ajax.
 */
$(() => {
    $("#attend-event-button").click(() => {
        const csrftoken = getCookie('csrftoken');
        const pathArray = window.location.pathname.split( '/' );
        const id = pathArray[3]
        $.ajax({
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrftoken,
                id:id
            },
            url: '/ajax/events/attend-event',
            success: (data) => {

            }, error: (data) => {

            }
        })
    })
})

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

