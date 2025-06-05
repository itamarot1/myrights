// static/script.js

const chatbox = document.getElementById('chatbox');
const input = document.getElementById('userInput');
const profile = {};
let lastQuestion = "";
let isWaitingForFinal = false;

function addMessage(text, sender = 'bot') {
  const div = document.createElement('div');
  div.className = 'message ' + sender;
  div.textContent = text;
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function sendMessage() {
  const msg = input.value.trim();
  if (!msg || isWaitingForFinal) return;

  addMessage(msg, 'user');
  input.value = '';

  // זיהוי שדות מתוך השאלה האחרונה
  if (lastQuestion.includes("מה גילך") || lastQuestion.includes("בן כמה")) profile["age"] = msg;
  else if (lastQuestion.includes("עובד")) profile["employment_status"] = msg;
  else if (lastQuestion.includes("נכות")) profile["disability"] = msg;
  else if (lastQuestion.includes("צבא")) profile["military_service"] = msg;
  else if (lastQuestion.includes("משפחתי")) profile["marital_status"] = msg;

  addMessage("📋 פרופיל נוכחי: " + JSON.stringify(profile), 'bot');

  // שליחת פרופיל לשרת
  fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile })
  })
  .then(res => res.json())
  .then(data => {
    if (data.done === true) {
      isWaitingForFinal = true;
      addMessage("🔍 הסוכן שלנו מחשב את הדוח שלך...", 'bot');
      setTimeout(() => {
        addMessage(data.reply, 'bot');
        document.getElementById("reportButton").style.display = "block";
        isWaitingForFinal = false;
      }, 1500);
      return;
    }
    if (data.done === "no-rights") {
      addMessage(data.reply, 'bot');
      return;
    }
    lastQuestion = data.reply;
    addMessage(lastQuestion, 'bot');
  })
  .catch(() => {
    addMessage("אירעה שגיאה בתקשורת עם השרת.", 'bot');
  });
}

function showFinalReport() {
  alert("כאן תוכל להעביר את המשתמש לטופס השארת פרטים, לשלוח את הדוח באימייל או לחבר לעורך דין.");
}

window.onload = () => {
  fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile: {} })
  })
  .then(res => res.json())
  .then(data => {
    lastQuestion = data.reply;
    addMessage(lastQuestion, 'bot');
  });
};

input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") sendMessage();
});
