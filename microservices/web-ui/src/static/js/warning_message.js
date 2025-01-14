// JavaScript function to handle the tutor button click
function handleTutorButtonClick(hobbyID) {
    var isTutor = JSON.parse(document.getElementById('isTutor').textContent);

    // If the user is not a tutor, show the warning message
    if (!isTutor) {
        var warningMessage = document.getElementById('warning-message');
        warningMessage.style.display = 'block';  // Make it visible
        warningMessage.style.opacity = 1;  // Fully visible

        // Set a timeout to fade out the message after 3 seconds
        setTimeout(function() {
            warningMessage.style.opacity = 0;  // Start fading out
        }, 3000);
    } else {
        // If the user is a tutor, redirect to the tutor hobby page
        window.location.href = '/tutor-hobby/' + hobbyID;
    }
}
