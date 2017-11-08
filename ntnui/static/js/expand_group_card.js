let $allgroups = $('#all-groups').find('.group-card-all-groups');
// let $paragraphs = $('#all-groups').find('.group-card-description');
//
// console.log("HELLO THERE",$paragraphs)
//
// $.each($paragraphs, function(i, p) {
//     console.log("TEXT",p.width);
//     if (p.innerWidth < p.scrollWidth) {
//         console.log("YO");
//         p.find('.group-card-read-more').toggleClass('group-card-read-more-hidden')
//     }
// });


$($allgroups.find('.group-card-read-more')).click(function () {
    console.log("VALUE", this.textContent);
    if (this.textContent === "Read more") {
        console.log("GOT IN HERE");
        this.textContent = "Read less";
    } else {
        this.textContent = "Read more";
    }

    $(this).siblings('p').toggleClass('group-card-description');
    $(this).siblings('p').toggleClass('group-card-description-expanded');

    $(this).parent().toggleClass('group-card-info');
    $(this).parent().toggleClass('group-card-info-expanded');

    $(this).parent().parent().toggleClass('group-card-all-groups');
    $(this).parent().parent().toggleClass('group-card-all-groups-expanded');
});