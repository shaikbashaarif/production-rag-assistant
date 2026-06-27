import { Send } from "lucide-react";

export default function ChatWindow({
  messages,
  question,
  setQuestion,
  handleAsk,
  loading,
}) {
  return (
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

                    {s.page !== null &&
                      s.page !== undefined && (
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
          <Send size={16} />
          Send
        </button>

      </form>

    </section>
  );
}