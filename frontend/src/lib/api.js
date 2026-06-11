
// const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

// export function newThreadId() {
//   return crypto.randomUUID();
// }

// export async function uploadDocument(file) {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch(`${API_BASE}/upload`, {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) throw new Error(await res.text());
//   return res.json();
// }

// export async function askQuestion(question, threadId) {
//   const res = await fetch(`${API_BASE}/chat`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       question,
//       thread_id: threadId,
//       top_k: 4,
//     }),
//   });

//   if (!res.ok) throw new Error(await res.text());
//   return res.json();
// }

// export async function streamQuestion(question, threadId, onToken) {
//   const res = await fetch(`${API_BASE}/chat/stream`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       question,
//       thread_id: threadId,
//       top_k: 4,
//     }),
//   });

//   if (!res.ok || !res.body) {
//     throw new Error(await res.text());
//   }

//   const reader = res.body.getReader();
//   const decoder = new TextDecoder();

//   let buffer = "";

//   while (true) {
//     const { value, done } = await reader.read();

//     if (done) break;

//     buffer += decoder.decode(value, { stream: true });

//     const parts = buffer.split("\n\n");
//     buffer = parts.pop() || "";

//     for (const part of parts) {
//       if (!part.startsWith("data: ")) continue;

//       const jsonText = part.replace("data: ", "").trim();

//       if (!jsonText) continue;

//       const payload = JSON.parse(jsonText);

//       if (payload.token) {
//         onToken(payload.token);
//       }

//       if (payload.done) {
//         return;
//       }
//     }
//   }
// }

// export async function listThreads() {
//   const res = await fetch(`${API_BASE}/threads`);

//   if (!res.ok) throw new Error(await res.text());

//   return res.json();
// }

// export async function getThreadMessages(threadId) {
//   const res = await fetch(`${API_BASE}/threads/${threadId}/messages`);

//   if (!res.ok) throw new Error(await res.text());

//   return res.json();
// }


const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

export function newThreadId() {
  return crypto.randomUUID();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
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
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteDocument(documentId) {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getEvaluationSummary() {
  const res = await fetch(`${API_BASE}/evaluations/summary`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function streamQuestion(question, threadId, onToken, onSources) {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      thread_id: threadId,
      top_k: 4,
    }),
  });

  if (!res.ok || !res.body) {
    throw new Error(await res.text());
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
  const res = await fetch(`${API_BASE}/threads`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getThreadMessages(threadId) {
  const res = await fetch(`${API_BASE}/threads/${threadId}/messages`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}