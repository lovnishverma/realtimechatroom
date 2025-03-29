        var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port, {
            transports: ['websocket', 'polling']
        });

        function getNickname() {
            return localStorage.getItem("nickname") || "Anonymous";
        }

        document.getElementById("nicknameInput").addEventListener("change", function() {
            localStorage.setItem("nickname", this.value.trim() || "Anonymous");
        });

        function appendMessage(msg) {
            var msgBox = document.getElementById("messages");
            var newMessage = document.createElement("p");
            newMessage.textContent = msg.timestamp + " - " + msg.nickname + ": " + msg.message;
            msgBox.appendChild(newMessage);
            msgBox.scrollTop = msgBox.scrollHeight;
        }

        socket.on('load_messages', function(messages) {
            messages.forEach(function(msg) {
                appendMessage(msg);
            });
        });

        socket.on('message', function(msg) {
            appendMessage(msg);
        });

        function sendMessage() {
            var msgInput = document.getElementById("messageInput");
            var msg = msgInput.value.trim();
            var nickname = getNickname();
            if (msg) {
                socket.emit('message', { message: msg, nickname: nickname });
                msgInput.value = "";
            }
        }

        document.getElementById("theme-toggle").addEventListener("click", function() {
            document.body.classList.toggle("theme-light");
            document.body.classList.toggle("theme-dark");
            var icon = this.querySelector("i");
            icon.classList.toggle("fa-moon");
            icon.classList.toggle("fa-sun");
        });