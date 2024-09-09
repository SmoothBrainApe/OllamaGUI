// Send Message Logic

const inputField = document.getElementById('user-input-field');
const submitButton = document.getElementById('send-button');

inputField.addEventListener('keypress', (event) => {
    if (event.key == 'Enter') {
        handleSubmit();
    }
});

submitButton.addEventListener('click', handleSubmit());

function handleSubmit() {
    const userInput = inputField.value;
    inputField.value = '';

    if (userInput !== '') {
        createChatBubble('user-chat-bubble', userInput);
        let responseBubble = null;
        const url = `/chat/message?message=${encodeURIComponent(userInput)}`;
        const eventSource = new EventSource(url);
        eventSource.onmessage = (event) => {
            const word = event.data.replace("\\n\\n", "\n\n").replace('\\n', '\n');
            if (!responseBubble) {
                responseBubble = createChatBubble('response-chat-bubble', word);
            } else {
                responseBubble.textContent += word;
            };
        };
        eventSource.onerror = () => {
            console.log("No data received from API")
            eventSource.close();
        };
        eventSource.onopen = () => {
            console.log('Connection established');
        }
    } else {
        console.log('Please enter a text');
    };
}

function createChatBubble(className, message) {
    const chatWindow = document.getElementById('chat-window')
    const chatBubble = document.createElement('div');
    chatBubble.classList.add(className);
    chatBubble.innerHTML = message.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
    chatWindow.prepend(chatBubble);
    return chatBubble;
}

const clearButton = document.getElementById('clear-button');
const uploadButton = document.getElementById('upload-button');
const unloadButton = document.getElementById('unload-button');


// Populate model list logic

let modelList = [];
let chatList = [];
let embedList = [];
let visionList = [];

document.addEventListener('DOMContentLoaded', fetchModels)

function fetchModels() {
    fetch('/chat/models', {
        method: 'GET',
        headers: {
            'Content-type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        modelList = data.message;
        console.log('Updated modelsLists:', modelList);
        modelList.forEach(model => {
            if (model.includes('moondream')) {
                visionList.push(model);
            } else if (model.includes('llava')) {
                visionList.push(model);
            } else if (model.includes('embed')) {
                embedList.push(model);
            } else {
                chatList.push(model);
            }
        });

        if (chatList.length > 0) {
            populateModels(chatList, 'chat-model-select')
        }

        if (embedList.length > 0) {
            populateModels(embedList, 'embed-model-select')
        }

        if (visionList.length > 0) {
            populateModels(visionList, 'vision-model-select')
        }
        
    })
    .catch(console.error)
}

function populateModels(list, selectElementID) {
    if (list.length > 0) {
        document.getElementById(selectElementID).innerHTML = '';
        let selectOption = document.createElement('option');
        selectOption.value = '';
        selectOption.text = 'Select a model';
        document.getElementById(selectElementID).appendChild(selectOption);

        list.forEach(model => {
            let option = document.createElement('option');
            option.value = model;
            option.text = model;
            document.getElementById(selectElementID).appendChild(option);
        })
    }
} 

// Choose model logic

const selectChatModel = document.getElementById('chat-model-select');

selectChatModel.addEventListener('change', (event) => {
    const selectedValue = event.target.value;

    if (selectedValue !== '') {
        fetch('/chat/models/chat', {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
            },
            body: JSON.stringify({ message: selectedValue }),
        })
        .then(response => response.json())
        .then(data => {
            returnMessage = data.message;
            console.log(returnMessage);
        })
    }
})