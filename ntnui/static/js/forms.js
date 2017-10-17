var isChanged = false;

// Detect input fields changing
$('input').change(function(e) {
    isChanged = false;

    $('*[id*=id_]:visible').each(function() {
            if (this.value) {
              isChanged = true;
            }
    });

    if (~e.target.name.indexOf("email")) {
        var email = e.target.value.trim().toLowerCase();

        $.ajax({
            url: '/ajax/validate_email/',
            data: {
                'email': email
            },
            dataType: 'json',
            success: function (data) {
              var id = e.target.id.replace('email', '');

              if (!data.error) {
                  document.getElementById(id + 'email').value=email;
                  document.getElementById(id + 'name').value=data.first_name + " " + data.last_name;
              } else {
                  document.getElementById(id + 'name').value='';
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
                    $('div.group-name-class').text("for " + data.group);
                    //document.getElementById('id_group').value =
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
