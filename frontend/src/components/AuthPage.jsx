import React from "react";

export default function AuthPage({
  authMode,
  setAuthMode,
  email,
  setEmail,
  password,
  setPassword,
  handleAuth,
  authStatus,
}) {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <h1>Production RAG Assistant</h1>

        <p>
          Login to access your private documents and chats.
        </p>

        <form onSubmit={handleAuth}>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
          />

          <input
            value={password}
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">
            {authMode === "login"
              ? "Login"
              : "Register & Login"}
          </button>
        </form>

        <button
          className="link-button"
          onClick={() =>
            setAuthMode(
              authMode === "login"
                ? "register"
                : "login"
            )
          }
        >
          {authMode === "login"
            ? "Create new account"
            : "Already have account? Login"}
        </button>

        {authStatus && (
          <p className="status error">
            {authStatus}
          </p>
        )}
      </section>
    </main>
  );
}