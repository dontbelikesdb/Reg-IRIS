import { useState } from "react";
import { Sparkles, ArrowRight } from "lucide-react";
import { askAssistant, suggestedPrompts } from "../services/api.js";

export default function AssistantPanel() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  const send = async (question) => {
    const q = (question ?? text).trim();
    if (!q || busy) return;
    setText("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", text: q }]);
    const answer = await askAssistant(q);
    setMessages((m) => [...m, { role: "bot", text: answer }]);
    setBusy(false);
  };

  return (
    <section className="card assistant">
      <div className="card-title"><Sparkles size={18} className="accent" /><h2>Ask Reg IRIS (AI Assistant)</h2></div>

      <div className="chat">
        {messages.length === 0 ? (
          <>
            <p className="muted">How can I help you today? Try asking:</p>
            <div className="chip-col">
              {suggestedPrompts.map((p) => (
                <button key={p} className="chip" onClick={() => send(p)}>{p}</button>
              ))}
            </div>
          </>
        ) : (
          messages.map((m, i) => <div key={i} className={`bubble ${m.role}`}>{m.text}</div>)
        )}
        {busy && <div className="bubble bot">Thinking…</div>}
      </div>

      <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send(); }}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type your question..." />
        <button className="btn icon-only" aria-label="Send"><ArrowRight size={18} /></button>
      </form>
    </section>
  );
}
