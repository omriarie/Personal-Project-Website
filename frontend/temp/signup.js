document.getElementById('signup-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const fullAddress = document.getElementById('full_address').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                full_address: fullAddress,
                email: email,
                password: password
            }),
        });

        const result = await response.json();

        if (response.ok) {
            alert('Sign-up successful');
            window.location.href = "login.html";  // Redirect to login page
        } else {
            document.getElementById('error-message').style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('error-message').style.display = 'block';
    }
});
