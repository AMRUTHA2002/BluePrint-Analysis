document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showImage(data.image_path);
            showText(data.extracted_text.join(' '));  // Join the array elements into a single string
        })
        .catch(error => console.error('Error:', error));
    });
});
