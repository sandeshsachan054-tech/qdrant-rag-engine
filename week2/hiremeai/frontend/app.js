const form = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = userInput.value.trim();
  if (!question) return;

  // 1. User message display karein
  appendMessage(question, "user", false);
  userInput.value = "";

  // 2. Bot thinking placeholder
  const loadingMsg = appendMessage("Thinking...", "bot", false);

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: question })
    });

    if (!response.ok) {
      throw new Error("Server error: " + response.status);
    }

    const data = await response.json();
    const rawReply = data.response || data.answer || data.message || JSON.stringify(data);

    // 3. Markdown parse karke render karein
    if (typeof marked !== "undefined") {
      loadingMsg.innerHTML = marked.parse(rawReply);
    } else {
      loadingMsg.innerText = rawReply;
    }
  } catch (error) {
    loadingMsg.innerText = "Error: Backend server se connect nahi ho paya.";
    loadingMsg.style.color = "#f87171";
  }

  chatBox.scrollTop = chatBox.scrollHeight;
});

function appendMessage(content, sender, isMarkdown = false) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("msg", sender);

  if (isMarkdown && typeof marked !== "undefined") {
    msgDiv.innerHTML = marked.parse(content);
  } else {
    msgDiv.innerText = content;
  }

  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
  return msgDiv;
}