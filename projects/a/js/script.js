// Add an event listener to the Contact section
const contactSection = document.querySelector('#contact');

if (contactSection) {
    contactSection.addEventListener('click', function() {
        alert('Contact section clicked!');
    });
} else {
    console.error('Contact section not found!');
}