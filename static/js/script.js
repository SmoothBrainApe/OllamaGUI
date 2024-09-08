const inputField = document.getElementById('user-input-field');
const submitButton = document.getElementById('send-button');

inputField.addEventListener('keypress', (event) => {
    if (event.key == 'Enter') {
        handleSubmit();
    }
});

submitButton.addEventListener('click', handleSubmit());

function handleSubmit() {
    const userInput = inputField.value.trim();

    if (userInput) {
        fetch('/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => console.log('Server response: ', data))
        .catch(error => console.error('Error: ', error));
    } else {
        console.log('Please enter a text');
    }
}

const clearButton = document.getElementById('clear-button');
const uploadButton = document.getElementById('upload-button');
const unloadButton = document.getElementById('unload-button');