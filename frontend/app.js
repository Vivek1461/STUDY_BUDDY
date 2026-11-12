"use strict";

/*
 * Study Buddy frontend integration.
 * API origin can be overridden before app.js loads with:
 * window.STUDY_BUDDY_API_URL = "http://127.0.0.1:8000";
 */
const API_BASE_URL = (window.STUDY_BUDDY_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
const STORAGE_KEYS = {
  token: "studybuddy-access-token",
  session: "studybuddy-session-id",
  theme: "studybuddy-theme"
};

const root = document.documentElement;
const toast = document.getElementById("toast");
let toastTimer;
let activeMode = "teach";
let currentSession = null;
let currentFiles = [];
let isSending = false;
let isUploading = false;

function notify(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function setTheme(theme) {
  root.dataset.theme = theme;
  localStorage.setItem(STORAGE_KEYS.theme, theme);
  document.querySelectorAll(".theme-toggle").forEach((btn) => {
    const glyph = btn.querySelector("span");
    if (glyph) glyph.textContent = theme === "dark" ? "☀" : "☾";
    btn.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
  });
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = theme === "dark" ? "#172522" : "#f5f2e9";
}

const savedTheme = localStorage.getItem(STORAGE_KEYS.theme);
if (savedTheme === "dark" || savedTheme === "light") setTheme(savedTheme);
document.querySelectorAll(".theme-toggle").forEach((btn) => {
  btn.addEventListener("click", () => setTheme(root.dataset.theme === "dark" ? "light" : "dark"));
});

const viewNames = { home: "Overview", library: "My library", study: "Study space" };
function showView(name) {
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active-view"));
  const target = document.getElementById("view-" + name);
  if (!target) return;
  target.classList.add("active-view");
  const crumb = document.getElementById("crumb-current");
  if (crumb) crumb.textContent = viewNames[name] || name;
  document.querySelectorAll(".nav-link").forEach((button) => button.classList.toggle("active", button.dataset.view === name));
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (name === "library") loadLibrary();
  if (name === "study") updateStudyHeader();
}
document.querySelectorAll("[data-view]").forEach((element) => {
  element.addEventListener("click", () => showView(element.dataset.view));
});

function getToken() {
  return localStorage.getItem(STORAGE_KEYS.token);
}

async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token) headers.set("Authorization", "Bearer " + token);
  const response = await fetch(API_BASE_URL + path, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.session);
    throw new Error("Your guest session expired. Refresh the page to start a new session.");
  }
  if (!response.ok) {
    let message = "Request failed (" + response.status + ")";
    try {
      const data = await response.json();
      message = data.detail || data.message || message;
    } catch (_) {
      try { message = (await response.text()) || message; } catch (_) { }
    }
    throw new Error(message);
  }
  return response;
}

async function createGuestSession() {
  const response = await fetch(API_BASE_URL + "/api/auth/guest", { method: "POST" });
  if (!response.ok) {
    let detail = "Could not start guest mode (" + response.status + ")";
    try { detail = (await response.json()).detail || detail; } catch (_) { }
    throw new Error(detail);
  }
  const data = await response.json();
  if (!data.access_token || !data.session_id) throw new Error("Guest login returned an incomplete session.");
  localStorage.setItem(STORAGE_KEYS.token, data.access_token);
  localStorage.setItem(STORAGE_KEYS.session, data.session_id);
  currentSession = { id: data.session_id, label: "Guest study session", files: [] };
  return currentSession;
}

async function ensureGuestSession() {
  const token = getToken();
  const sessionId = localStorage.getItem(STORAGE_KEYS.session);
  if (token && sessionId) {
    try {
      const response = await apiRequest("/api/sessions/" + encodeURIComponent(sessionId));
      currentSession = await response.json();
      return currentSession;
    } catch (_) {
      localStorage.removeItem(STORAGE_KEYS.token);
      localStorage.removeItem(STORAGE_KEYS.session);
    }
  }
  return createGuestSession();
}

function setConnectionState(connected, label) {
  document.querySelectorAll(".preview-indicator").forEach((el) => {
    el.innerHTML = connected ? "<i></i> Backend connected" : "<i></i> " + (label || "Backend unavailable");
  });
  document.querySelectorAll(".conversation-preview").forEach((el) => {
    el.textContent = connected ? "LIVE STUDY SESSION" : "CONNECTION REQUIRED";
  });
  const source = document.querySelector(".source-status");
  if (source) source.innerHTML = connected ? "<i></i> Session connected" : "<i></i> Not connected";
  const foot = document.querySelector(".composer-foot span:last-child");
  if (foot) foot.textContent = connected ? "GROUNDED STUDY CHAT" : "BACKEND NOT CONNECTED";
}

function addMessage(role, text, options = {}) {
  const messages = document.getElementById("messages");
  const wrapper = document.createElement("div");
  let paragraph = null;

  if (role === "user") {
    wrapper.className = "user-message";
    paragraph = document.createElement("p");
    paragraph.textContent = text;
    wrapper.appendChild(paragraph);
  } else {
    wrapper.className = "assistant-message";
    const mark = document.createElement("div");
    mark.className = "assistant-mark";
    mark.textContent = "s";
    const spark = document.createElement("span");
    spark.textContent = "?";
    mark.appendChild(spark);

    const body = document.createElement("div");
    body.className = "message-body";
    const author = document.createElement("div");
    author.className = "message-author";
    author.textContent = "STUDY BUDDY";
    paragraph = document.createElement("p");
    paragraph.textContent = text || "";
    body.append(author, paragraph);

    if (options.note) {
      const note = document.createElement("div");
      note.className = "message-note";
      note.textContent = options.note;
      body.appendChild(note);
    }
    wrapper.append(mark, body);
  }

  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
  if (role !== "user" && options.returnParagraph) return paragraph;
  return wrapper;
}

function updateStudyHeader() {
  const name = currentFiles.length ? currentFiles[currentFiles.length - 1].original_name : "Your study session";
  const strong = document.querySelector(".study-doc-meta strong");
  const small = document.querySelector(".study-doc-meta small");
  if (strong) strong.textContent = name;
  if (small) small.textContent = currentFiles.length + " document" + (currentFiles.length === 1 ? "" : "s") + " in this session";
  const heading = document.querySelector(".study-heading > p");
  if (heading) heading.textContent = currentFiles.length
    ? "Ask questions grounded in your uploaded study material."
    : "Upload a document to begin a document-grounded study session.";
}

function fileIcon(file) {
  const ext = (file.original_name || "").split(".").pop().toLowerCase();
  return ext === "pdf" ? "PDF" : ext === "docx" ? "DOC" : ext === "pptx" ? "PPT" : ext.toUpperCase().slice(0, 3);
}

function renderRecentDocuments(files) {
  const container = document.getElementById("recent-documents");
  if (!container) return;
  container.replaceChildren();
  if (!files.length) {
    const empty = document.createElement("p");
    empty.className = "hero-description";
    empty.textContent = "No documents yet. Add your study material to get started.";
    container.appendChild(empty);
    return;
  }
  files.slice(-3).reverse().forEach((file) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "document-row";
    row.addEventListener("click", () => showView("study"));
    const thumb = document.createElement("span");
    thumb.className = "document-thumb pdf-thumb";
    const tag = document.createElement("b");
    tag.textContent = fileIcon(file);
    thumb.appendChild(tag);
    ["one", "two", "three"].forEach(() => {
      const line = document.createElement("i");
      thumb.appendChild(line);
    });
    const info = document.createElement("span");
    info.className = "document-info";
    const title = document.createElement("strong");
    title.textContent = file.original_name;
    const detail = document.createElement("small");
    detail.textContent = file.file_type.toUpperCase() + " · " + (file.chunk_count || 0) + " indexed chunks";
    info.append(title, detail);
    const status = document.createElement("span");
    status.className = "document-status" + (file.status === "ready" ? "" : " muted-status");
    status.textContent = file.status === "ready" ? "Ready" : file.status;
    const arrow = document.createElement("span");
    arrow.className = "row-chevron";
    arrow.textContent = "↗";
    row.append(thumb, info, status, arrow);
    container.appendChild(row);
  });
}

function renderLibrary(files) {
  currentFiles = Array.isArray(files) ? files : [];
  renderRecentDocuments(currentFiles);
  const list = document.getElementById("library-list");
  const empty = document.getElementById("library-empty");
  const summary = document.getElementById("library-summary");
  const count = document.getElementById("library-count");
  list.replaceChildren();
  currentFiles.forEach((file) => {
    const item = document.createElement("div");
    item.className = "library-item";
    item.dataset.search = (file.original_name + " " + file.file_type).toLowerCase();
    item.style.cursor = "default";

    const thumb = document.createElement("span");
    thumb.className = "document-thumb " + (file.file_type === "txt" ? "notes-thumb" : "pdf-thumb");
    const label = document.createElement("b");
    label.textContent = fileIcon(file);
    const line1 = document.createElement("i");
    const line2 = document.createElement("i");
    const line3 = document.createElement("i");
    thumb.append(label, line1, line2, line3);

    const info = document.createElement("span");
    info.className = "document-info";
    const title = document.createElement("strong");
    title.textContent = file.original_name;
    const detail = document.createElement("small");
    const size = Number(file.file_size || 0);
    detail.textContent = file.file_type.toUpperCase() + " · " + (size / 1024).toFixed(1) + " KB · " + (file.chunk_count || 0) + " chunks";
    info.append(title, detail);

    const status = document.createElement("span");
    status.className = "document-status" + (file.status === "ready" ? "" : " muted-status");
    status.textContent = file.status === "ready" ? "Indexed and ready" : file.status;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "button button-outline small-button";
    remove.textContent = "Remove";
    remove.setAttribute("aria-label", "Remove " + file.original_name);
    remove.addEventListener("click", () => deleteDocument(file.id, file.original_name));

    item.append(thumb, info, status, remove);
    list.appendChild(item);
  });
  if (empty) empty.hidden = currentFiles.length !== 0;
  if (summary) summary.textContent = currentFiles.length + " document" + (currentFiles.length === 1 ? "" : "s");
  if (count) count.textContent = String(currentFiles.length).padStart(2, "0");
  updateStudyHeader();
  filterLibrary();
}

async function loadLibrary() {
  if (!getToken()) return;
  try {
    const response = await apiRequest("/api/sessions");
    const sessions = await response.json();
    const session = sessions.find((item) => item.id === localStorage.getItem(STORAGE_KEYS.session));
    currentSession = session || currentSession;
    renderLibrary(session ? session.files : []);
  } catch (error) {
    notify("Could not load your library: " + error.message);
  }
}

async function deleteDocument(fileId, filename) {
  if (!window.confirm('Remove "' + filename + '" from this study session?')) return;
  try {
    await apiRequest("/api/upload/" + encodeURIComponent(fileId), { method: "DELETE" });
    notify("Document removed.");
    await loadLibrary();
  } catch (error) {
    notify("Could not remove document: " + error.message);
  }
}

const fileInput = document.getElementById("file-input");
function openPicker() {
  if (isUploading) return;
  fileInput.click();
}
document.getElementById("upload-trigger").addEventListener("click", openPicker);
document.getElementById("library-upload").addEventListener("click", openPicker);

async function uploadSelectedFiles(fileList) {
  const files = [...fileList];
  if (!files.length || isUploading) return;
  if (!getToken()) {
    notify("Guest session is not ready yet. Please try again.");
    return;
  }
  isUploading = true;
  const feedback = document.getElementById("upload-feedback");
  const allowed = /\.(pdf|docx|pptx|txt|jpg|jpeg|png)$/i;
  try {
    for (const file of files) {
      if (!allowed.test(file.name)) {
        notify("Unsupported file type: " + file.name);
        continue;
      }
      if (file.size === 0) {
        notify("This file is empty: " + file.name);
        continue;
      }
      feedback.textContent = "Uploading and indexing " + file.name + "…";
      const form = new FormData();
      form.append("file", file, file.name);
      form.append("session_id", currentSession.id);
      const response = await apiRequest("/api/upload", { method: "POST", body: form });
      const result = await response.json();
      currentSession.id = result.session_id;
      localStorage.setItem(STORAGE_KEYS.session, result.session_id);
      notify(result.message || (file.name + " uploaded successfully."));
    }
    await loadLibrary();
    feedback.textContent = files.length + " file upload operation(s) completed. Your library is synced with the backend.";
    showView("study");
    if (currentFiles.length) addMessage("assistant", "Your material is uploaded and indexed. Ask me a question about the documents in this session.", { note: "Answers are generated using retrieved passages from your uploaded material." });
  } catch (error) {
    feedback.textContent = "Upload failed: " + error.message;
    notify("Upload failed: " + error.message);
  } finally {
    isUploading = false;
    fileInput.value = "";
  }
}
fileInput.addEventListener("change", (event) => uploadSelectedFiles(event.target.files));

const search = document.getElementById("library-search");
function filterLibrary() {
  if (!search) return;
  const query = search.value.trim().toLowerCase();
  let shown = 0;
  document.querySelectorAll("#library-list .library-item").forEach((item) => {
    const match = (item.dataset.search || item.textContent).toLowerCase().includes(query);
    item.hidden = !match;
    if (match) shown++;
  });
  const empty = document.getElementById("library-empty");
  if (empty) {
    empty.hidden = currentFiles.length > 0 && (!query || shown > 0);
    if (query && shown === 0) {
      empty.hidden = false;
      const heading = empty.querySelector("h3");
      const paragraph = empty.querySelector("p");
      if (heading) heading.textContent = "No matching material";
      if (paragraph) paragraph.textContent = "Try another title or clear your search.";
    }
  }
  const summary = document.getElementById("library-summary");
  if (summary) summary.textContent = query ? shown + " matching document(s)" : currentFiles.length + " document(s)";
}
if (search) search.addEventListener("input", filterLibrary);

document.querySelectorAll(".mode-button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".mode-button").forEach((item) => item.classList.remove("selected"));
    button.classList.add("selected");
    activeMode = button.dataset.mode;
    notify(button.querySelector("b").textContent + " mode selected");
  });
});

async function loadChatHistory() {
  const messages = document.getElementById("messages");
  messages.replaceChildren();
  const response = await apiRequest("/api/chat/" + encodeURIComponent(currentSession.id) + "/messages");
  const history = await response.json();
  history.forEach((item) => addMessage(item.role === "user" ? "user" : "assistant", item.content));
  return history.length;
}

async function streamChat(message) {
  const response = await apiRequest("/api/chat/" + encodeURIComponent(currentSession.id) + "/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify({ message, action: activeMode })
  });
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let assistantParagraph = null;
  let answerStarted = false;

  function handleEvent(rawEvent) {
    const dataLine = rawEvent.split(/\r?\n/).find((line) => line.startsWith("data:"));
    if (!dataLine) return null;
    const raw = dataLine.slice(5).trim();
    if (!raw) return null;
    let event;
    try { event = JSON.parse(raw); } catch (_) { return null; }
    if (event.error) throw new Error(event.error);
    if (event.token) {
      if (!answerStarted) {
        assistantParagraph = addMessage("assistant", "", { returnParagraph: true });
        answerStarted = true;
      }
      assistantParagraph.textContent += event.token;
      const messages = document.getElementById("messages");
      messages.scrollTop = messages.scrollHeight;
    }
    if (event.done) return true;
    return null;
  }

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || "";
    for (const event of events) handleEvent(event);
  }
  buffer += decoder.decode();
  if (buffer.trim()) handleEvent(buffer);
  if (!answerStarted) addMessage("assistant", "The backend completed the request but returned no answer text.");
}

async function sendChatMessage(value) {
  if (isSending) return;
  if (!currentSession || !getToken()) {
    notify("Your guest session is not ready. Refresh and try again.");
    return;
  }
  if (!currentFiles.some((file) => file.status === "ready")) {
    notify("Upload and index a document before asking a question.");
    return;
  }
  isSending = true;
  const sendButton = document.querySelector("#chat-form button[type='submit']");
  if (sendButton) sendButton.disabled = true;
  addMessage("user", value);
  try {
    await streamChat(value);
  } catch (error) {
    addMessage("assistant", "I couldn't complete that request: " + error.message, { note: "Check your connection and backend logs, then try again." });
    notify("Chat request failed.");
  } finally {
    isSending = false;
    if (sendButton) sendButton.disabled = false;
  }
}

document.getElementById("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const value = input.value.trim();
  if (!value) return;
  input.value = "";
  input.style.height = "auto";
  await sendChatMessage(value);
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById("chat-input");
    input.value = button.dataset.prompt;
    input.focus();
  });
});

const textarea = document.getElementById("chat-input");
textarea.addEventListener("input", () => {
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 110) + "px";
});

const date = new Date();
document.getElementById("today-date").textContent =
  new Intl.DateTimeFormat("en", { weekday: "long", month: "long", day: "numeric" }).format(date).toUpperCase() +
  "  ·  A GOOD DAY TO GET CURIOUS";

(async function initializeStudyBuddy() {
  try {
    const session = await ensureGuestSession();
    setConnectionState(true);
    await loadLibrary();
    const historyCount = await loadChatHistory();
    if (!historyCount) {
      addMessage("assistant", currentFiles.length
        ? "Your guest session and uploaded documents are ready. Ask a question grounded in your material."
        : "Welcome to your study space. Your guest session is ready. Upload a PDF, DOCX, PPTX, TXT or image to start asking questions grounded in your material.");
    }
  } catch (error) {
    setConnectionState(false, "Backend unavailable");
    addMessage("assistant", "The frontend loaded, but it could not connect to the Study Buddy backend: " + error.message, { note: "Start the FastAPI server at " + API_BASE_URL + " and refresh this page." });
    notify("Backend connection failed. Check that FastAPI is running.");
  }
})();
