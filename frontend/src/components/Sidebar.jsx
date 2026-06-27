import React from "react";
import { Plus, LogOut } from "lucide-react";

export default function Sidebar({
  user,
  threadId,
  threads,
  startNewChat,
  loadThread,
  handleLogout,
}) {
  return (
    <aside className="sidebar">
      <div className="user-box">
        <b>{user.email}</b>

        <button
          className="logout"
          onClick={handleLogout}
        >
          <LogOut size={14} />
          Logout
        </button>
      </div>

      <button
        className="new"
        type="button"
        onClick={startNewChat}
      >
        <Plus size={16} />
        New Chat
      </button>

      <h3>Threads</h3>

      {threads.map((t) => (
        <button
          key={t.id}
          className={
            t.id === threadId
              ? "thread active-thread"
              : "thread"
          }
          onClick={() => loadThread(t.id)}
        >
          {t.title}
        </button>
      ))}
    </aside>
  );
}