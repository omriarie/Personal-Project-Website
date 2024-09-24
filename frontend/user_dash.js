document.addEventListener('DOMContentLoaded', async () => {
    const userId = localStorage.getItem('user_id');
    const firstName = localStorage.getItem('first_name');
    const token = localStorage.getItem('Token');  // Retrieve the token from localStorage

    // Display user name
    document.getElementById('user-name').textContent = firstName;

    // Ensure user is logged in and token is available
    if (!token || !userId) {
        alert("You need to be logged in to view this page.");
        window.location.href = "login.html";
        return;
    }

    // Fetch and display user products
    try {
        const response = await fetch(`http://127.0.0.1:8000/user_products/${userId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`  // Send the token in the request header
            }
        });

        const products = await response.json();

        // Check if the response is an array and handle empty products list
        if (Array.isArray(products)) {
            const tableBody = document.querySelector('#user-product-table tbody');
            tableBody.innerHTML = '';  // Clear the table body

            if (products.length === 0) {
                // No products, display a friendly message
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="7">You haven't added any products yet. Use the form below to add new products.</td>`;
                tableBody.appendChild(row);
            } else {
                // Display products if there are any
                products.forEach(product => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${product.id}</td>
                        <td><img src="/static/uploads/${product.image}" alt="${product.name}" style="max-width: 100px;"/></td>
                        <td>${product.name}</td>
                        <td>${product.description}</td>
                        <td>${product.price}</td>
                        <td>${product.quantity}</td>
                        <td><button class="delete-product" data-id="${product.id}">Delete</button></td>
                    `;
                    tableBody.appendChild(row);
                });

                // Add event listener to delete buttons
                document.querySelectorAll('.delete-product').forEach(button => {
                    button.addEventListener('click', async (e) => {
                        const productId = e.target.getAttribute('data-id');
                        await deleteProduct(productId);
                    });
                });
            }
        } else {
            console.log('No products found.');
        }
    } catch (error) {
        console.log('Error fetching user products:', error);
    }

    // Handle product form submission with image upload
    const productForm = document.getElementById('new-product-form');

    if (productForm) {
        productForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Retrieve token and userId from localStorage
            const token = localStorage.getItem('Token');
            const userId = localStorage.getItem('user_id');

            // Debug: Check if the token and userId are present
            if (!token || !userId) {
                alert("You must be logged in to add a product.");
                window.location.href = "login.html";
                return;
            }

            const formData = new FormData();
            formData.append('name', document.getElementById('name').value);
            formData.append('description', document.getElementById('description').value);
            formData.append('price', document.getElementById('price').value);
            formData.append('quantity', document.getElementById('quantity').value);
            formData.append('image', document.getElementById('image').files[0]);

            try {
                const response = await fetch('http://127.0.0.1:8000/products', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Authorization': `Bearer ${token}`  // Include token for authorization
                    }
                });

                if (response.ok) {
                    alert('Product added successfully');
                    window.location.reload(); // Reload the page to show the new product
                } else {
                    console.error("Failed response status:", response.status);
                    alert('Failed to add product');
                }
            } catch (error) {
                console.error('Error adding product:', error);
                alert('Error adding product!');
            }
        });
    }

    // Logout button functionality
    document.getElementById('logout-button').addEventListener('click', function () {
        // Clear localStorage to log the user out
        localStorage.removeItem('user_id');
        localStorage.removeItem('first_name');
        localStorage.removeItem('Token');  // Ensure the token is cleared

        // Redirect to the login page
        window.location.href = "login.html";
    });
});

// Function to delete a product
async function deleteProduct(productId) {
    const token = localStorage.getItem('Token');

    try {
        const response = await fetch(`http://127.0.0.1:8000/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('Product deleted successfully');
            window.location.reload();
        } else {
            alert('Failed to delete product');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
    }
}
