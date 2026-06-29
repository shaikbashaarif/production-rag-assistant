import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { useThreads } from "./hooks/useThreads";
import "./style.css";

import AuthPage from "./components/AuthPage";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import UploadPanel from "./components/UploadPanel";
import DocumentPanel from "./components/DocumentPanel";
import ChatWindow from "./components/ChatWindow";

import { newThreadId, getCurrentUser, getToken } from "./lib/api";

import { useAuth } from "./hooks/useAuth";
import { useDocuments } from "./hooks/useDocuments";
import { useChat } from "./hooks/useChat";

import { useAppInitialization } from "./hooks/useAppInitialization";


function App() {
  /******************************
   * Authentication
   ******************************/
  const [authMode, setAuthMode] = useState("login");
  const [email, setEmail] = useState("user1@test.com");
  const [password, setPassword] = useState("test1234");

  const {
    user,
    setUser,
    authStatus,
    login,
    register,
    logout,
  } = useAuth();

  /******************************
   * UI State
   ******************************/
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  /******************************
   * Thread State
   ******************************/
 

  /******************************
   * Documents Hook
   ******************************/
  const {
    documents,
    summary,
    status,
    setStatus,
    refreshDocuments,
    refreshSummary,
    upload,
    remove,
  } = useDocuments();

  /******************************
   * Threads Hook
   ******************************/

  const {
  threadId,
  setThreadId,
  restoreThread,
  startNewChat,
} = useThreads(user);

  /******************************
   * Chat Hook
   ******************************/
  const {
    messages,
    setMessages,
    question,
    setQuestion,
    threads,
    refreshThreads,
    loadThread,
    ask,
  } = useChat(threadId);

  /******************************
   * Restore login on refresh
   ******************************/
  useAppInitialization({
    setUser,
    restoreThread,
  });

  /******************************
   * Refresh data
   ******************************/
  useEffect(() => {
    if (!user) return;

    refreshThreads();
    refreshDocuments();
    refreshSummary();
  }, [user, threadId]);

  /******************************
   * Login/Register
   ******************************/


  async function handleAuth(e) {
  e.preventDefault();

  console.log("LOGIN BUTTON CLICKED");

  try {
    let currentUser;

    if (authMode === "register") {
      console.log("REGISTER");
      currentUser = await register(email, password);
    } else {
      console.log("LOGIN");
      currentUser = await login(email, password);
    }

    console.log(currentUser);

    const savedThread =
      localStorage.getItem(
        getThreadStorageKey(currentUser.email)
      ) || newThreadId();

    localStorage.setItem(
      getThreadStorageKey(currentUser.email),
      savedThread
    );

    setThreadId(savedThread);
    setMessages([]);

  } catch (err) {
    console.error(err);
  }
}

  /******************************
   * Logout
   ******************************/
  function handleLogout() {
    logout();

    setThreadId(newThreadId());
    setMessages([]);
    setQuestion("");
    setStatus("");
  }

  /******************************
   * New Chat
   ******************************/
  

  /******************************
   * Login Screen
   ******************************/
  if (!user) {
    return (
      <AuthPage
        authMode={authMode}
        setAuthMode={setAuthMode}
        email={email}
        setEmail={setEmail}
        password={password}
        setPassword={setPassword}
        handleAuth={handleAuth}
        authStatus={authStatus}
      />
    );
  }

  /******************************
   * Main UI
   ******************************/
  return (
    <main className="layout">
      <Sidebar
        user={user}
        threadId={threadId}
        threads={threads}
        startNewChat={() => {
          const id = startNewChat();

          console.log("MAIN RECEIVED:", id);

          setMessages([]);
          setQuestion("");
          setStatus("");
        }}
        loadThread={loadThread}
        handleLogout={handleLogout}
      />

      <section className="app">

        <section className="hero">
          <h1>Production RAG Assistant</h1>

          <p>
            Multi-user RAG with PostgreSQL,
            pgvector,
            JWT Authentication,
            private documents,
            streaming,
            and evaluation dashboard.
          </p>
        </section>

        <Dashboard summary={summary} />

        <UploadPanel
          files={files}
          setFiles={setFiles}
          loading={loading}
          status={status}
          handleUpload={async () => {
            await upload(files, setLoading);
            setFiles([]);
          }}
        />

        <DocumentPanel
          documents={documents}
          handleDeleteDocument={remove}
        />

        <ChatWindow
          messages={messages}
          question={question}
          setQuestion={setQuestion}
          loading={loading}
          handleAsk={async (e) => {
            e.preventDefault();

            await ask(
              question,
              refreshSummary,
              setLoading
            );
          }}
        />

      </section>
    </main>
  );
}

createRoot(
  document.getElementById("root")
).render(<App />);