const storeProfile = {
  businessName: "Houston TCG",
  assistantName: "Houston TCG Bot",
  city: "Houston",
  state: "Texas",
  fulfillment: ["local meetup", "porch pickup", "shipping when arranged"],
  paymentOptions: ["cash", "Zelle", "Cash App", "Facebook Marketplace checkout when enabled"],
  supportTone:
    "friendly, fast, and focused on helping buyers reach the right Facebook Marketplace listing"
};

const products = [
  {
    id: "outlaws-kit",
    category: "MTG",
    title: "Outlaws of Thunder Junction Deluxe Commander Kit",
    description:
      "A featured Magic: The Gathering item for players and collectors looking for a premium Commander pickup.",
    image: "images/outlaws-of-thunder-junction-deluxe-commander-kit.jpeg",
    fbUrl: "https://www.facebook.com/marketplace/item/1216163437111287",
    keywords: ["mtg", "magic", "magic the gathering", "outlaws", "thunder junction", "commander", "deluxe commander kit"],
    tags: ["cards", "collectible", "tcg", "commander"]
  },
  {
    id: "iphone-14",
    category: "Electronics",
    title: "iPhone 14 128GB - Black",
    description:
      "A clean, high-demand phone listing that fits perfectly alongside collectibles and resale finds.",
    image: "images/iphone-14-128gb-black.webp",
    fbUrl: "https://www.facebook.com/marketplace/item/1285667683751650",
    keywords: ["iphone", "iphone 14", "phone", "apple", "128gb", "black iphone"],
    tags: ["electronics", "phone", "apple"]
  },
  {
    id: "lego-good-fortune",
    category: "Lego",
    title: "Lego Good Fortune Set",
    description:
      "A standout building set for collectors, gift buyers, and anyone hunting for a fun display piece.",
    image: "images/lego-good-fortune-set.jpg",
    fbUrl: "https://www.facebook.com/marketplace/item/1064221970107751",
    keywords: ["lego", "good fortune", "lego set", "building set"],
    tags: ["lego", "collectible", "display"]
  },
  {
    id: "kidkraft-market",
    category: "Kids",
    title: "Kidkraft Fresh Farm Market Stand",
    description:
      "A larger-item listing with a family-friendly angle, great for broadening the shop mix beyond cards.",
    image: "images/kidkraft-fresh-farm-market-stand.jpg",
    fbUrl: "https://www.facebook.com/marketplace/item/978858158419038",
    keywords: ["kidkraft", "fresh farm", "market stand", "farm stand", "kids stand"],
    tags: ["kids", "play", "furniture"]
  },
  {
    id: "pikachu-squishmallow",
    category: "Collectibles",
    title: 'Pikachu Squishmallow 20"',
    description:
      "A recognizable fan-favorite plush listing that fits the collectible and pop-culture side of the brand.",
    image: "images/pikachu-squishmallow-20-inch.jpg",
    fbUrl: "https://www.facebook.com/marketplace/item/839622288569049",
    keywords: ["pikachu", "squishmallow", "plush", "pokemon", "20 inch pikachu"],
    tags: ["pokemon", "plush", "collectible"]
  },
  {
    id: "pikachu-bundle",
    category: "Bundle",
    title: "Pikachu & Fresh Market Stand Bundle",
    description:
      "A bundle card for a combined offer, useful when you want a playful featured package on the storefront.",
    image: "images/pikachu-fresh-market-stand-bundle.jpg",
    fbUrl: "https://www.facebook.com/marketplace/item/958655823830399",
    keywords: ["bundle", "pikachu bundle", "fresh market bundle", "market stand bundle", "combo"],
    tags: ["bundle", "pokemon", "kids"]
  }
];

const grid = document.getElementById("product-grid");
const template = document.getElementById("product-card-template");
const chatShell = document.getElementById("chat-shell");
const chatFab = document.getElementById("chat-fab");
const chatClose = document.getElementById("chat-close");
const heroChatTrigger = document.getElementById("hero-chat-trigger");
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const quickPromptsToggle = document.getElementById("quick-prompts-toggle");
const promptChipsWrap = document.getElementById("prompt-chips");
const promptChips = document.querySelectorAll(".prompt-chip");

const starterMessages = [
  `Hi! I'm ${storeProfile.assistantName}. Ask me about inventory, bundles, how to buy on Facebook Marketplace, or which item fits what you're looking for.`,
  `Try questions like "show me the MTG item", "do you have a bundle?", or "how do I buy the iPhone?"`
];

function createProductCard(product) {
  const fragment = template.content.cloneNode(true);
  const image = fragment.querySelector(".product-image");
  const fallback = fragment.querySelector(".image-fallback");
  const category = fragment.querySelector(".product-category");
  const title = fragment.querySelector(".product-title");
  const description = fragment.querySelector(".product-description");
  const link = fragment.querySelector(".purchase-link");

  image.src = product.image;
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
  link.href = product.fbUrl;
  link.setAttribute("aria-label", `Purchase ${product.title} on Facebook Marketplace`);

  return fragment;
}

function renderProducts() {
  products.forEach((product) => {
    grid.appendChild(createProductCard(product));
  });
}

function normalizeText(text) {
  return text.toLowerCase().replace(/[^\w\s"]/g, " ").replace(/\s+/g, " ").trim();
}

function detectProducts(message) {
  const normalized = normalizeText(message);

  return products.filter((product) => {
    if (normalized.includes(product.title.toLowerCase())) {
      return true;
    }

    return product.keywords.some((keyword) => normalized.includes(keyword));
  });
}

function detectIntent(message) {
  const normalized = normalizeText(message);

  const intents = {
    buy: ["buy", "purchase", "order", "get it", "marketplace", "link", "listing"],
    bundle: ["bundle", "combo", "together", "pair"],
    inventory: ["show", "have", "available", "inventory", "items", "stock", "sell"],
    shipping: ["ship", "shipping", "deliver", "delivery", "pickup", "meet", "meetup", "local"],
    payment: ["pay", "payment", "cash", "zelle", "cash app"],
    greeting: ["hi", "hello", "hey"],
    help: ["help", "what can you do", "how does this work"],
    categoryMtg: ["mtg", "magic", "commander", "cards", "tcg"],
    categoryPokemon: ["pokemon", "pikachu", "plush"],
    categoryKids: ["kids", "toy", "market stand", "kidkraft"],
    categoryElectronics: ["iphone", "phone", "apple", "electronics"]
  };

  return Object.entries(intents)
    .filter(([, keywords]) => keywords.some((keyword) => normalized.includes(keyword)))
    .map(([intent]) => intent);
}

function formatProductLine(product) {
  return `<strong>${product.title}</strong> <a href="${product.fbUrl}" target="_blank" rel="noopener noreferrer">Open listing</a>`;
}

function buildInventoryReply(selectedProducts) {
  if (selectedProducts.length === 1) {
    const product = selectedProducts[0];
    return `I found the match: ${formatProductLine(product)}. ${product.description}`;
  }

  if (selectedProducts.length > 1) {
    return `Here are the closest matches:<br>${selectedProducts
      .map((product) => `• ${formatProductLine(product)}`)
      .join("<br>")}`;
  }

  return `Right now the site features ${products.length} items: ${products
    .map((product) => product.title)
    .join(", ")}. Tell me a product name or category and I’ll point you to the right listing.`;
}

function buildPurchaseReply(selectedProducts) {
  if (selectedProducts.length > 0) {
    return selectedProducts
      .map(
        (product) =>
          `You can buy <strong>${product.title}</strong> here: <a href="${product.fbUrl}" target="_blank" rel="noopener noreferrer">click to open the Facebook Marketplace listing</a>.`
      )
      .join("<br><br>");
  }

  return `Choose any product card or tell me which item you want, and I’ll send you to the exact Facebook Marketplace listing.`;
}

function buildShippingReply() {
  return `${storeProfile.businessName} can be described as offering ${storeProfile.fulfillment.join(
    ", "
  )}. Update this wording in <code>storeProfile</code> if you want the bot to reflect your exact pickup and shipping rules.`;
}

function buildPaymentReply() {
  return `Typical payment options listed by the bot are ${storeProfile.paymentOptions.join(
    ", "
  )}. You can customize those in <code>storeProfile</code> inside <code>app.js</code>.`;
}

function buildCategoryReply(intents) {
  if (intents.includes("categoryMtg")) {
    return buildInventoryReply(products.filter((product) => product.category === "MTG"));
  }

  if (intents.includes("categoryElectronics")) {
    return buildInventoryReply(products.filter((product) => product.category === "Electronics"));
  }

  if (intents.includes("categoryKids")) {
    return buildInventoryReply(
      products.filter((product) => ["Kids", "Bundle"].includes(product.category))
    );
  }

  if (intents.includes("categoryPokemon")) {
    return buildInventoryReply(
      products.filter((product) => product.tags.includes("pokemon"))
    );
  }

  return "";
}

function generateBotReply(message) {
  const intents = detectIntent(message);
  const selectedProducts = detectProducts(message);
  const categoryReply = buildCategoryReply(intents);

  if (intents.includes("greeting")) {
    return `Hi! I can help visitors browse ${storeProfile.businessName} listings, find product matches, and jump straight to Facebook Marketplace purchase links.`;
  }

  if (intents.includes("help")) {
    return `You can ask about product names, bundles, MTG items, the iPhone, pickup, shipping, payment methods, or how to buy through Facebook Marketplace.`;
  }

  if (selectedProducts.length > 0 && intents.includes("buy")) {
    return buildPurchaseReply(selectedProducts);
  }

  if (selectedProducts.length > 0) {
    return buildInventoryReply(selectedProducts);
  }

  if (intents.includes("bundle")) {
    return buildInventoryReply(products.filter((product) => product.category === "Bundle"));
  }

  if (intents.includes("shipping")) {
    return buildShippingReply();
  }

  if (intents.includes("payment")) {
    return buildPaymentReply();
  }

  if (intents.includes("inventory") || categoryReply) {
    return categoryReply || buildInventoryReply([]);
  }

  if (intents.includes("buy")) {
    return buildPurchaseReply([]);
  }

  return `I’m not fully sure which item you mean yet. Try asking for "the iPhone", "the MTG item", "the Pikachu bundle", or "how do I buy on Facebook Marketplace?"`;
}

function appendMessage(role, html) {
  const message = document.createElement("div");
  message.className = `chat-bubble ${role}`;
  message.innerHTML = `<p>${html}</p>`;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
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

function handleUserMessage(message) {
  const cleanMessage = message.trim();

  if (!cleanMessage) {
    return;
  }

  appendMessage("user", cleanMessage);

  window.setTimeout(() => {
    appendMessage("bot", generateBotReply(cleanMessage));
  }, 280);
}

function initializeChat() {
  starterMessages.forEach((message) => appendMessage("bot", message));

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
    setChatOpen(true);
    handleUserMessage(chatInput.value);
    chatInput.value = "";
    chatInput.focus();
  });

  promptChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.dataset.prompt || "";
      setChatOpen(true);
      handleUserMessage(prompt);
    });
  });
}

renderProducts();
initializeChat();
