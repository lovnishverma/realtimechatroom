     // Socket connection
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
        const backgroundVideo = document.getElementById("background-video");
        const backgroundWrapper = document.getElementById("background-wrapper");
        const typingIndicator = document.querySelector(".typing-indicator");

        // App state
        let isTyping = false;
        let typingTimeout = null;

        // Initialize
        function init() {
            createParticles();
            populateEmojiPicker();
            loadNickname();
            setupEventListeners();
            messageInput.focus();
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
            const emojis = [
                '😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', 
                '😉', '😊', '😋', '😎', '😍', '😘', '😗', '😙', 
                '😚', '🙂', '🤗', '🤔', '😐', '😑', '😶', '🙄', 
                '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', 
                '😴', '😌', '😛', '😜', '😝', '🤤', '😒', '😓'
            ];
            
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
            // Message input events
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
                
                if (!isTyping) {
                    isTyping = true;
                    // Here you would emit a 'typing' event to the server
                    // socket.emit('typing', { nickname: getNickname() });
                }
                
                clearTimeout(typingTimeout);
                typingTimeout = setTimeout(() => {
                    isTyping = false;
                    // Here you would emit a 'stop-typing' event
                    // socket.emit('stop-typing', { nickname: getNickname() });
                }, 1000);
            });

            // Change nickname
            changeNicknameBtn.addEventListener('click', () => {
                const newNickname = prompt('Enter your new nickname:', getNickname());
                if (newNickname && newNickname.trim()) {
                    setNickname(newNickname.trim());
                    currentNicknameElement.textContent = getNickname();
                }
            });

            // Theme toggle
            themeToggleBtn.addEventListener('click', () => {
                document.body.classList.toggle('theme-light');
                const icon = themeToggleBtn.querySelector('i');
                if (icon.classList.contains('fa-moon')) {
                    icon.classList.replace('fa-moon', 'fa-sun');
                } else {
                    icon.classList.replace('fa-sun', 'fa-moon');
                }
            });

            // Emoji picker toggle
            emojiBtn.addEventListener('click', () => {
                if (emojiPicker.style.display === 'grid') {
                    emojiPicker.style.display = 'none';
                } else {
                    emojiPicker.style.display = 'grid';
                }
            });

            // Close emoji picker when clicking outside
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

        // Message functions
        function appendMessage(msg, type) {
            const newMessage = document.createElement('div');
            newMessage.classList.add('message', type);
            
            newMessage.innerHTML = `
                <div class="meta"><strong>${msg.nickname}</strong> • ${msg.timestamp}</div>
                <div class="content">${formatMessage(msg.message)}</div>
            `;
            
            messagesContainer.appendChild(newMessage);
            scrollToBottom();

            // Add animation class after a slight delay
            setTimeout(() => {
                newMessage.style.opacity = '1';
                newMessage.style.transform = 'translateY(0)';
            }, 10);
        }

        function formatMessage(message) {
            // Function to convert URLs to clickable links and add basic markdown
            // This is a simple implementation - you might want to use a proper markdown library
            
            // Convert URLs to links
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            message = message.replace(urlRegex, url => `<a href="${url}" target="_blank" class="text-info">${url}</a>`);
            
            // Convert emojis
            message = message.replace(/:\)/g, '😊')
                             .replace(/:\(/g, '😔')
                             .replace(/:D/g, '😁')
                             .replace(/;\)/g, '😉');
            
            return message;
        }

        function scrollToBottom() {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function sendMessage() {
            const msg = messageInput.value.trim();
            const nickname = getNickname();
            
            if (msg) {
                const now = new Date();
                const options = { hour: '2-digit', minute: '2-digit' };
                const timestamp = now.toLocaleTimeString([], options);
                
                appendMessage({
                    nickname: nickname,
                    message: msg,
                    timestamp: timestamp
                }, 'sent');
                
                socket.emit('message', {
                    message: msg,
                    nickname: nickname
                });
                
                messageInput.value = '';
            }
        }

        // Socket events
        socket.on('connect', function() {
            console.log('Connected to server');
        });

        socket.on('load_messages', function(messages) {
            messagesContainer.innerHTML = '';
            messages.forEach(function(msg) {
                appendMessage(msg, getNickname() === msg.nickname ? 'sent' : 'received');
            });
            scrollToBottom();
        });

        socket.on('message', function(msg) {
            // Only display received messages (not our own sent ones)
            if (msg.nickname !== getNickname()) {
                appendMessage(msg, 'received');
                
                // Play sound for new message
                playMessageSound();
            }
        });

socket.on('ban_notification', function(data) {
    if (data.message) {
        alert(data.message + (data.remaining ? "\nRemaining time: " + data.remaining : ""));
        
        // Disable message input and sending
        document.getElementById("messageInput").disabled = true;
        document.getElementById("send-btn").disabled = true;
        document.getElementById("change-nickname-btn").disabled = true;
    }
});




        // For future implementation:
        socket.on('typing', function(data) {
            if (data.nickname !== getNickname()) {
                typingIndicator.style.display = 'block';
                scrollToBottom();
            }
        });

        socket.on('stop-typing', function() {
            typingIndicator.style.display = 'none';
        });

        // Play sound when new message arrives
        function playMessageSound() {
            const audio = new Audio('https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c1539c.mp3?filename=notification-sound-7062.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Audio play prevented:', e));
        }

        // Initialize app
        document.addEventListener('DOMContentLoaded', init);