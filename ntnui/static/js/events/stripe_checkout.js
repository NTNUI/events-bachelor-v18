var handler = StripeCheckout.configure({
    key: 'pk_test_TagT9jGDj7CN9NOQfTnueTxz',
    image: "/static/img/ntnui2.svg",
    locale: 'auto',
    token: function (token) {
        console.log(token)
        const csrftoken = getCookie('csrftoken');
        $.ajax({
        dataType: "json",
        type: "POST",
        url: '/ajax/events/5/payment',
        data: {
            csrfmiddlewaretoken: csrftoken,
            stripeToken: token.id,
            stripEmail:token.email
        },
        success: data => {
            console.log(data);
        },
        error: data => {
            console.log(data);
        }
        });
    }
});
document.getElementById('customButton').addEventListener('click', function (e) {
    // Open Checkout with further options:
    const price = parseInt($("#price").text().replace(/[^0-9]/g,''))

    handler.open({
        amount:price*100,
        currency: "nok",
        name: 'test',
        description: 'test',
        email: "pci@mail.com",
    });
    e.preventDefault();

});

// Close Checkout on page navigation:
window.addEventListener('popstate', function () {
    handler.close();
});

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

