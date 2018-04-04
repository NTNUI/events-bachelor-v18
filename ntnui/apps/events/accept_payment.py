def accept_payment():
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys
    stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

    # Token is created using Checkout or Elements!
    # Get the payment token ID submitted by the form:
    token = request.form['stripeToken'] # Using Flask

    # Charge the user's card:
    charge = stripe.Charge.create(
      amount=999,
      currency="usd",
      description="Example charge",
      source=token,
    )
