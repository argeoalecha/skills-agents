/** Metrics + CTA + Footer */
function Metrics({ theme }) {
  const items = [["12k+", "teams"], ["99.9%", "uptime"], ["5", "themes"], ["2.0", "release"]];
  const isDark = theme === "midnight";
  return (
    <section style={{ background: isDark ? "#0F3836" : "var(--cream)", padding: "80px 32px", borderTop: "1px solid var(--border-1)" }}>
      <div style={{ maxWidth: 1240, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 24 }}>
        {items.map(([n, l]) => (
          <div key={l}>
            <div style={{ fontFamily: "var(--font-display)", fontSize: 56, lineHeight: 1, color: isDark ? "#faf7f5" : "#0a3d3a", letterSpacing: "-0.03em" }}>{n}</div>
            <div className="t-caption" style={{ marginTop: 8, color: isDark ? "#A1E4DB" : "var(--fg-3)" }}>{l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function CTA({ theme }) {
  const isCoral = theme === "coral";
  const bg = isCoral ? "#ff6b47" : "linear-gradient(135deg, #1E6E66 0%, #0a3d3a 100%)";
  return (
    <section style={{ background: bg, padding: "108px 32px", textAlign: "center" }}>
      <div style={{ maxWidth: 720, margin: "0 auto" }}>
        <h2 style={{ color: "#faf7f5" }}>Start designing in minutes.</h2>
        <p style={{ color: isCoral ? "rgba(255,255,255,0.9)" : "#A1E4DB", marginTop: 16, fontSize: 18 }}>
          Pick a theme, drop in the CSS, and ship.
        </p>
        <div style={{ marginTop: 32, display: "flex", gap: 12, justifyContent: "center" }}>
          <button className="btn-primary" style={{ background: isCoral ? "#0a3d3a" : "#ff6b47", boxShadow: isCoral ? "0 4px 16px rgba(10,61,58,0.3)" : undefined }}>Get started →</button>
          <button className="btn-secondary" style={{ borderColor: "rgba(255,255,255,0.4)", color: "#faf7f5" }}>Read the docs</button>
        </div>
      </div>
    </section>
  );
}

function Footer({ theme }) {
  return (
    <footer style={{ background: "#0F3836", color: "#e8f4f1", padding: "64px 32px 40px", borderTop: theme === "editorial" ? "3px solid #ff6b47" : "none" }}>
      <div style={{ maxWidth: 1240, margin: "0 auto", display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 32 }}>
        <div>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <svg viewBox="0 0 64 64" width="28" height="28"><path d="M 12 52 A 28 28 0 0 1 52 12" fill="none" stroke="#A1E4DB" strokeWidth="6" strokeLinecap="round"/><circle cx="52" cy="12" r="6" fill="#ff6b47"/></svg>
            <span style={{ fontFamily: "var(--font-display)", fontSize: 22, color: "#faf7f5" }}>Hayah</span>
          </div>
          <p style={{ marginTop: 14, fontSize: 14, color: "#A1E4DB", maxWidth: 320 }}>
            A design system for teams that ship.
          </p>
        </div>
        {[
          ["Product", ["Themes", "Components", "Tokens", "Changelog"]],
          ["Resources", ["Docs", "Figma", "GitHub", "Examples"]],
          ["Company", ["About", "Pricing", "Contact", "Status"]],
        ].map(([heading, links]) => (
          <div key={heading}>
            <div className="eyebrow" style={{ color: "#A1E4DB", marginBottom: 12 }}>{heading}</div>
            {links.map(l => <a key={l} href="#" style={{ display: "block", color: "#e8f4f1", fontSize: 14, padding: "4px 0" }}>{l}</a>)}
          </div>
        ))}
      </div>
      <div style={{ maxWidth: 1240, margin: "48px auto 0", paddingTop: 24, borderTop: "1px solid rgba(161,228,219,0.15)", display: "flex", justifyContent: "space-between", fontSize: 13, color: "#7a9b96" }}>
        <span>© 2026 Hayah Design</span>
        <span>v2.0 · April 2026</span>
      </div>
    </footer>
  );
}

window.Metrics = Metrics;
window.CTA = CTA;
window.Footer = Footer;
