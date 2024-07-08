document.addEventListener('DOMContentLoaded', () => {
    const bookNowButtons = document.querySelectorAll('.book-now');
    const destinationInput = document.querySelector('#destination');
    const numberInput = document.querySelector('#number_of_guests');
    const costInput = document.querySelector('#cost');
    let basePrice = 0; // Variable to store the base price

    bookNowButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default link behavior

            const packageName = button.getAttribute('data-package'); // Get package name
            basePrice = parseFloat(button.getAttribute('data-price')); // Get package price

            destinationInput.value = packageName; // Set the input field value to package name
            updateCost(); // Update the cost based on the initial number of guests
            document.querySelector('#book').scrollIntoView({ behavior: 'smooth' }); // Scroll to the booking section
        });
    });

    numberInput.addEventListener('input', () => {
        updateCost();
    });

    function updateCost() {
        const guests = parseInt(numberInput.value); // Get number of guests
        if (!isNaN(guests) && guests >= 2) { // Ensure the number of guests is valid and at least 2
            const totalPrice = basePrice * guests; // Calculate total price
            costInput.value = totalPrice.toFixed(2); // Set the input field value to total price
        } else {
            costInput.value = basePrice.toFixed(2); // Reset to base price if input is invalid
        }
    }
});
