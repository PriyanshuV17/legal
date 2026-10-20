import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function ChatPage({ user }) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  useEffect(() => {
    if (!user) return;
    api.get(`/users/${user.id}/history`).then(({ data }) => setSessions(data.sessions));
  }, [user]);

  async function sendMessage(event) {
    event.preventDefault();
    if (!prompt.trim()) return;
    const userMessage = { role: "user", content: prompt };
    setMessages((prev) => [...prev, userMessage]);
    const currentPrompt = prompt;
    setPrompt("");
    const { data } = await api.post("/chat", {
      user_id: user.id,
      query: currentPrompt,
      session_id: activeSessionId,
      // Pass user context for personalization
      user_context: {
        location: user.city,
        state: user.state,
        language: user.language,
        profession: user.profession,
        age: user.age,
        name: user.name
      }
    });
    setActiveSessionId(data.session_id);
    setMessages((prev) => [...prev, { role: "assistant", content: buildAssistantMessage(data) }]);
    const history = await api.get(`/users/${user.id}/history`);
    setSessions(history.data.sessions);
  }

  async function loadSession(sessionId) {
    const { data } = await api.get(`/users/${user.id}/history/${sessionId}`);
    setMessages(data.messages);
    setActiveSessionId(sessionId);
  }

  return (
    <div className="page three-column">
      <aside className="glass-card sidebar-panel">
        <SectionHeader eyebrow="History" title="Previous Chats" />
        <button className="primary-button" onClick={() => { setMessages([]); setActiveSessionId(null); }}>New Chat</button>
        <div className="stack compact">
          {sessions.map((session) => (
            <button key={session.id} className="session-chip" onClick={() => loadSession(session.id)}>
              <span>{session.title}</span>
            </button>
          ))}
        </div>
      </aside>
      <section className="glass-card chat-panel">
        <SectionHeader
          eyebrow="Core Assistant"
          title="Chat Assistant"
          description="History-aware AI legal support with case suggestions and retrieval hooks."
        />
        <div className="chat-thread">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={`chat-bubble ${message.role}`}>
              <strong>{message.role === "user" ? "You" : "LegalBuddy"}</strong>
              <div>{message.content}</div>
            </div>
          ))}
        </div>
        <form className="chat-form" onSubmit={sendMessage}>
          <textarea rows="3" placeholder="Describe your issue or ask your legal question..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
          <button className="primary-button" type="submit">Send</button>
        </form>
      </section>
      <aside className="glass-card sidebar-panel">
        <SectionHeader eyebrow="Outcome" title="Chat Benefits" />
        <ul className="clean-list">
          <li>Semantic memory from vector storage</li>
          <li>Chats stored in SQL sessions</li>
          <li>Case references attached to responses</li>
          <li>Admin can audit overall usage</li>
        </ul>
      </aside>
    </div>
  );
}

function buildAssistantMessage(data) {
  let output = data.answer;
  if (data.case_type?.length) output += `\n\nCase Type: ${data.case_type[0]}`;
  if (data.recommended_lawyers?.length) output += `\nRecommended Lawyer: ${data.recommended_lawyers.join(", ")}`;
  if (data.case_insights?.length) {
    output += "\nRelevant Judgments:";
    data.case_insights.forEach((item) => {
      output += `\n- ${item.title} (${item.year})`;
    });
  }
  return output;
}
