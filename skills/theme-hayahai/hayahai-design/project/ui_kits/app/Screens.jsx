/** Three workspace screens: Home (project list), Chat, Settings */

function HomeScreen({ onOpenProject }) {
  const projects = [
    { id: 1, name: "Acme — Marketing site", updated: "2h ago", members: 4, color: "#ff6b47" },
    { id: 2, name: "Internal · Onboarding", updated: "yesterday", members: 2, color: "#25A497" },
    { id: 3, name: "Brand refresh 2026", updated: "3 days ago", members: 7, color: "#A1E4DB" },
    { id: 4, name: "Mobile app prototype", updated: "1 week ago", members: 3, color: "#1E6E66" },
  ];
  return (
    <div data-screen-label="01 Home">
      <div style={{ marginBottom: 36 }}>
        <span className="eyebrow">Today · April 29</span>
        <h1 style={{ marginTop: 8, fontSize: 36 }}>Welcome back, Maya.</h1>
        <p style={{ marginTop: 6, color: "var(--fg-2)" }}>4 projects · 2 awaiting review</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16, marginBottom: 32 }}>
        <StatCard label="Active projects" value="4" delta="+1 this week"/>
        <StatCard label="Open conversations" value="12" delta="3 unread" deltaColor="#ff6b47"/>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 16 }}>
        <h2 style={{ fontSize: 22 }}>Projects</h2>
        <a href="#" style={{ fontSize: 13, fontWeight: 500 }}>View all →</a>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 14 }}>
        {projects.map(p => (
          <button key={p.id} onClick={() => onOpenProject?.(p)} style={{
            textAlign: "left", cursor: "pointer", padding: 22,
            background: "#fff", border: "1px solid var(--border-1)", borderRadius: 16,
            boxShadow: "0 2px 8px rgba(10,61,58,0.04)",
            transition: "box-shadow 200ms",
            fontFamily: "inherit",
          }}
          onMouseEnter={e => e.currentTarget.style.boxShadow = "0 4px 16px rgba(10,61,58,0.08)"}
          onMouseLeave={e => e.currentTarget.style.boxShadow = "0 2px 8px rgba(10,61,58,0.04)"}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: p.color }}/>
              <Icon name="more-horizontal" size={16} color="var(--fg-3)"/>
            </div>
            <h3 style={{ marginTop: 18, fontSize: 17, fontWeight: 600 }}>{p.name}</h3>
            <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--fg-3)" }}>
              <span>Updated {p.updated}</span>
              <span>{p.members} members</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function StatCard({ label, value, delta, deltaColor = "#25A497" }) {
  return (
    <div style={{
      padding: 22, background: "var(--teal-200)", borderRadius: 16,
      border: "1px solid #A1E4DB",
    }}>
      <span className="eyebrow" style={{ color: "#1E6E66" }}>{label}</span>
      <div style={{ marginTop: 8, fontFamily: "var(--font-display)", fontSize: 40, lineHeight: 1, color: "#0a3d3a", letterSpacing: "-0.02em" }}>{value}</div>
      <div style={{ marginTop: 8, fontSize: 13, color: deltaColor, fontWeight: 600 }}>{delta}</div>
    </div>
  );
}

function ChatScreen() {
  const [messages, setMessages] = React.useState([
    { who: "ai", text: "Hi Maya. What are we building today?" },
    { who: "me", text: "Mock a settings screen for the app kit." },
    { who: "ai", text: "On it. Should the form use the Pearl card style or sit on the page surface?" },
  ]);
  const [draft, setDraft] = React.useState("");
  const send = () => {
    if (!draft.trim()) return;
    setMessages([...messages, { who: "me", text: draft }]);
    setDraft("");
    setTimeout(() => {
      setMessages(m => [...m, { who: "ai", text: "Got it — drafting now." }]);
    }, 600);
  };
  return (
    <div data-screen-label="02 Chat" style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 130px)" }}>
      <div style={{ marginBottom: 16 }}>
        <span className="eyebrow">Conversation</span>
        <h2 style={{ fontSize: 22, marginTop: 4 }}>Acme · Marketing site</h2>
      </div>
      <div style={{ flex: 1, overflow: "auto", display: "flex", flexDirection: "column", gap: 12, padding: "8px 0" }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            alignSelf: m.who === "me" ? "flex-end" : "flex-start",
            maxWidth: "70%",
            padding: "12px 16px",
            background: m.who === "me" ? "#0a3d3a" : "#fff",
            color: m.who === "me" ? "#faf7f5" : "var(--fg-1)",
            border: m.who === "me" ? "none" : "1px solid var(--border-1)",
            borderRadius: 16, borderBottomRightRadius: m.who === "me" ? 4 : 16,
            borderBottomLeftRadius: m.who === "ai" ? 4 : 16,
            fontSize: 14, lineHeight: 1.55,
          }}>{m.text}</div>
        ))}
      </div>
      <div style={{
        marginTop: 12, display: "flex", gap: 8, alignItems: "center",
        background: "#fff", border: "1.5px solid var(--border-2)", borderRadius: 14, padding: "8px 8px 8px 16px",
      }}>
        <Icon name="sparkles" size={16} color="#25A497"/>
        <input value={draft} onChange={e => setDraft(e.target.value)} onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Ask anything…" style={{
            flex: 1, border: "none", outline: "none", background: "transparent",
            fontFamily: "inherit", fontSize: 14, color: "var(--fg-1)",
          }}/>
        <button onClick={send} style={{
          width: 36, height: 36, borderRadius: 10, border: "none",
          background: "var(--coral-500)", color: "#fff", cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}><Icon name="send" size={14} color="#fff"/></button>
      </div>
    </div>
  );
}

function SettingsScreen() {
  return (
    <div data-screen-label="03 Settings" style={{ maxWidth: 720 }}>
      <div style={{ marginBottom: 28 }}>
        <span className="eyebrow">Workspace</span>
        <h2 style={{ fontSize: 28, marginTop: 4 }}>Settings</h2>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        <Field label="Workspace name" value="Hayah Studio"/>
        <Field label="Email" value="maya@hayah.design" badge="Verified"/>
        <Field label="API key" mono value="hyh_4f8c…2a91" help="Rotate every 90 days." readOnly/>
        <div>
          <span style={{ display:"block", fontSize: 12, fontWeight:600, marginBottom: 6 }}>Theme</span>
          <div style={{ display: "flex", gap: 8 }}>
            {["classic","coral","editorial","bento","midnight"].map(t => (
              <button key={t} style={{
                padding: "8px 14px", borderRadius: 10, fontSize: 13, fontWeight: 500,
                background: t === "classic" ? "#0a3d3a" : "#fff",
                color: t === "classic" ? "#faf7f5" : "var(--fg-1)",
                border: t === "classic" ? "none" : "1px solid var(--border-2)",
                cursor: "pointer", fontFamily: "inherit", textTransform: "capitalize",
              }}>{t}</button>
            ))}
          </div>
        </div>
        <div style={{ paddingTop: 24, borderTop: "1px solid var(--border-1)", display: "flex", gap: 10 }}>
          <button className="btn-primary">Save changes</button>
          <button className="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, help, mono, readOnly, badge }) {
  return (
    <div>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom: 6 }}>
        <label style={{ fontSize: 12, fontWeight: 600 }}>{label}</label>
        {badge && <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 9999, background: "rgba(37,164,151,0.15)", color: "#25A497", fontWeight: 600 }}>{badge}</span>}
      </div>
      <input value={value} readOnly={readOnly} style={{
        width: "100%", fontFamily: mono ? "var(--font-mono)" : "inherit",
        fontSize: mono ? 13 : 15, color: "var(--fg-1)", background: "#fff",
        border: "1.5px solid var(--border-2)", borderRadius: 10, padding: "12px 14px", outline: "none",
      }}/>
      {help && <div style={{ fontSize: 12, color: "var(--fg-3)", marginTop: 6 }}>{help}</div>}
    </div>
  );
}

window.HomeScreen = HomeScreen;
window.ChatScreen = ChatScreen;
window.SettingsScreen = SettingsScreen;
