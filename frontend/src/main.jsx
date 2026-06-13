// // import React, { useEffect, useState } from "react";
// // import { createRoot } from "react-dom/client";
// // import { Upload, Send, Plus } from "lucide-react";
// // import { uploadDocument, streamQuestion, listThreads, getThreadMessages, newThreadId } from "./lib/api";
// // import "./style.css";

// // function App() {
// //   const [file, setFile] = useState(null);
// //   const [status, setStatus] = useState("");
// //   const [question, setQuestion] = useState("");
// //   const [messages, setMessages] = useState([]);
// //   const [loading, setLoading] = useState(false);
// //   const [threadId, setThreadId] = useState(localStorage.getItem("thread_id") || newThreadId());
// //   const [threads, setThreads] = useState([]);

// //   useEffect(() => { localStorage.setItem("thread_id", threadId); refreshThreads(); }, [threadId]);

// //   async function refreshThreads() {
// //     try { setThreads(await listThreads()); } catch {}
// //   }

// //   async function loadThread(id) {
// //     setThreadId(id);
// //     const rows = await getThreadMessages(id);
// //     setMessages(rows.map(r => ({ role: r.role, text: r.content, sources: r.sources })));
// //   }

// //   function startNewChat() {
// //     const id = newThreadId();
// //     setThreadId(id);
// //     setMessages([]);
// //   }

// //   async function handleUpload() {
// //     if (!file) return;
// //     setLoading(true);
// //     try {
// //       const data = await uploadDocument(file);
// //       setStatus(`${data.filename} indexed successfully. Chunks: ${data.chunks_added}`);
// //     } catch (e) { setStatus(`Upload failed: ${e.message}`); }
// //     finally { setLoading(false); }
// //   }

// //   async function handleAsk(e) {
// //     e.preventDefault();
// //     if (!question.trim()) return;
// //     const userQuestion = question;
// //     setQuestion("");
// //     setMessages(m => [...m, { role: "user", text: userQuestion }, { role: "assistant", text: "" }]);
// //     setLoading(true);
// //     try {
// //       await streamQuestion(userQuestion, threadId, (token) => {
// //         setMessages(m => {
// //           const copy = [...m];
// //           copy[copy.length - 1] = { ...copy[copy.length - 1], text: copy[copy.length - 1].text + token };
// //           return copy;
// //         });
// //       });
// //       refreshThreads();
// //     } catch (e) {
// //       setMessages(m => [...m, { role: "assistant", text: `Error: ${e.message}` }]);
// //     } finally { setLoading(false); }
// //   }

// //   return <main className="layout">
// //     <aside className="sidebar">
// //       <button className="new" onClick={startNewChat}><Plus size={16}/> New Chat</button>
// //       <h3>Threads</h3>
// //       {threads.map(t => <button key={t.id} className="thread" onClick={() => loadThread(t.id)}>{t.title}</button>)}
// //     </aside>
// //     <section className="app">
// //       <section className="hero"><h1>Production RAG Assistant</h1><p>Persistent RAG with SQLite threads, Chroma vector storage, and streaming answers.</p></section>
// //       <section className="card upload-card"><input type="file" accept=".pdf,.txt" onChange={e => setFile(e.target.files[0])}/><button onClick={handleUpload} disabled={!file || loading}><Upload size={16}/> Upload & Index</button>{status && <p className="status">{status}</p>}</section>
// //       <section className="card chat-card"><div className="messages">{messages.map((m,i)=><div key={i} className={`msg ${m.role}`}><b>{m.role}</b><p>{m.text}</p>{m.sources?.length>0 && <details><summary>Sources</summary>{m.sources.map((s,j)=><p key={j}>{s.filename} {s.page!==null?`page ${s.page+1}`:""}: {s.preview}</p>)}</details>}</div>)}</div><form onSubmit={handleAsk}><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask your document..."/><button disabled={loading}><Send size={16}/> Send</button></form></section>
// //     </section>
// //   </main>;
// // }

// // createRoot(document.getElementById("root")).render(<App />);


// import React, { useEffect, useState } from "react";
// import { createRoot } from "react-dom/client";
// import { Upload, Send, Plus, Trash2, FileText, BarChart3 } from "lucide-react";

// import {
//   uploadMultipleDocuments,
//   streamQuestion,
//   listThreads,
//   getThreadMessages,
//   newThreadId,
//   listDocuments,
//   deleteDocument,
//   getEvaluationSummary,
// } from "./lib/api";

// import "./style.css";

// function App() {
//   const [files, setFiles] = useState([]);
//   const [status, setStatus] = useState("");
//   const [question, setQuestion] = useState("");
//   const [messages, setMessages] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const [threadId, setThreadId] = useState(
//     localStorage.getItem("thread_id") || newThreadId()
//   );

//   const [threads, setThreads] = useState([]);
//   const [documents, setDocuments] = useState([]);
//   const [summary, setSummary] = useState(null);

//   useEffect(() => {
//     localStorage.setItem("thread_id", threadId);
//     refreshThreads();
//     refreshDocuments();
//     refreshSummary();
//   }, [threadId]);

//   async function refreshThreads() {
//     try {
//       setThreads(await listThreads());
//     } catch {}
//   }

//   async function refreshDocuments() {
//     try {
//       setDocuments(await listDocuments());
//     } catch {}
//   }

//   async function refreshSummary() {
//     try {
//       setSummary(await getEvaluationSummary());
//     } catch {}
//   }

//   async function loadThread(id) {
//     setThreadId(id);
//     const rows = await getThreadMessages(id);

//     setMessages(
//       rows.map((r) => ({
//         role: r.role,
//         text: r.content,
//         sources: r.sources || [],
//       }))
//     );
//   }

//   // function startNewChat() {
//   //   const id = newThreadId();
//   //   setThreadId(id);
//   //   setMessages([]);
//   // }

// //   function startNewChat() {
// //     const id = newThreadId();

// //     localStorage.setItem("thread_id", id);
// //     setThreadId(id);
// //     setMessages([]);
// //     setQuestion("");
// // }

//   function startNewChat() {
//     const id = newThreadId();

//     localStorage.removeItem("thread_id");
//     localStorage.setItem("thread_id", id);

//     setThreadId(id);
//     setMessages([]);
//     setQuestion("");
//     setStatus("");

//     window.history.replaceState(null, "", "/");
// }

//   async function handleUpload() {
//     if (!files.length) return;

//     setLoading(true);
//     setStatus("Uploading and indexing documents...");

//     try {
//       const results = await uploadMultipleDocuments(files);

//       const totalChunks = results.reduce(
//         (sum, item) => sum + item.chunks_added,
//         0
//       );

//       setStatus(
//         `${results.length} document(s) indexed successfully. Total chunks: ${totalChunks}`
//       );

//       setFiles([]);
//       await refreshDocuments();
//       await refreshSummary();
//     } catch (e) {
//       setStatus(`Upload failed: ${e.message}`);
//     } finally {
//       setLoading(false);
//     }
//   }

//   async function handleDeleteDocument(documentId) {
//     const confirmDelete = confirm("Delete this document and its vector chunks?");

//     if (!confirmDelete) return;

//     try {
//       await deleteDocument(documentId);
//       await refreshDocuments();
//       await refreshSummary();
//       setStatus("Document deleted successfully.");
//     } catch (e) {
//       setStatus(`Delete failed: ${e.message}`);
//     }
//   }

//   async function handleAsk(e) {
//     e.preventDefault();

//     if (!question.trim()) return;

//     const userQuestion = question;
//     setQuestion("");

//     setMessages((m) => [
//       ...m,
//       { role: "user", text: userQuestion, sources: [] },
//       { role: "assistant", text: "", sources: [] },
//     ]);

//     setLoading(true);

//     try {
//       await streamQuestion(
//         userQuestion,
//         threadId,
//         (token) => {
//           setMessages((m) => {
//             const copy = [...m];
//             const last = copy[copy.length - 1];

//             copy[copy.length - 1] = {
//               ...last,
//               text: last.text + token,
//             };

//             return copy;
//           });
//         },
//         (sources) => {
//           setMessages((m) => {
//             const copy = [...m];
//             const last = copy[copy.length - 1];

//             copy[copy.length - 1] = {
//               ...last,
//               sources,
//             };

//             return copy;
//           });
//         }
//       );

//       await refreshThreads();
//       await refreshSummary();
//     } catch (e) {
//       setMessages((m) => [
//         ...m,
//         {
//           role: "assistant",
//           text: `Error: ${e.message}`,
//           sources: [],
//         },
//       ]);
//     } finally {
//       setLoading(false);
//     }
//   }

//   return (
//     <main className="layout">
//       <aside className="sidebar">
//         <button
//           className="new"
//           type="button"
//           onClick={(e) => {
//             e.preventDefault();
//             startNewChat();
//           }}
//         >
//           <Plus size={16} /> New Chat
//         </button>

//         <h3>Threads</h3>

//         {threads.map((t) => (
//           <button
//             key={t.id}
//             className="thread"
//             onClick={() => loadThread(t.id)}
//           >
//             {t.title}
//           </button>
//         ))}
//       </aside>

//       <section className="app">
//         <section className="hero">
//           <h1>Production RAG Assistant</h1>
//           <p>
//             Persistent RAG with SQLite threads, Chroma vector storage, document
//             management, source citations, and evaluation dashboard.
//           </p>
//         </section>

//         <section className="dashboard">
//           <div className="metric">
//             <BarChart3 size={18} />
//             <span>Total Queries</span>
//             <b>{summary?.total_queries ?? 0}</b>
//           </div>

//           <div className="metric">
//             <FileText size={18} />
//             <span>Documents</span>
//             <b>{summary?.total_documents ?? 0}</b>
//           </div>

//           <div className="metric">
//             <span>Chunks</span>
//             <b>{summary?.total_chunks ?? 0}</b>
//           </div>

//           <div className="metric">
//             <span>No Answer</span>
//             <b>{summary?.no_answer_count ?? 0}</b>
//           </div>

//           <div className="metric">
//             <span>Avg Latency</span>
//             <b>{summary?.average_latency_ms ?? 0} ms</b>
//           </div>
//         </section>

//         <section className="card upload-card">
//           <h2>Upload Documents</h2>

//           <input
//             type="file"
//             accept=".pdf,.txt"
//             multiple
//             onChange={(e) => setFiles(Array.from(e.target.files || []))}
//           />

//           <button onClick={handleUpload} disabled={!files.length || loading}>
//             <Upload size={16} /> Upload & Index
//           </button>

//           {files.length > 0 && (
//             <p className="status">
//               Selected: {files.map((file) => file.name).join(", ")}
//             </p>
//           )}

//           {status && <p className="status">{status}</p>}
//         </section>

//         <section className="card documents-card">
//           <h2>Documents</h2>

//           {documents.length === 0 && <p>No documents uploaded yet.</p>}

//           {documents.map((doc) => (
//             <div key={doc.document_id} className="document-row">
//               <div>
//                 <b>{doc.filename}</b>
//                 <p>
//                   Chunks: {doc.chunks_added} | ID:{" "}
//                   {doc.document_id.slice(0, 8)}
//                 </p>
//               </div>

//               <button
//                 className="delete"
//                 onClick={() => handleDeleteDocument(doc.document_id)}
//               >
//                 <Trash2 size={16} /> Delete
//               </button>
//             </div>
//           ))}
//         </section>

//         <section className="card chat-card">
//           <div className="messages">
//             {messages.map((m, i) => (
//               <div key={i} className={`msg ${m.role}`}>
//                 <b>{m.role}</b>
//                 <p>{m.text}</p>

//                 {m.sources?.length > 0 && (
//                   <details>
//                     <summary>Sources</summary>

//                     {m.sources.map((s, j) => (
//                       <div key={j} className="source-box">
//                         <b>{s.filename}</b>
//                         {s.page !== null && s.page !== undefined && (
//                           <span> | Page {s.page + 1}</span>
//                         )}
//                         <p>{s.preview}</p>
//                       </div>
//                     ))}
//                   </details>
//                 )}
//               </div>
//             ))}
//           </div>

//           <form onSubmit={handleAsk}>
//             <input
//               value={question}
//               onChange={(e) => setQuestion(e.target.value)}
//               placeholder="Ask your documents..."
//             />

//             <button disabled={loading}>
//               <Send size={16} /> Send
//             </button>
//           </form>
//         </section>
//       </section>
//     </main>
//   );
// }

// createRoot(document.getElementById("root")).render(<App />);

import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { Upload, Send, Plus, Trash2, FileText, BarChart3 } from "lucide-react";

import {
  uploadMultipleDocuments,
  streamQuestion,
  listThreads,
  getThreadMessages,
  newThreadId,
  listDocuments,
  deleteDocument,
  getEvaluationSummary,
} from "./lib/api";

import "./style.css";

function App() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [threadId, setThreadId] = useState(
    localStorage.getItem("thread_id") || newThreadId()
  );

  const [threads, setThreads] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    localStorage.setItem("thread_id", threadId);
    refreshThreads();
    refreshDocuments();
    refreshSummary();
  }, [threadId]);

  async function refreshThreads() {
    try {
      setThreads(await listThreads());
    } catch {}
  }

  async function refreshDocuments() {
    try {
      setDocuments(await listDocuments());
    } catch {}
  }

  async function refreshSummary() {
    try {
      setSummary(await getEvaluationSummary());
    } catch {}
  }

  async function loadThread(id) {
    setThreadId(id);

    const rows = await getThreadMessages(id);

    setMessages(
      rows.map((r) => ({
        role: r.role,
        text: r.content,
        sources: r.sources || [],
      }))
    );
  }

  function startNewChat() {
    const id = newThreadId();

    localStorage.setItem("thread_id", id);

    setThreadId(id);
    setMessages([]);
    setQuestion("");
    setStatus("");
  }

  async function handleUpload() {
    if (!files.length) return;

    setLoading(true);
    setStatus("Uploading and indexing documents...");

    try {
      const results = await uploadMultipleDocuments(files);

      const totalChunks = results.reduce(
        (sum, item) => sum + item.chunks_added,
        0
      );

      setStatus(
        `${results.length} document(s) indexed successfully. Total chunks: ${totalChunks}`
      );

      setFiles([]);
      await refreshDocuments();
      await refreshSummary();
    } catch (e) {
      setStatus(`Upload failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteDocument(documentId) {
    const confirmDelete = confirm("Delete this document and its vector chunks?");

    if (!confirmDelete) return;

    try {
      await deleteDocument(documentId);
      await refreshDocuments();
      await refreshSummary();
      setStatus("Document deleted successfully.");
    } catch (e) {
      setStatus(`Delete failed: ${e.message}`);
    }
  }

  async function handleAsk(e) {
    e.preventDefault();

    if (!question.trim()) return;

    const userQuestion = question;
    setQuestion("");

    setMessages((m) => [
      ...m,
      { role: "user", text: userQuestion, sources: [] },
      { role: "assistant", text: "", sources: [] },
    ]);

    setLoading(true);

    try {
      await streamQuestion(
        userQuestion,
        threadId,
        (token) => {
          setMessages((m) => {
            const copy = [...m];
            const last = copy[copy.length - 1];

            copy[copy.length - 1] = {
              ...last,
              text: last.text + token,
            };

            return copy;
          });
        },
        (sources) => {
          setMessages((m) => {
            const copy = [...m];
            const last = copy[copy.length - 1];

            copy[copy.length - 1] = {
              ...last,
              sources,
            };

            return copy;
          });
        }
      );

      await refreshThreads();
      await refreshSummary();
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: `Error: ${e.message}`,
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="layout">
      <aside className="sidebar">
        <button className="new" type="button" onClick={startNewChat}>
          <Plus size={16} /> New Chat
        </button>

        <h3>Threads</h3>

        {threads.map((t) => (
          <button
            key={t.id}
            className={t.id === threadId ? "thread active-thread" : "thread"}
            onClick={() => loadThread(t.id)}
          >
            {t.title}
          </button>
        ))}
      </aside>

      <section className="app">
        <section className="hero">
          <h1>Production RAG Assistant</h1>
          <p>
            Persistent RAG with PostgreSQL, pgvector, document management,
            source citations, streaming answers, and evaluation dashboard.
          </p>
        </section>

        <section className="dashboard">
          <div className="metric">
            <BarChart3 size={18} />
            <span>Total Queries</span>
            <b>{summary?.total_queries ?? 0}</b>
          </div>

          <div className="metric">
            <FileText size={18} />
            <span>Documents</span>
            <b>{summary?.total_documents ?? 0}</b>
          </div>

          <div className="metric">
            <span>Chunks</span>
            <b>{summary?.total_chunks ?? 0}</b>
          </div>

          <div className="metric">
            <span>No Answer</span>
            <b>{summary?.no_answer_count ?? 0}</b>
          </div>

          <div className="metric">
            <span>Avg Latency</span>
            <b>{summary?.average_latency_ms ?? 0} ms</b>
          </div>
        </section>

        <section className="card upload-card">
          <h2>Upload Documents</h2>

          <input
            type="file"
            accept=".pdf,.txt"
            multiple
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
          />

          <button onClick={handleUpload} disabled={!files.length || loading}>
            <Upload size={16} /> Upload & Index
          </button>

          {files.length > 0 && (
            <p className="status">
              Selected: {files.map((file) => file.name).join(", ")}
            </p>
          )}

          {status && <p className="status">{status}</p>}
        </section>

        <section className="card documents-card">
          <h2>Documents</h2>

          {documents.length === 0 && <p>No documents uploaded yet.</p>}

          {documents.map((doc) => (
            <div key={doc.document_id} className="document-row">
              <div>
                <b>{doc.filename}</b>
                <p>
                  Chunks: {doc.chunks_added} | ID:{" "}
                  {doc.document_id.slice(0, 8)}
                </p>
              </div>

              <button
                className="delete"
                type="button"
                onClick={() => handleDeleteDocument(doc.document_id)}
              >
                <Trash2 size={16} /> Delete
              </button>
            </div>
          ))}
        </section>

        <section className="card chat-card">
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <b>{m.role}</b>
                <p>{m.text}</p>

                {m.sources?.length > 0 && (
                  <details>
                    <summary>Sources</summary>

                    {m.sources.map((s, j) => (
                      <div key={j} className="source-box">
                        <b>{s.filename}</b>

                        {s.page !== null && s.page !== undefined && (
                          <span> | Page {s.page + 1}</span>
                        )}

                        <p>{s.preview}</p>
                      </div>
                    ))}
                  </details>
                )}
              </div>
            ))}
          </div>

          <form onSubmit={handleAsk}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask your documents..."
            />

            <button disabled={loading}>
              <Send size={16} /> Send
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);