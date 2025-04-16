document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registerForm");

    form.addEventListener("submit", function (e) {
        const password = document.getElementById("password").value;
        const confirm = document.getElementById("confirm_password").value;

        if (password !== confirm) {
            e.preventDefault();
            alert("Passwords do not match.");
        }
    });
});
