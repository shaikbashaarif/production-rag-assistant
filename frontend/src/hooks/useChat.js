import { useState } from "react";

import {
  streamQuestion,
  listThreads,
  getThreadMessages,
} from "../lib/api";

export function useChat(threadId) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [threads, setThreads] = useState([]);

  async function refreshThreads() {
    try {
      const data = await listThreads();
      setThreads(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function loadThread(id) {
    try {
      const rows = await getThreadMessages(id);

      setMessages(
        rows.map((row) => ({
          role: row.role,
          text: row.content,
          sources: row.sources || [],
        }))
      );
    } catch (err) {
      console.error(err);
    }
  }

  async function ask(questionText, refreshSummary, setLoading) {
    if (!questionText.trim()) return;

    setQuestion("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: questionText,
        sources: [],
      },
      {
        role: "assistant",
        text: "",
        sources: [],
      },
    ]);

    setLoading(true);

    try {
      await streamQuestion(
        questionText,
        threadId,

        (token) => {
          setMessages((prev) => {
            const copy = [...prev];

            copy[copy.length - 1] = {
              ...copy[copy.length - 1],
              text: copy[copy.length - 1].text + token,
            };

            return copy;
          });
        },

        (sources) => {
          setMessages((prev) => {
            const copy = [...prev];

            copy[copy.length - 1] = {
              ...copy[copy.length - 1],
              sources,
            };

            return copy;
          });
        }
      );

      await refreshThreads();
      await refreshSummary();

    } catch (err) {

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `Error: ${err.message}`,
          sources: [],
        },
      ]);

    } finally {
      setLoading(false);
    }
  }

  return {
    messages,
    setMessages,

    question,
    setQuestion,

    threads,

    refreshThreads,
    loadThread,

    ask,
  };
}