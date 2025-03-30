// Establish Socket connection
var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port, {
    transports: ['websocket', 'polling']
});

// DOM elements
const messagesContainer = document.getElementById("messages");
const messageInput = document.getElementById("messageInput");
const currentNicknameElement = document.getElementById("current-nickname");
const changeNicknameBtn = document.getElementById("change-nickname-btn");
const themeToggleBtn = document.getElementById("theme-toggle");
const emojiBtn = document.getElementById("emoji-btn");
const emojiPicker = document.getElementById("emoji-picker");
const backgroundWrapper = document.getElementById("background-wrapper");
const typingIndicator = document.querySelector(".typing-indicator");
const banMessage = document.getElementById("ban-message");
const banText = document.getElementById("ban-text");

// App state
let isTyping = false;
let typingTimeout = null;

// Initialize app
function init() {
    createParticles();
    populateEmojiPicker();
    loadNickname();
    setupEventListeners();
    messageInput.focus();
    banMessage.style.display = "none"; // Ensure the ban message is hidden initially
}

// Create floating particles
function createParticles() {
    const colors = ['#6c5ce7', '#a29bfe', '#fd79a8', '#00cec9', '#55efc4'];
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        const size = Math.random() * 20 + 5;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDuration = `${Math.random() * 20 + 10}s`;
        particle.style.animationDelay = `${Math.random() * 5}s`;
        backgroundWrapper.appendChild(particle);
    }
}

// Populate emoji picker
function populateEmojiPicker() {
    const emojis = ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊'];
    emojis.forEach(emoji => {
        const button = document.createElement('button');
        button.classList.add('emoji-btn');
        button.textContent = emoji;
        button.addEventListener('click', () => {
            messageInput.value += emoji;
            messageInput.focus();
            emojiPicker.style.display = 'none';
        });
        emojiPicker.appendChild(button);
    });
}

// Event listeners
function setupEventListeners() {
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    messageInput.addEventListener('input', () => {
        if (!isTyping) {
            isTyping = true;
            socket.emit('typing', { nickname: getNickname() });
        }
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            isTyping = false;
            socket.emit('stop-typing', { nickname: getNickname() });
        }, 2000);
    });

    changeNicknameBtn.addEventListener('click', () => {
        const newNickname = prompt('Enter your new nickname:', getNickname());
        if (newNickname && newNickname.trim()) {
            setNickname(newNickname.trim());
            currentNicknameElement.textContent = getNickname();
        }
    });

    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('theme-light');
    });

    emojiBtn.addEventListener('click', () => {
        emojiPicker.style.display = emojiPicker.style.display === 'grid' ? 'none' : 'grid';
    });
    
    document.addEventListener('click', (e) => {
        if (!emojiPicker.contains(e.target) && e.target !== emojiBtn) {
            emojiPicker.style.display = 'none';
        }
    });
}

// Nickname management
function getNickname() {
    return localStorage.getItem('nickname') || 'Anonymous';
}

function setNickname(nickname) {
    localStorage.setItem('nickname', nickname);
}

function loadNickname() {
    currentNicknameElement.textContent = getNickname();
}

// Messaging functions
function appendMessage(msg, type) {
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', type);
    newMessage.innerHTML = `<div class="meta"><strong>${msg.nickname}</strong> • ${msg.timestamp}</div><div class="content">${msg.message}</div>`;
    messagesContainer.appendChild(newMessage);
    scrollToBottom();
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendMessage() {
    const msg = messageInput.value.trim();
    if (msg) {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        appendMessage({ nickname: getNickname(), message: msg, timestamp }, 'sent');
        socket.emit('message', { nickname: getNickname(), message: msg });
        messageInput.value = '';
    }
}

// Socket events
socket.on('connect', () => {
    console.log('Connected to server');
    banMessage.style.display = "none";
});

socket.on('load_messages', (messages) => {
    messagesContainer.innerHTML = '';
    messages.forEach(msg => appendMessage(msg, getNickname() === msg.nickname ? 'sent' : 'received'));
    scrollToBottom();
});

socket.on('message', (msg) => {
    if (msg.nickname !== getNickname()) {
        appendMessage(msg, 'received');
    }
});

socket.on("ban_notification", function (data) {
    console.log("🚨 Received ban notification:", data);

    let banText = document.getElementById("ban-text");
    let banMessage = document.getElementById("ban-message");

    if (banText && banMessage) {
        console.log("✅ Ban message elements found in DOM.");
        banText.textContent = `${data.message} Don't use Abusive Language`;
        banMessage.classList.add("show");
    } else {
        console.warn("❌ Ban message elements not found in the DOM.");
    }
});

// Ensure the ban message is hidden when the page loads
document.addEventListener("DOMContentLoaded", function () {
    let banMessage = document.getElementById("ban-message");
    if (banMessage) {
        banMessage.classList.remove("show");
    }
});


socket.on('typing', (data) => {
    if (data.nickname !== getNickname()) {
        typingIndicator.style.display = 'block';
    }
});

socket.on('stop-typing', () => typingIndicator.style.display = 'none');

socket.on('disconnect', () => {
    console.log('Disconnected from server. Attempting to reconnect...');
    setTimeout(() => socket.connect(), 5000);
});

document.addEventListener('DOMContentLoaded', init);