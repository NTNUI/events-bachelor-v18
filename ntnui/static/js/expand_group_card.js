let $allgroups = $('#all-groups').find('.group-card-all-groups');
$($allgroups.find('.group-card-read-more')).click(function () {
    console.log("VALUE", this.value)
    $(this).parent().parent().toggleClass('group-card-all-groups');
    $(this).parent().parent().toggleClass('group-card-all-groups-expanded');
});