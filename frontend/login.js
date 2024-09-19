document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        // Debugging: Logging the response data to verify the token is returned
        console.log("Login response data:", data);

        if (response.ok) {
            // Store the token in localStorage
            const token = data.token; // Extract the access_token from the response
            const firstName = data.first_name;
            const userId = data.user_id;

            console.log("token:", token);  // Debugging: Log the token to check its value

            localStorage.setItem('Token', token);  // Store the token
            localStorage.setItem('first_name', firstName);  // Store the user's first name
            localStorage.setItem('user_id', userId);  // Store the user's ID

            // Redirect to the home page or another protected page
            alert('Login successful!');
            window.location.href = "index.html";
        } else {
            alert('Login failed. Please check your credentials and try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
    }
});
