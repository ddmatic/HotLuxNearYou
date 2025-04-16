$(document).ready(function () {
    $('#loginForm').on('submit', function (e) {
        // e.preventDefault(); // Stop the default form submission

        var username = $('#username').val();
        var password = $('#password').val();

        if (username === "" || password === "") {
            alert("Please fill out both fields.");
            return;
        }

        // Send login data to Flask backend
        $.post('/login', {
            username: username,
            password: password
        }).done(function (data) {
            if (data.success) {
                window.location.href = '/'; // Redirect to index on success
            } else {
                alert("Wrong username or password.");
            }
        }).fail(function () {
            alert("Server error. Please try again later.");
        });
    });
});