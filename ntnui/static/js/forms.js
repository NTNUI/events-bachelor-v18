var isChanged = false;

// Detect input fields changing
$('input').change(function(e) {
    isChanged = false;

    $('*[id*=id_]:visible').each(function() {
            if (this.value) {
              isChanged = true;
            }
    });

    if (~e.target.id.indexOf("email")) {
      var email = e.target.value.trim().toLowerCase();
      var id = e.target.id;
      getName(email, id);
    }
});

$(document).ready( function () {
  getGroup();

  // Get the names from the database
  $('*[id*=_email]:visible:input').each(function() {
    if(this.value) {
      getName(this.value, this.id);
    } else {
      document.getElementById(this.id.replace('email', 'name')).value = "";
    }

    if(this.value=="None") {
      this.value="";
    }
  });
});

function getName(email, id) {
  fieldId = id.replace('email', '');

  $.ajax({
    url: '/ajax/validate_email/',
    data: {
        'email': email,
        'id': fieldId
    },
    dataType: 'json',
    success: function (data) {

      if (!data.error) {
          document.getElementById(data.id + 'email').value=email;
          document.getElementById(data.id + 'name').value=data.first_name + " " + data.last_name;
      } else {
          document.getElementById(data.id + 'name').value="";
      }
    }
  });
}

function getGroup() {
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
    }); // end ajax
  } catch (err) {
    console.error("No such field")
  }
}

window.onbeforeunload = function() {
    if (isChanged) {
        return "Are you sure you want to leave?";
    } else {
        return;
    }
};

$('form').submit(function () {
    window.onbeforeunload = null;
});
