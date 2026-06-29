import { useState } from "react";
import { newThreadId } from "../lib/api";

function getThreadStorageKey(email) {
  return `thread_id_${email}`;
}

export function useThreads(user) {
  const [threadId, setThreadId] = useState(newThreadId());

  function restoreThread(userEmail) {
    const saved =
      localStorage.getItem(getThreadStorageKey(userEmail)) ||
      newThreadId();

    localStorage.setItem(
      getThreadStorageKey(userEmail),
      saved
    );

    setThreadId(saved);

    return saved;
  }

  function startNewChat() {
    if (!user) return;

    const id = newThreadId();

    console.log("NEW THREAD:", id);

    localStorage.setItem(
        getThreadStorageKey(user.email),
        id
    );

    setThreadId(id);

    return id;
    }

  return {
    threadId,
    setThreadId,
    restoreThread,
    startNewChat,
  };
}