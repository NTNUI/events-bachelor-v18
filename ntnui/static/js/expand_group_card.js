
// Hello there! This is jQuery-code controlling the behaviour of the "Read more"-button


// Get the group-cards and the paragraphs inside them.
let $allgroups = $('#all-groups').find('.group-card-all-groups');
let $paragraphs = $('#all-groups').find('.group-card-description');



//This is some jQuery-code from stackoverflow who finds out if the "element" is wider than its parent
function isOverflowing(element) {

    var wrapper = document.createElement('span'),
        result;

    while (element.firstChild) {
        wrapper.appendChild(element.firstChild);
    }

    element.appendChild(wrapper);

    result = wrapper.offsetWidth > wrapper.parentNode.offsetWidth;

    element.removeChild(wrapper);

    while (wrapper.firstChild) {
        element.appendChild(wrapper.firstChild);
    }

    return result;

}

//if the paragraph is not wider than its parent, hide the "Read more"-button
$.each($paragraphs, function(i, p) {
    if (isOverflowing(p)) {
        $($allgroups[i]).find('.group-card-read-more-hidden').toggleClass('group-card-read-more-hidden')
    }
});

//What happens when you click on the "Read more"-button.
$($allgroups.find('.group-card-read-more')).click(function () {

    // Change the text to "Read less".
    if (this.textContent === "Read more") {
        this.textContent = "Read less";
    } else {
        this.textContent = "Read more";
    }

    // Change the class-names of some elements so that the CSS makes the text wrap and the box higher.
    $(this).siblings('p').toggleClass('group-card-description');
    $(this).siblings('p').toggleClass('group-card-description-expanded');

    $(this).parent().toggleClass('group-card-info');
    $(this).parent().toggleClass('group-card-info-expanded');

    $(this).parent().parent().toggleClass('group-card-all-groups');
    $(this).parent().parent().toggleClass('group-card-all-groups-expanded');
});