/**
 * Hayah Landing — Nav
 * Theme-switchable via prop.
 */
function LandingNav({ theme, setTheme }) {
  const themes = ["classic", "coral", "editorial", "bento", "midnight"];
  const isDark = theme === "midnight";
  const isEditorial = theme === "editorial";

  const navStyle = {
    position: "sticky", top: 0, zIndex: 50,
    padding: "16px 32px",
    background: isDark
      ? "rgba(15, 56, 54, 0.85)"
      : isEditorial
        ? "#ffffff"
        : "rgba(250, 247, 245, 0.85)",
    backdropFilter: isEditorial ? "none" : "blur(20px)",
    borderBottom: isEditorial
      ? "1px solid #e8f4f1"
      : "1px solid var(--border-1)",
    display: "flex", alignItems: "center", gap: 24,
  };

  return (
    <nav style={navStyle}>
      <a href="#" style={{ display: "flex", alignItems: "center", textDecoration: "none" }}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 344 96" width="207" height="58" role="img" aria-label="Hayah-AI — business automation">
          <path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke={isDark ? "#faf7f5" : "#0a3d3a"} strokeWidth="8" strokeLinecap="round"/>
          <circle cx="52" cy="12" r="6" fill="#ff6b47"/>
          <text x="68" y="48" fontFamily="DM Serif Display, Georgia, serif" fontSize="44" fontWeight="400" fill={isDark ? "#faf7f5" : "#0a3d3a"} letterSpacing="-1.2">
            hayah<tspan fill={isDark ? "#A1E4DB" : "#7a9b96"}>-</tspan><tspan fill="#ff6b47" fontStyle="italic">ai</tspan>
          </text>
          <text x="0" y="84" fontFamily="Inter, Helvetica Neue, sans-serif" fontSize="15" fontWeight="300" fill={isDark ? "#faf7f5" : "#0a3d3a"} textLength="230" lengthAdjust="spacing">
            business automation
          </text>
        </svg>
      </a>
      <div style={{ display: "flex", gap: 20, marginLeft: 24 }}>
        {["Product", "Customers", "Pricing", "Docs"].map(l => (
          <a key={l} href="#" style={{
            color: isDark ? "#A1E4DB" : "var(--fg-1)",
            fontSize: 14, fontWeight: 500,
          }}>{l}</a>
        ))}
      </div>
      <div style={{ marginLeft: "auto", display: "flex", gap: 10, alignItems: "center" }}>
        <select value={theme} onChange={e => setTheme(e.target.value)}
          style={{
            background: isDark ? "rgba(28,87,83,0.4)" : "transparent",
            color: isDark ? "#A1E4DB" : "var(--fg-1)",
            border: `1px solid ${isDark ? "rgba(161,228,219,0.3)" : "var(--border-2)"}`,
            borderRadius: isEditorial ? 0 : 10,
            padding: "8px 12px", fontFamily: "inherit", fontSize: 13, fontWeight: 500,
            cursor: "pointer", textTransform: "capitalize",
          }}>
          {themes.map(t => <option key={t} value={t}>Theme: {t}</option>)}
        </select>
        <button className="btn-primary">Get started</button>
      </div>
    </nav>
  );
}
window.LandingNav = LandingNav;
