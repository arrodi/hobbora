const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadButton = document.getElementById('upload-button');

let selectedFile = null;

// Open file dialog when clicking the upload area
uploadArea.addEventListener('click', () => fileInput.click());

// Highlight the area on drag over
uploadArea.addEventListener('dragover', (event) => {
  event.preventDefault();
  uploadArea.classList.add('dragover');
});

// Remove highlight on drag leave
uploadArea.addEventListener('dragleave', () => {
  uploadArea.classList.remove('dragover');
});

// Handle file drop
uploadArea.addEventListener('drop', (event) => {
  event.preventDefault();
  uploadArea.classList.remove('dragover');
  const files = event.dataTransfer.files;
  handleFile(files[0]);
});

// Handle file input change
fileInput.addEventListener('change', (event) => {
  const files = event.target.files;
  handleFile(files[0]);
});

// Handle file selection and preview
function handleFile(file) {
  if (file && file.type.startsWith('image/')) {
    selectedFile = file;

    // Display image preview
    const reader = new FileReader();
    reader.onload = (e) => {
      uploadArea.innerHTML = `
        <p>Drag and drop an image here or click to upload</p>
        <input type="file" id="file-input" accept="image/*">
      `;
      const img = document.createElement('img');
      img.src = e.target.result;
      img.alt = "Preview";
      img.style.maxWidth = "100%";
      uploadArea.appendChild(img);
    };
    reader.readAsDataURL(file);

    uploadButton.disabled = false; // Enable upload button
  } else {
    alert('Only image files are allowed!');
    uploadButton.disabled = true;
    selectedFile = null;
  }
}

// Handle upload button click
uploadButton.addEventListener('click', () => {
  if (selectedFile) {
    const formData = new FormData();
    formData.append('file', selectedFile);

    fetch(uploadUrl, {
      method: 'POST',
      body: formData,
    })
      .then((response) => {
        if (response.redirected) {
          window.location.href = response.url; // Handle redirection
        } else {
          return response.json();
        }
      })
      .then((data) => {
        console.log('Upload successful:', data);
      })
      .catch((error) => {
        alert(`Upload failed. Please try again.\nError: ${error.message}`);
      });
  }
});
