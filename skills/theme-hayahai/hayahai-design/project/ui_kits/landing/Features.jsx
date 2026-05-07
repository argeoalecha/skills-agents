/** Bento-style feature grid + a metrics strip */
function Features({ theme }) {
  const isDark = theme === "midnight";
  const isEditorial = theme === "editorial";
  const isBento = theme === "bento";

  const items = [
    { eyebrow: "TOKENS", title: "One source of truth", body: "CSS variables for color, type, spacing, radii, shadows. Drop in and go." },
    { eyebrow: "THEMES", title: "Five personalities", body: "Classic, Coral, Editorial, Bento, Midnight — same palette, different voice." },
    { eyebrow: "COMPONENTS", title: "Production-grade", body: "Buttons, forms, cards, badges. All themed, all accessible." },
    { eyebrow: "TYPE", title: "Pair-programmed", body: "Display + body curated per theme. No bad pairings, ever." },
  ];

  return (
    <section style={{
      background: isDark ? "#0a3d3a" : isEditorial ? "#0F3836" : "#ffffff",
      color: (isDark || isEditorial) ? "#faf7f5" : "var(--fg-1)",
      padding: "108px 32px",
    }}>
      <div style={{ maxWidth: 1240, margin: "0 auto" }}>
        <div style={{ marginBottom: 56, maxWidth: 720 }}>
          <span className="eyebrow" style={{ color: isDark || isEditorial ? "#25A497" : "#1E6E66" }}>Why Hayah</span>
          <h2 style={{ marginTop: 12, color: "inherit" }}>A system, not a stylesheet.</h2>
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: isBento ? "2fr 1fr 1fr" : "repeat(2, 1fr)",
          gridAutoRows: isBento ? "minmax(180px, auto)" : "auto",
          gap: isEditorial ? 2 : 16,
        }}>
          {items.map((it, i) => (
            <div key={i} style={{
              gridColumn: isBento && i === 0 ? "span 1" : "auto",
              gridRow: isBento && i === 0 ? "span 2" : "auto",
              background: isDark
                ? "rgba(28,87,83,0.5)"
                : isEditorial
                  ? "#ffffff"
                  : isBento && i === 0
                    ? "linear-gradient(135deg, #1E6E66, #0a3d3a)"
                    : i === 1 && !isEditorial && !isDark ? "#e8f4f1" : "#ffffff",
              color: (isBento && i === 0) ? "#faf7f5" : isEditorial ? "#0F3836" : "inherit",
              border: isDark
                ? "1px solid rgba(161,228,219,0.15)"
                : isEditorial
                  ? "none"
                  : "1px solid rgba(161,228,219,0.4)",
              borderTop: isEditorial ? "3px solid #0F3836" : undefined,
              borderRadius: isEditorial ? 0 : 20,
              padding: 28,
              boxShadow: isDark || isEditorial ? "none" : "0 2px 16px rgba(10,61,58,0.06)",
            }}>
              <span className="eyebrow" style={{ color: (isBento && i === 0) ? "#A1E4DB" : isDark ? "#A1E4DB" : "#1E6E66" }}>{it.eyebrow}</span>
              <h3 style={{ marginTop: 10, marginBottom: 8, color: "inherit" }}>{it.title}</h3>
              <p style={{ color: (isBento && i === 0) ? "#A1E4DB" : isDark ? "#A1E4DB" : "var(--fg-2)", margin: 0 }}>{it.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
window.Features = Features;
