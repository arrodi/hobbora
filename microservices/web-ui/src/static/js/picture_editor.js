// Handle Replace Picture Popup
document.querySelectorAll('.replace-button').forEach((button) => {
    button.addEventListener('click', (event) => {
        const modal = document.getElementById('upload-modal');
        const hobbyId = event.target.getAttribute('data-hobby-id');
        const pictureId = event.target.getAttribute('data-picture-id');
        const replaceUrl = event.target.getAttribute('data-replace-url');

        // Update modal attributes
        modal.setAttribute('data-hobby-id', hobbyId);
        modal.setAttribute('data-picture-id', pictureId);
        modal.setAttribute('data-replace-url', replaceUrl);
        modal.classList.remove('hidden');
    });
});
// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("upload-modal");

    // Add event listener for the Replace button
    document.querySelector('.file-upload-button').addEventListener('click', () => {
        // Get the hobby ID and picture ID from the modal's data attributes
        const hobbyId = modal.getAttribute('data-hobby-id');
        const pictureId = modal.getAttribute('data-picture-id');
        const replaceUrl = modal.getAttribute('data-replace-url');

        // Get the uploaded file from the input
        const fileInput = document.getElementById("file-upload");
        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a file to upload.");
            return;
        }

        // Prepare the form data for uploading
        const formData = new FormData();
        formData.append("file", file);
        formData.append("hobbyId", hobbyId);
        formData.append("pictureId", pictureId);

        // Send the file to the server
        fetch(replaceUrl, {
            method: "POST",
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Reload the page to reflect the changes
                } else {
                    alert(`Error: ${data.message}\n`);
                }
            })
            .catch(error => {
                alert(`An error occurred while uploading the file:\n${error.message || error}\nURL:${replaceUrl}\nHobby ID:${hobbyId}\nPicture ID:${pictureId}`);
            });

    });

    document.querySelectorAll('.delete-button').forEach((button) => {
        button.addEventListener('click', (event) => {
            const hobbyId = event.target.getAttribute('data-hobby-id');
            const pictureId = event.target.getAttribute('data-picture-id');
            const deleteUrl = event.target.getAttribute('data-delete-url');
    
            // Confirm before deletion
            if (!confirm("Are you sure you want to delete this picture?")) {
                return;
            }
    
            // Send the delete request to the server
            fetch(deleteUrl, {
                method: "GET", // Use DELETE method instead of POST for semantic clarity
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`${data.message}`);
                        location.reload(); // Reload the page to reflect the changes
                    } else {
                        alert(`Error: ${data.message}`);
                    }
                })
                .catch(error => {
                    console.error("Error during file delete:", error);
                    alert(`An error occurred: ${error.message || error}`);
                });
        });
    });
    

    // Add event listener for the Cancel button to close the modal
    document.querySelector('.close-modal').addEventListener('click', () => {
        modal.classList.add('hidden');
    });
});
