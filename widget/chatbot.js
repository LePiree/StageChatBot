/**
 * Wedding Chatbot Widget
 * Fichier autonome, sans dépendances — intégrable WordPress via snippet
 * 
 * Usage : <script src="chatbot.js" data-api-url="http://localhost:8000"></script>
 */
(function () {
  "use strict";

  // Capturer ici, pendant l'exécution synchrone du script (currentScript devient null après)
  const _scriptEl = document.currentScript;
  const _scriptSrc = _scriptEl ? _scriptEl.src : "";

  const API_URL = (_scriptEl && _scriptEl.dataset.apiUrl)
    ? _scriptEl.dataset.apiUrl.replace(/\/$/, "")
    : "http://localhost:8000";

  // ── État ─────────────────────────────────────────────────────────────────
  let conversationHistory = [];
  let isOpen = false;
  let isLoading = false;

  // ── Injection du CSS ─────────────────────────────────────────────────────
  function injectCSS() {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = _scriptSrc.replace("chatbot.js", "chatbot.css");
    document.head.appendChild(link);
  }

  // ── Construction du DOM ──────────────────────────────────────────────────
  function buildWidget() {
    // Bouton flottant
    const toggleBtn = document.createElement("button");
    toggleBtn.id = "wcb-toggle";
    toggleBtn.setAttribute("aria-label", "Ouvrir le chatbot");
    toggleBtn.innerHTML = "💬";

    // Fenêtre de chat
    const chatWindow = document.createElement("div");
    chatWindow.id = "wcb-window";
    chatWindow.setAttribute("aria-live", "polite");
    chatWindow.innerHTML = `
      <div id="wcb-header">
        <span>Assistant Mariage</span>
        <button id="wcb-close" aria-label="Fermer">✕</button>
      </div>
      <div id="wcb-messages"></div>
      <div id="wcb-input-area">
        <input id="wcb-input" type="text" placeholder="Posez votre question…" autocomplete="off" />
        <button id="wcb-send" aria-label="Envoyer">➤</button>
      </div>
    `;

    document.body.appendChild(toggleBtn);
    document.body.appendChild(chatWindow);

    // Message de bienvenue
    appendMessage("assistant", "Bonjour ! 💍 Je suis votre assistant mariage. Comment puis-je vous aider aujourd'hui ?");
  }

  // ── Affichage des messages ────────────────────────────────────────────────
  function appendMessage(role, text) {
    const messagesEl = document.getElementById("wcb-messages");
    const bubble = document.createElement("div");
    bubble.classList.add("wcb-bubble", role === "user" ? "wcb-user" : "wcb-assistant");
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setLoadingIndicator(show) {
    const existing = document.getElementById("wcb-loading");
    if (show && !existing) {
      const indicator = document.createElement("div");
      indicator.id = "wcb-loading";
      indicator.classList.add("wcb-bubble", "wcb-assistant");
      indicator.innerHTML = '<span class="wcb-dots"><span>.</span><span>.</span><span>.</span></span>';
      document.getElementById("wcb-messages").appendChild(indicator);
      document.getElementById("wcb-messages").scrollTop = 99999;
    } else if (!show && existing) {
      existing.remove();
    }
  }

  // ── Envoi d'un message ───────────────────────────────────────────────────
  async function sendMessage() {
    if (isLoading) return;

    const input = document.getElementById("wcb-input");
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    conversationHistory.push({ role: "user", content: text });
    appendMessage("user", text);

    isLoading = true;
    setLoadingIndicator(true);
    document.getElementById("wcb-send").disabled = true;

    try {
      const response = await fetch(API_URL + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: conversationHistory }),
      });

      if (!response.ok) {
        throw new Error("Erreur serveur : " + response.status);
      }

      const data = await response.json();
      const reply = data.response;
      conversationHistory.push({ role: "assistant", content: reply });
      setLoadingIndicator(false);
      appendMessage("assistant", reply);
    } catch (err) {
      setLoadingIndicator(false);
      appendMessage("assistant", "Désolé, une erreur est survenue. Veuillez réessayer.");
      console.error("[WeddingChatbot]", err);
    } finally {
      isLoading = false;
      document.getElementById("wcb-send").disabled = false;
      input.focus();
    }
  }

  // ── Gestion ouverture/fermeture ──────────────────────────────────────────
  function toggleWindow() {
    isOpen = !isOpen;
    const win = document.getElementById("wcb-window");
    const btn = document.getElementById("wcb-toggle");
    win.classList.toggle("wcb-open", isOpen);
    btn.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) {
      document.getElementById("wcb-input").focus();
    }
  }

  // ── Événements ──────────────────────────────────────────────────────────
  function bindEvents() {
    document.getElementById("wcb-toggle").addEventListener("click", toggleWindow);
    document.getElementById("wcb-close").addEventListener("click", toggleWindow);
    document.getElementById("wcb-send").addEventListener("click", sendMessage);
    document.getElementById("wcb-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // ── Init ─────────────────────────────────────────────────────────────────
  function init() {
    injectCSS();
    buildWidget();
    bindEvents();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
