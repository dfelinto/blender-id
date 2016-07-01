// Used in login_user.jade
function send_confirm_mail(endpoint) {
    var email = $('#email').val();
    var csrf_token = $('#csrf_token').val();

    function show(html_class, msg) {
        var p = $("<p>")
            .addClass(html_class)
            .text(msg);

        $('#email_input_group').append(p);
    }


    $.ajax({
        type: 'POST',
        url: endpoint,
        data: JSON.stringify({
            'email': email,
            'csrf_token': csrf_token
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function (data) {
            // Can still be a failure, we need to inspect the data.
            if (data.meta.code == 200) {
                show('info', 'Email sent, please check your inbox.');
            } else {
                show('error', 'There was a problem sending your email: ' +
                    JSON.stringify(data.response.errors));
            }
        },
        failure: function (errMsg) {
            show('error', 'There was a problem sending your email: ' + errMsg);
        }
    });
}
