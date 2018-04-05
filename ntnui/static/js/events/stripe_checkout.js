var handler = StripeCheckout.configure({
    key: 'pk_test_TagT9jGDj7CN9NOQfTnueTxz',
    image: "/static/img/ntnui2.svg",
    locale: 'auto',
    token: function (token) {
        // You can access the token ID with `token.id`.
        // Get the token ID to your server-side code for use.
    }
});
document.getElementById('customButton').addEventListener('click', function (e) {
    // Open Checkout with further options:
    data = handler.open({
        amount: 19999,
        currency: "nok",
        name: 'test',
        description: 'test',
        email: "pål@mail.com"
    });
    e.preventDefault();
    $.ajax({
    dataType: "json",
    url: '/ajax/events/5/payment',
    data: data,
    success: data => {
        console.log(data);
    },
    error: data => {
        console.log(data);
    }
});
});

// Close Checkout on page navigation:
window.addEventListener('popstate', function () {
    handler.close();
});

