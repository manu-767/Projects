let menu = document.querySelector('#menu-bar');
let nav = document.querySelector('.nav');

menu.onclick = () => {
    menu.classList.toggle('fa-times');
    nav.classList.toggle('active');
};

let section = document.querySelectorAll('section');
let navLinks = document.querySelectorAll('header .nav a');

window.onscroll = () => {
    menu.classList.remove('fa-times');
    nav.classList.remove('active');

    section.forEach(sec => {
        let top = window.scrollY;
        let height = sec.offsetHeight;
        let offset = sec.offsetTop - 150;
        let id = sec.getAttribute('id');

        if (top >= offset && top < offset + height) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                document.querySelector(`header .nav a[href*="${id}"]`).classList.add('active');
            });
        }
    });
};

const realFileBtn = document.getElementById("real-file");
const customBtn = document.getElementById("custom-button");
const customTxt = document.getElementById("custom-text");
const uploadForm = document.getElementById("upload-form");
const submitBtn = document.getElementById("submit-button");
const spinner = document.getElementById("inferenceSpinner");

customBtn.addEventListener("click", function () {
    realFileBtn.click();
});

realFileBtn.addEventListener("change", function () {
    if (realFileBtn.value) {
        customTxt.innerHTML = realFileBtn.value.match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1];
    } else {
        customTxt.innerHTML = "No file chosen, yet.";
    }
});

// ✅ Chatbot popup toggle
function toggleChat() {
    const popup = document.getElementById("chatPopup");
    popup.style.display = popup.style.display === "none" || popup.style.display === "" ? "block" : "none";
}

// ✅ Chat sending logic
function sendMessage() {
    const input = document.getElementById("userInput");
    const chatBody = document.getElementById("chatBody");
    const message = input.value.trim();
    if (!message || message.length < 2) {
        alert("Please enter a longer message.");
        return;
    }

    const userMsg = document.createElement("div");
    userMsg.className = "chat-message user";
    userMsg.textContent = message;
    chatBody.appendChild(userMsg);
    input.value = "";

    // ✅ Show typing placeholder
    const loadingMsg = document.createElement("div");
    loadingMsg.className = "chat-message bot typing";
    loadingMsg.textContent = "Typing...";
    chatBody.appendChild(loadingMsg);
    chatBody.scrollTop = chatBody.scrollHeight;

    // ✅ Fetch response
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
        .then(res => res.json())
        .then(data => {
            chatBody.removeChild(loadingMsg);
            const botMsg = document.createElement("div");
            botMsg.className = "chat-message bot";
            botMsg.textContent = data.response;
            chatBody.appendChild(botMsg);
            chatBody.scrollTop = chatBody.scrollHeight;
        })
        .catch((error) => {
            chatBody.removeChild(loadingMsg);
            const errMsg = document.createElement("div");
            errMsg.className = "chat-message bot";
            errMsg.textContent = "⚠️ Failed to connect: " + error.message;
            chatBody.appendChild(errMsg);
        });
}

// ✅ Enter key submits the chatbot form
document.getElementById("userInput").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

// ✅ Image preview logic
function previewImage(event) {
    const input = event.target;
    const preview = document.getElementById('imagePreview');
    const file = input.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        preview.src = '#';
        preview.style.display = 'none';
    }
}

// Enhance form UX: disable submit during inference, show spinner
if (uploadForm && submitBtn && spinner) {
  uploadForm.addEventListener('submit', function() {
    submitBtn.setAttribute('disabled', 'true');
    spinner.classList.remove('visually-hidden');
    spinner.setAttribute('aria-hidden', 'false');
  });
}

// Initialize progress bars from data attribute
window.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.progress-bar[data-progress]')
    .forEach(function(el){
      var val = parseInt(el.getAttribute('data-progress'), 10);
      if (!isNaN(val)) {
        el.style.width = Math.max(0, Math.min(100, val)) + '%';
      }
    });
});


// feedback.js
//  emailjs.init('FG1mWniKBIi5a2y9z');
// document.getElementById('contact-form').addEventListener('submit', function (e) {
//   e.preventDefault();

//   // Set the time field to current time
//   this.time.value = new Date().toLocaleString();

//   // Send the email
//   emailjs.sendForm('service_4b9uww8', 'template_yq387u9', this)
//     .then(() => {
//       alert('✅ Message sent successfully!');
//       this.reset(); // Optional: clear the form
//     }, (error) => {
//       alert('❌ Failed to send message: ' + error.text);
//     });
// });




emailjs.init('FG1mWniKBIi5a2y9z');
document.getElementById('contact-form').addEventListener('submit', function (e) {
  e.preventDefault();

  // Set the time field
  this.time.value = new Date().toLocaleString();

  const form = this;

  // Send message to YOU (admin)
  emailjs.sendForm('service_4b9uww8', 'template_yq387u9', form)
    .then(() => {
      // Send auto-reply to USER
      emailjs.sendForm('service_4b9uww8', 'template_axhtt9i', form)
        .then(() => {
          alert('✅ Message sent and confirmation email sent to user!');
          form.reset();
        })
        .catch((error) => {
          alert('⚠️ Message sent, but failed to send auto-reply to user: ' + error.text);
        });
    })
    .catch((error) => {
      alert('❌ Failed to send message: ' + error.text);
    });
});
