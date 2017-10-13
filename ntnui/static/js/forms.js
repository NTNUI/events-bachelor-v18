var isChanged = false;

// Detect input fields changing
$('input').change(function(e) {
    if (~e.target.name.indexOf("email")) {
        var email = e.target.value.trim();

        $.ajax({
            url: '/ajax/validate_email/',
            data: {
                'email': email
            },
            dataType: 'json',
            success: function (data) {
                if (!data.error) {
                    var id = e.target.id.replace('email', '');
                    console.log(id + 'email');
                    document.getElementById(id + 'email').value=email;
                    document.getElementById(id + 'first_name').value=data.first_name;
                    document.getElementById(id + 'last_name').value=data.last_name;
                } else {
                    document.getElementById(id + 'first_name').value='';
                    document.getElementById(id + 'last_name').value='';
                }
            }
        });
    }});

$(document).ready( function () {
    // Clear all text fields on ready
    $('*[id*=id_]:visible').each(function() {
            this.value ='';
    });

    try {
        var slug = window.slug;

        $.ajax({
            url: '/ajax/group_name/',
            data: {
                'group': slug
            },
            dataType: 'json',
            success: function (data) {
                if (!data.error) {
                    document.getElementById('id_group').value = data.group;
                } else {
                    console.log("An Error Occurred");
                }

            }
        });
    } catch (err) {
        console.error("No such field")
    }});

window.onbeforeunload = function() {
    console.log(isChanged);
    // TODO: Edit ischanged flag

    if (isChanged) {
        return "Are you sure you want to leave?";
    } else {
        return;
    }
};

$('form').submit(function () {
    window.onbeforeunload = null;
});

