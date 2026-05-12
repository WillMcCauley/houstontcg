const APP_CONFIG = {
  apiBase: window.HOUSTON_TCG_API_BASE || "http://127.0.0.1:8001",
  fallbackCatalogPath: "backend/data/products.json",
  productLimit: 3
};

const STORAGE_KEY = "houston-tcg-copilot-session-id";

const grid = document.getElementById("product-grid");
const template = document.getElementById("product-card-template");
const chatShell = document.getElementById("chat-shell");
const chatFab = document.getElementById("chat-fab");
const chatClose = document.getElementById("chat-close");
const heroChatTrigger = document.getElementById("hero-chat-trigger");
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatStatus = document.querySelector(".chat-status");
const quickPromptsToggle = document.getElementById("quick-prompts-toggle");
const promptChipsWrap = document.getElementById("prompt-chips");
const promptChips = document.querySelectorAll(".prompt-chip");

const starterMessages = [
  {
    html:
      "Hi! I’m the Houston TCG AI Sales and Support Copilot. Ask about products, gifts, bundles, pickup, shipping, payments, or Facebook Marketplace purchase help."
  },
  {
    html:
      "Try questions like <strong>best gift for a Pokemon fan</strong>, <strong>show me something collectible</strong>, or <strong>how do I buy on Facebook Marketplace?</strong>"
  }
];

let sessionId = loadSessionId();
let isChatBusy = false;

function loadSessionId() {
  const existing = window.localStorage.getItem(STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const generated =
    window.crypto && "randomUUID" in window.crypto
      ? window.crypto.randomUUID()
      : `session-${Date.now()}`;
  window.localStorage.setItem(STORAGE_KEY, generated);
  return generated;
}

function setChatStatus(text, mode = "ready") {
  chatStatus.textContent = text;
  chatStatus.dataset.mode = mode;
}

function normalizeProducts(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload && Array.isArray(payload.products)) {
    return payload.products;
  }

  return [];
}

async function fetchCatalog() {
  const apiUrl = `${APP_CONFIG.apiBase}/api/products`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`Product API returned ${response.status}`);
    }

    const payload = await response.json();
    setChatStatus("AI Copilot Live", "ready");
    return normalizeProducts(payload);
  } catch (error) {
    setChatStatus("Catalog Fallback", "warning");
    const fallbackResponse = await fetch(APP_CONFIG.fallbackCatalogPath);
    if (!fallbackResponse.ok) {
      throw new Error("Unable to load product catalog.");
    }

    const fallbackPayload = await fallbackResponse.json();
    return normalizeProducts(fallbackPayload);
  }
}

function logFeedback(eventType, productId = null, metadata = {}) {
  return fetch(`${APP_CONFIG.apiBase}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      event_type: eventType,
      product_id: productId,
      metadata
    }),
    keepalive: true
  }).catch(() => undefined);
}

function attachProductTracking(link, productId, source) {
  link.addEventListener("click", () => {
    logFeedback("product_click", productId, { source });
  });
}

function createProductCard(product) {
  const fragment = template.content.cloneNode(true);
  const card = fragment.querySelector(".product-card");
  const image = fragment.querySelector(".product-image");
  const fallback = fragment.querySelector(".image-fallback");
  const category = fragment.querySelector(".product-category");
  const title = fragment.querySelector(".product-title");
  const description = fragment.querySelector(".product-description");
  const link = fragment.querySelector(".purchase-link");

  card.dataset.productId = product.id;
  image.src = product.image_url;
  image.alt = product.title;
  image.addEventListener("load", () => {
    fallback.hidden = true;
  });
  image.addEventListener("error", () => {
    image.style.display = "none";
    fallback.hidden = false;
  });

  category.textContent = product.category;
  title.textContent = product.title;
  description.textContent = product.description;
  link.href = product.listing_url;
  link.setAttribute("aria-label", `Purchase ${product.title} on Facebook Marketplace`);
  attachProductTracking(link, product.id, "grid");

  return fragment;
}

function renderCatalogNotice(message) {
  const notice = document.createElement("article");
  notice.className = "catalog-notice";
  notice.innerHTML = `<p>${message}</p>`;
  grid.appendChild(notice);
}

async function renderProducts() {
  grid.innerHTML = "";

  try {
    const products = await fetchCatalog();
    products.forEach((product) => {
      grid.appendChild(createProductCard(product));
    });
  } catch (error) {
    renderCatalogNotice(
      "The storefront catalog could not load right now. Start the backend API or refresh to try again."
    );
  }
}

function createChatProductCard(item) {
  const product = item.product;
  const wrapper = document.createElement("article");
  wrapper.className = "chat-product-card";

  const title = document.createElement("h4");
  title.className = "chat-product-title";
  title.textContent = product.title;

  const meta = document.createElement("p");
  meta.className = "chat-product-meta";
  const reason =
    item.reason || item.explanation || `Relevant match score: ${item.score.toFixed(3)}`;
  meta.textContent = `${product.category} • ${reason}`;

  const status = document.createElement("p");
  status.className = "chat-product-status";
  status.textContent = product.availability;

  const link = document.createElement("a");
  link.className = "chat-product-link";
  link.href = product.listing_url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "Open Facebook Marketplace listing";
  attachProductTracking(link, product.id, "chat");

  wrapper.append(title, meta, status, link);
  return wrapper;
}

function appendMessage(role, payload) {
  const message = document.createElement("div");
  message.className = `chat-bubble ${role}`;

  if (payload.loading) {
    message.classList.add("loading");
  }

  const content = document.createElement("div");
  content.className = "chat-message-content";
  if (payload.html) {
    content.innerHTML = `<p>${payload.html}</p>`;
  }
  message.appendChild(content);

  if (payload.products && payload.products.length > 0) {
    const productGrid = document.createElement("div");
    productGrid.className = "chat-response-products";
    payload.products.forEach((item) => {
      productGrid.appendChild(createChatProductCard(item));
    });
    message.appendChild(productGrid);
  }

  if (payload.nextAction) {
    const nextAction = document.createElement("p");
    nextAction.className = "chat-next-action";
    nextAction.textContent = payload.nextAction;
    message.appendChild(nextAction);
  }

  if (payload.policyHits && payload.policyHits.length > 0) {
    const policies = document.createElement("p");
    policies.className = "chat-hint";
    policies.textContent = `Grounded in: ${payload.policyHits
      .map((item) => item.title)
      .join(", ")}`;
    message.appendChild(policies);
  }

  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return message;
}

function setChatOpen(isOpen) {
  chatShell.classList.toggle("is-collapsed", !isOpen);
  chatFab.setAttribute("aria-expanded", String(isOpen));
  chatFab.textContent = isOpen ? "Hide Houston TCG Chat" : "Chat with Houston TCG";

  if (isOpen) {
    window.setTimeout(() => {
      chatInput.focus();
    }, 160);
  }
}

function setQuickPromptsExpanded(isExpanded) {
  promptChipsWrap.classList.toggle("is-collapsed", !isExpanded);
  quickPromptsToggle.setAttribute("aria-expanded", String(isExpanded));
  quickPromptsToggle.textContent = isExpanded ? "Minimize" : "Show";
}

function renderStarterMessages() {
  starterMessages.forEach((message) => appendMessage("bot", message));
}

async function sendChatRequest(message) {
  const response = await fetch(`${APP_CONFIG.apiBase}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      limit: APP_CONFIG.productLimit
    })
  });

  if (!response.ok) {
    throw new Error(`Chat API returned ${response.status}`);
  }

  return response.json();
}

async function handleUserMessage(message) {
  const cleanMessage = message.trim();
  if (!cleanMessage || isChatBusy) {
    return;
  }

  setChatOpen(true);
  appendMessage("user", { html: cleanMessage });
  const loadingBubble = appendMessage("bot", {
    html: "Thinking through your request and checking inventory...",
    loading: true
  });

  isChatBusy = true;
  setChatStatus("Responding...", "loading");

  try {
    const payload = await sendChatRequest(cleanMessage);
    sessionId = payload.session_id || sessionId;
    window.localStorage.setItem(STORAGE_KEY, sessionId);
    loadingBubble.remove();

    appendMessage("bot", {
      html: payload.answer,
      nextAction: payload.next_action,
      products: payload.products || [],
      policyHits: payload.policy_hits || []
    });

    setChatStatus(`Intent: ${payload.intent}`, payload.fallback ? "warning" : "ready");
  } catch (error) {
    loadingBubble.remove();
    appendMessage("bot", {
      html:
        "The AI copilot backend is unavailable right now. Start the FastAPI service to enable live recommendations, policy answers, and analytics logging."
    });
    setChatStatus("API Offline", "error");
  } finally {
    isChatBusy = false;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

function initializeChat() {
  renderStarterMessages();

  chatFab.addEventListener("click", () => {
    const shouldOpen = chatShell.classList.contains("is-collapsed");
    setChatOpen(shouldOpen);
  });

  chatClose.addEventListener("click", () => {
    setChatOpen(false);
  });

  heroChatTrigger.addEventListener("click", () => {
    setChatOpen(true);
  });

  quickPromptsToggle.addEventListener("click", () => {
    const isExpanded = quickPromptsToggle.getAttribute("aria-expanded") === "true";
    setQuickPromptsExpanded(!isExpanded);
  });

  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = chatInput.value;
    chatInput.value = "";
    handleUserMessage(value);
  });

  promptChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.dataset.prompt || "";
      handleUserMessage(prompt);
    });
  });
}

renderProducts();
initializeChat();
