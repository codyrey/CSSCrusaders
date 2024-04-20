const ws = true;
let socket = null;

function initWS(){
  console.log("HI THERE");
  socket = io();

  socket.on("connect", () => {
    console.log("user connected!");
  })

  socket.on("disconnect", () => {
    console.log("user disconnected");
  })

  socket.on("message", (ws_message) => {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType;
    if(messageType === 'message'){
      console.log("message sent");
    }
  });
}

function addText () {
  document.getElementById("post-text-box").focus();
  document.getElementById("post-title").innerHTML += "Posts";
}

function sendChat () {
    const chatTextBox = document.getElementById('post-text-box');
    const message = chatTextBox.value;
    chatTextBox.value = "";

    if (ws){
      socket.send(JSON.stringify({"message": message}));
    }
    else {
      fetch("/chat-messages", {
        method: "POST", 
        body: JSON.stringify({"message":message}),
        headers: {
          "Content-Type": "application/json"
        }
      })
      .then((result) => {
        console.log(result);
      })
    }
  chatTextBox.focus();
}

function fetchMessages() {
    fetch("/get-messages")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch messages");
            }
            return response.json();
        })
        .then(messages => {
            renderMessages(messages);
        })
        .catch(error => {
            console.error("Error fetching messages:", error);
        });
    }
    // Function to render messages in the HTML container
function renderMessages(messages) {
    const messagesContainer = document.getElementById("messages-container");
    messagesContainer.innerHTML = "";
    messages.forEach(message => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.textContent = message.content;
        messagesContainer.appendChild(messageElement);
    });
}
function renderMessage(message) {
        const messageContainer = document.getElementById("posts-container");
        messageContainer.innerHTML = "";
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.textContent = message.content;
        messageContainer.appendChild(messageElement);
    }
document.addEventListener("DOMContentLoaded", fetchMessages);
function fetchInitialLikeCounts() {
    document.querySelectorAll(".post-likes").forEach(like => {
        const postId = like.parentElement.dataset.postId;
        fetch(`/like?postId=${postId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                const counter = like.querySelector(".like-count");
                counter.innerText = data.likeCount;
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });
}
window.addEventListener("load", fetchInitialLikeCounts);
document.querySelectorAll(".post-likes").forEach(like => {
  like.addEventListener("click", function() {
    const postId = this.parentElement.dataset.postId;
    const counter = this.querySelector(".like-count");
    const isLiked = this.classList.contains("liked");
    const username = this.parentElement.dataset.username;
    fetch("/like", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ postId: postId, username: username })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then(data => {
      if (data.liked) {
        like.classList.add("liked");
      } else {
        like.classList.remove("liked");
      }
      counter.innerText = data.likeCount;
    })
    .catch(error => {
      console.error("Error:", error);
    });
  });
});

function welcome(){
  addText();
  if(ws){
    initWS();
  }
}