$('.open-modal').click(function(event) {
    event.preventDefault();
    this.blur(); // Manually remove focus from clicked link.
    $.get($(this).attr('href'), function(html) {
        $('#modal-container')
            .html(html)
            .modal({
                fadeDuration: 100,
                showClose: false,
            });
    });
});
