const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

const TOKEN_KEY = "rag_auth_token";

export function newThreadId() {
  return crypto.randomUUID();
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(extraHeaders = {}) {
  const token = getToken();

  if (!token) {
    return extraHeaders;
  }

  return {
    ...extraHeaders,
    Authorization: `Bearer ${token}`,
  };
}

async function handleResponse(res) {
  if (!res.ok) {
    const errorText = await res.text();

    if (res.status === 401) {
      clearToken();
      throw new Error("Session expired. Please login again.");
    }

    throw new Error(errorText);
  }

  return res.json();
}

export async function registerUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  return handleResponse(res);
}

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await handleResponse(res);

  setToken(data.access_token);

  return data;
}

export async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: authHeaders(),
  });

  return handleResponse(res);
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  return handleResponse(res);
}

export async function uploadMultipleDocuments(files) {
  const results = [];

  for (const file of files) {
    const result = await uploadDocument(file);
    results.push(result);
  }

  return results;
}

export async function listDocuments() {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: authHeaders(),
  });

  return handleResponse(res);
}

export async function deleteDocument(documentId) {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  return handleResponse(res);
}

export async function getEvaluationSummary() {
  const res = await fetch(`${API_BASE}/evaluations/summary`, {
    headers: authHeaders(),
  });

  return handleResponse(res);
}

export async function streamQuestion(question, threadId, onToken, onSources) {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: authHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({
      question,
      thread_id: threadId,
      top_k: 4,
    }),
  });

  if (!res.ok || !res.body) {
    const errorText = await res.text();

    if (res.status === 401) {
      clearToken();
      throw new Error("Session expired. Please login again.");
    }

    throw new Error(errorText);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      if (!part.startsWith("data: ")) continue;

      const payload = JSON.parse(part.replace("data: ", "").trim());

      if (payload.token) onToken(payload.token);
      if (payload.sources && onSources) onSources(payload.sources);
      if (payload.done) return;
    }
  }
}

export async function listThreads() {
  const res = await fetch(`${API_BASE}/threads`, {
    headers: authHeaders(),
  });

  return handleResponse(res);
}

export async function getThreadMessages(threadId) {
  const res = await fetch(`${API_BASE}/threads/${threadId}/messages`, {
    headers: authHeaders(),
  });

  return handleResponse(res);
}