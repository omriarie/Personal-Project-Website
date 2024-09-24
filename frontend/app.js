let currentPage = 0;
const limit = 10; // Limit set to 10 for standard display
let totalPages = 0; // Total number of pages

// Function to fetch total pages from the backend
async function fetchTotalPages() {
    try {
        const response = await fetch(`http://127.0.0.1:8000/total_pages?limit=${limit}`);
        const data = await response.json();
        totalPages = data.total_pages;  // Update the total pages
    } catch (error) {
        console.error('Error fetching total pages:', error);
    }
}

// Function to fetch products with pagination
async function fetchProducts(page = 0) {
    const skip = page * limit;
    try {
        // Fetch products from the backend
        const response = await fetch(`http://127.0.0.1:8000/products?skip=${skip}&limit=${limit}`);
        const data = await response.json();

        // Get the table body element where rows will be inserted
        const tableBody = document.querySelector('#product-table tbody');
        
        // Clear any existing rows
        tableBody.innerHTML = '';

        // Loop through the products and create a row for each
        data.forEach(product => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
            <td>${product.id}</td>
            <td><img src="/static/uploads/${product.image}" alt="${product.name}" style="max-width: 100px;"></td>
            <td>${product.name}</td>
            <td>${product.description}</td>
            <td>$${product.price}</td>
            <td>${product.quantity}</td>
            <td>${product.full_address || 'N/A'}</td> <!-- Safeguard in case full_address is undefined -->
            `;
            
            tableBody.appendChild(row);  // Append the row to the table
        });

        // Update the current page number display
        document.querySelector("#page-number").innerText = `Page: ${page + 1} of ${totalPages}`;

        // Disable/Enable Previous and Next buttons based on logic
        document.querySelector("#prev-button").disabled = page === 0;  // Disable Previous button on the first page
        document.querySelector("#next-button").disabled = page >= (totalPages - 1);  // Disable Next button on the last page

        // Update the current page
        currentPage = page;
    } catch (error) {
        console.error('Error fetching products:', error);
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
}

// Event listeners for pagination buttons
document.querySelector("#next-button").addEventListener("click", () => {
    if (currentPage < totalPages - 1) {
        fetchProducts(currentPage + 1);
    }
});

document.querySelector("#prev-button").addEventListener("click", () => {
    if (currentPage > 0) {
        fetchProducts(currentPage - 1);
    }
});

// Initialize: Fetch total pages and first set of products
window.onload = async () => {
    await fetchTotalPages();  // Fetch the total pages first
    fetchProducts();          // Fetch the products for the first page
};
