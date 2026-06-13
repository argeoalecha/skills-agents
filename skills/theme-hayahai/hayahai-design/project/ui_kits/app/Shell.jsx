/**
 * Hayah App — Sidebar + Topbar + Workspace shell
 * A simple workspace/dashboard mock using the brand language.
 */
function AppShell({ children, active, onNav, theme }) {
  const isDark = theme === "midnight";
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "240px 1fr", height: "100vh",
      background: isDark ? "#0F3836" : "var(--cream)",
    }}>
      <Sidebar active={active} onNav={onNav} isDark={isDark}/>
      <div style={{ display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <Topbar isDark={isDark}/>
        <main style={{ flex: 1, overflow: "auto", padding: 32 }}>{children}</main>
      </div>
    </div>
  );
}

function Sidebar({ active, onNav, isDark }) {
  const items = [
    { id: "home", label: "Home", icon: "home" },
    { id: "projects", label: "Projects", icon: "folder" },
    { id: "chat", label: "Conversations", icon: "message-square" },
    { id: "team", label: "Team", icon: "users" },
    { id: "settings", label: "Settings", icon: "settings" },
  ];
  return (
    <aside style={{
      background: isDark ? "rgba(28,87,83,0.4)" : "#fff",
      borderRight: `1px solid ${isDark ? "rgba(161,228,219,0.15)" : "var(--border-1)"}`,
      padding: 20, display: "flex", flexDirection: "column", gap: 4,
    }}>
      <div style={{ padding: "8px 10px 20px" }}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 344 96" width="207" height="58" role="img" aria-label="Hayah-AI — business automation">
          <path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke={isDark ? "#faf7f5" : "#0a3d3a"} strokeWidth="8" strokeLinecap="round"/>
          <circle cx="52" cy="12" r="6" fill="#ff6b47"/>
          <text x="68" y="48" fontFamily="DM Serif Display, Georgia, serif" fontSize="44" fontWeight="400" fill={isDark ? "#faf7f5" : "#0a3d3a"} letterSpacing="-1.2">
            hayah<tspan fill={isDark ? "#A1E4DB" : "#7a9b96"}>-</tspan><tspan fill="#ff6b47" fontStyle="italic">ai</tspan>
          </text>
          <text x="0" y="84" fontFamily="Geist, Helvetica Neue, sans-serif" fontSize="15" fontWeight="300" fill={isDark ? "#faf7f5" : "#0a3d3a"} textLength="230" lengthAdjust="spacing">
            business automation
          </text>
        </svg>
      </div>
      {items.map(it => {
        const isActive = active === it.id;
        return (
          <button key={it.id} onClick={() => onNav(it.id)} style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "9px 10px", borderRadius: 8, border: "none",
            background: isActive
              ? (isDark ? "rgba(37,164,151,0.2)" : "var(--teal-200)")
              : "transparent",
            color: isActive
              ? (isDark ? "#A1E4DB" : "var(--teal-900)")
              : (isDark ? "rgba(161,228,219,0.7)" : "var(--fg-2)"),
            fontSize: 14, fontWeight: isActive ? 600 : 500, cursor: "pointer",
            fontFamily: "inherit", textAlign: "left",
          }}>
            <Icon name={it.icon} size={16}/>
            <span>{it.label}</span>
          </button>
        );
      })}
      <div style={{ marginTop: "auto", padding: "12px 10px", display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 30, height: 30, borderRadius: 9999, background: "linear-gradient(135deg, #25A497, #0a3d3a)" }}/>
        <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: isDark ? "#faf7f5" : "var(--fg-1)" }}>Maya R.</span>
          <span style={{ fontSize: 11, color: "var(--fg-3)" }}>Studio · Pro</span>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ isDark }) {
  return (
    <header style={{
      display: "flex", alignItems: "center", gap: 14,
      padding: "14px 32px",
      background: isDark ? "rgba(15,56,54,0.85)" : "rgba(250,247,245,0.85)",
      borderBottom: `1px solid ${isDark ? "rgba(161,228,219,0.1)" : "var(--border-1)"}`,
      backdropFilter: "blur(12px)",
    }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 8, flex: 1, maxWidth: 420,
        background: isDark ? "rgba(28,87,83,0.5)" : "#fff",
        border: `1px solid ${isDark ? "rgba(161,228,219,0.2)" : "var(--border-1)"}`,
        borderRadius: 10, padding: "8px 12px",
      }}>
        <Icon name="search" size={15} color={isDark ? "#7a9b96" : "var(--fg-3)"}/>
        <input placeholder="Search projects, chats…" style={{
          flex: 1, border: "none", outline: "none", background: "transparent",
          color: isDark ? "#faf7f5" : "var(--fg-1)", fontFamily: "inherit", fontSize: 13,
        }}/>
        <span style={{ fontSize: 11, color: "var(--fg-3)", padding: "1px 6px", border: "1px solid var(--border-1)", borderRadius: 4 }}>⌘K</span>
      </div>
      <button className="btn-primary" style={{ padding: "10px 18px", fontSize: 14 }}>+ New project</button>
    </header>
  );
}

window.AppShell = AppShell;
