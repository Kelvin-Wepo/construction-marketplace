document.addEventListener("DOMContentLoaded", () => {
  // Initialize Socket.IO if on messaging page
  if (document.querySelector(".chat-container")) {
    initializeChat()
  }

  // Initialize star rating if on review form
  if (document.querySelector(".rating-input")) {
    initializeRating()
  }
})

function initializeChat() {
  const chatContainer = document.querySelector(".chat-container")
  const messageForm = document.getElementById("message-form")
  const messageInput = document.getElementById("content")
  const userId = document.getElementById("user-id").value

  // Scroll to bottom of chat
  chatContainer.scrollTop = chatContainer.scrollHeight

  // Connect to Socket.IO
  const socket = io()

  // Join user's room
  socket.on("connect", () => {
    socket.emit("join", { room: `user_${userId}` })
  })

  // Listen for new messages
  socket.on("new_message", (data) => {
    // Only add message if it's for the current conversation
    const currentPartnerId = document.getElementById("partner-id").value
    if (data.sender_id == currentPartnerId || data.receiver_id == currentPartnerId) {
      addMessageToChat(data)
      chatContainer.scrollTop = chatContainer.scrollHeight
    }
  })

  // Handle message form submission
  if (messageForm) {
    messageForm.addEventListener("submit", () => {
      // Clear input after form submission
      setTimeout(() => {
        messageInput.value = ""
      }, 10)
    })
  }
}

function addMessageToChat(data) {
  const chatContainer = document.querySelector(".chat-container")
  const currentUserId = document.getElementById("user-id").value

  // Create message element
  const messageDiv = document.createElement("div")
  messageDiv.classList.add("message")

  // Determine if sent or received
  if (data.sender_id == currentUserId) {
    messageDiv.classList.add("message-sent")
  } else {
    messageDiv.classList.add("message-received")
  }

  // Add message content
  messageDiv.innerHTML = `
        <div class="message-content">${data.content}</div>
        ${
          data.attachment_url
            ? `<div class="message-attachment mt-2">
            <a href="${data.attachment_url}" target="_blank" class="btn btn-sm btn-light">
                <i class="bi bi-paperclip"></i> Attachment
            </a>
        </div>`
            : ""
        }
        <div class="message-time">${data.created_at}</div>
    `

  // Add to chat container
  chatContainer.appendChild(messageDiv)
}

function initializeRating() {
  const ratingInput = document.querySelector(".rating-input")
  const stars = document.querySelectorAll(".rating-star")

  stars.forEach((star, index) => {
    star.addEventListener("click", () => {
      const rating = index + 1
      ratingInput.value = rating

      // Update visual stars
      stars.forEach((s, i) => {
        if (i < rating) {
          s.classList.remove("bi-star")
          s.classList.add("bi-star-fill")
        } else {
          s.classList.remove("bi-star-fill")
          s.classList.add("bi-star")
        }
      })
    })
  })
}
