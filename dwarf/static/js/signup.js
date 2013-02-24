$(document).ready(function () {

    // Deactivate submit button until all the fields are perfect
    var signupForm = $('#signup-form');
    var submitBtn = signupForm.find(':submit');
    var spinnerIcon = $('<i/>').addClass('icon-spinner');
    spinnerIcon.addClass('icon-spin');
    submitBtn.addClass('disabled');
    submitBtn.attr('disabled', 'true');

    //bind  the form checker in each change
    var fields = $(".control-group");

    for (var i=0; i < fields.length; i++){
        var div = $(fields[i]);
        div.focusout(checkFormIsValid);
    }

    function checkFormIsValid(){
        // Check if all classes have succes
        var fields = $(".control-group");
        for (var i=0; i < fields.length; i++){
            var div = $(fields[i]);
            if (!div.hasClass('success')){
                 // Set the form for submission
                submitBtn.addClass('disabled');
                submitBtn.attr('disabled', 'true');
                return;
            }
        }
        // Set the form for submission
        submitBtn.removeAttr("disabled");
        submitBtn.removeClass('disabled');
    }

    function isValidEmailAddress(emailAddress) {
        var pattern = new RegExp(/^[+a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i);
        return pattern.test(emailAddress);
    }

    // Ajax check of the username
    $('#id_username').focusout(function() {
        var username = $('#id_username').val();

        // Check if is filled
        if (username === ''){
            $('#username-control-group').removeClass('error');
            $('#username-control-group').removeClass('success');
            $('#username-help-inline').text('');
            return;
        }

        //Add load spinner
        $('#username-help-inline').text('');
        $('#username-help-inline').append(spinnerIcon);
        
        // Check by ajax if the user exists
        $.ajax({
            type: "GET",
            url: "userexists/" + username,
            success: function(data) {
                if (data.exists){
                    console.log(data.error);
                    // Add error to bootstrap field
                    $('#username-control-group').removeClass('success');
                    $('#username-control-group').addClass('error');
                    $('#username-help-inline').text(data.error);
                }else{
                    $('#username-control-group').removeClass('error');
                    $('#username-control-group').addClass('success');
                    $('#username-help-inline').text('');
                }
                checkFormIsValid();
            }
        });
    });

    // Ajax check of the email
    $('#id_email').focusout(function() {
        var email = $('#id_email').val();

        //not inserted
        if (email === ''){
            $('#email-control-group').removeClass('error');
            $('#email-control-group').removeClass('success');
            $('#email-help-inline').text('');
            return;
        }

        //Add load spinner
        $('#email-help-inline').text('');
        $('#email-help-inline').append(spinnerIcon);

        // Check email format
        if (isValidEmailAddress(email)){
            var csrfToken = signupForm.find('input[name="csrfmiddlewaretoken"]').val();
            // Check by ajax if the user exists
            $.ajax({
                type: "POST",
                url: "emailexists/",
                data:{
                    email: email,
                    csrfmiddlewaretoken: csrfToken
                },
                success: function(data) {
                    if (data.exists){
                        console.log(data.error);
                        // Add error to bootstrap field
                        $('#email-control-group').removeClass('success');
                        $('#email-control-group').addClass('error');
                        $('#email-help-inline').text(data.error);
                    }else{
                        $('#email-control-group').removeClass('error');
                        $('#email-control-group').addClass('success');
                        $('#email-help-inline').text('');
                    }
                    checkFormIsValid();
                },
                error: function(data){
                    console.log("error");
                }
            });
        }else{
            $('#email-control-group').removeClass('success');
            $('#email-control-group').addClass('error');
            $('#email-help-inline').text("Not a valid email");
        }
    });

    // Check 2 passwords are the same
    var check_passwords = function() {
        pass1 = $('#id_password1').val();
        pass2 = $('#id_password2').val();
        if (pass1 !== '' && pass2 !== ''){
            if (pass1 === pass2){
                $('#password1-help-inline').text("");
                $('#password2-help-inline').text("");
                $('#password1-control-group').removeClass('error');
                $('#password1-control-group').addClass('success');
                $('#password2-control-group').removeClass('error');
                $('#password2-control-group').addClass('success');
            }else{
                $('#password1-help-inline').text("Passwords don't match");
                $('#password2-help-inline').text("Passwords don't match");
                $('#password1-control-group').removeClass('success');
                $('#password1-control-group').addClass('error');
                $('#password2-control-group').removeClass('success');
                $('#password2-control-group').addClass('error');
            }
        }

        checkFormIsValid();
    };

    $('#id_password1').focusout(check_passwords);
    $('#id_password2').keyup(check_passwords);
});
