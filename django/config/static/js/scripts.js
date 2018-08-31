function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$('a.vote').click(function (e) {
    e.preventDefault();
    var url = $(this).attr('href');
    var $rating = $(this).parent().find('.rating');
    $.post(url, {
        'value': $(this).hasClass('vote-up'),
        'csrfmiddlewaretoken': getCookie('csrftoken')
    }, function (response) {
        $rating.text(response['rating']);
    });
});


$('a.mark').click(function (e) {
    e.preventDefault();
    var $this = $(this);
    var url = $this.attr('href');
    $.post(url, {
        'csrfmiddlewaretoken': getCookie('csrftoken')
    }, function (response) {
        if (response['success']) {
            var needActivate = !$this.hasClass('active');
            $('.answer-list').find('.mark').each(function () {
                $(this).removeClass('active');
            });
            if (needActivate) {
                $this.addClass('active');
            }
        }
    });
});