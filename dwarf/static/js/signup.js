$(document).ready(function () {
    $('#id_username').focusout(function() {
        var username = $('#id_username').val();

        // Check by ajax if the user exists
        $.ajax({
            type: "GET",
            url: "userexists/" + username,
            success: function(data) {
                if (data.exists){
                    console.log(data.error);
                    $(data.error).insertAfter('#id_username');
                }else{
                    console.log("Username available");
                }
            },
            error: function(data) {
                alert("Error");
            }
        });
    });
});
