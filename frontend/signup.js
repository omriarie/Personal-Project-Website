let autocomplete;
let addressField;

function initAutocomplete() {
    // Get the input element for the address
    addressField = document.querySelector("#full_address");

    // Create the autocomplete object, restricting the search predictions to addresses in Israel
    autocomplete = new google.maps.places.Autocomplete(addressField, {
        componentRestrictions: { country: "IL" },  // Restrict to Israel
        types: ["geocode"]  // Only geocoded results (addresses)
    });

    // Add an event listener to handle when a user selects an address
    autocomplete.addListener("place_changed", fillInAddress);
}

// Function to handle filling in the address
function fillInAddress() {
    // Get the place details from the autocomplete object
    const place = autocomplete.getPlace();
    
    // Initialize the full address string
    let fullAddress = "";

    // Loop through each component of the address
    for (const component of place.address_components) {
        const componentType = component.types[0];

        // Concatenate the address components to form a full address string
        switch (componentType) {
            case "street_number":
                fullAddress = `${component.long_name} ${fullAddress}`;
                break;
            case "route":
                fullAddress += component.short_name;
                break;
            case "locality":
                fullAddress += `, ${component.long_name}`;
                break;
            case "administrative_area_level_1":
                fullAddress += `, ${component.short_name}`;
                break;
            case "country":
                fullAddress += `, ${component.long_name}`;
                break;
            case "postal_code":
                fullAddress += `, ${component.long_name}`;
                break;
        }
    }

    // Set the full address to the address field
    addressField.value = fullAddress;

    // Log the full address to debug if needed
    console.log("Selected full address:", fullAddress);
}

// Initialize the autocomplete on window load
window.onload = initAutocomplete;
