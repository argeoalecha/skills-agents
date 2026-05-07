/** Hero — adapts to theme */
function Hero({ theme }) {
  const isDark = theme === "midnight";
  const isEditorial = theme === "editorial";
  const isCoral = theme === "coral";
  const isBento = theme === "bento";

  const bg = isDark
    ? "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(37,164,151,0.25) 0%, transparent 70%), #0F3836"
    : isCoral
      ? "linear-gradient(160deg, #fff5f2 0%, #faf7f5 50%, #F3FFF9 100%)"
      : isBento
        ? "radial-gradient(ellipse 100% 80% at 50% -20%, rgba(37,164,151,0.15) 0%, transparent 60%), #faf7f5"
        : "var(--cream)";

  const headline = isEditorial
    ? <>The design system <br/>that <span style={{ color: "#ff6b47" }}>ships.</span></>
    : <>Built for teams <br/>that ship.</>;

  return (
    <section style={{
      background: bg,
      padding: isEditorial ? "120px 32px 80px" : "100px 32px 80px",
      borderTop: isEditorial ? "4px solid #0F3836" : "none",
      textAlign: isEditorial ? "left" : "center",
    }}>
      <div style={{ maxWidth: 1240, margin: "0 auto" }}>
        <span className="eyebrow" style={{ color: isDark ? "#25A497" : isCoral ? "#ff6b47" : "#1E6E66", display: "block", marginBottom: 24 }}>
          {isEditorial ? "ANNOUNCING · v2.0" : "What's new · April 2026"}
        </span>
        <h1 className="t-hero" style={{
          color: isDark ? "#faf7f5" : "var(--fg-1)",
          margin: 0, maxWidth: isEditorial ? "100%" : 880,
          marginLeft: isEditorial ? 0 : "auto", marginRight: isEditorial ? 0 : "auto",
        }}>{headline}</h1>
        <p className="t-body-lg" style={{
          marginTop: 28,
          color: isDark ? "#A1E4DB" : "var(--fg-2)",
          maxWidth: 580, marginLeft: isEditorial ? 0 : "auto", marginRight: isEditorial ? 0 : "auto",
        }}>
          A calm, contemporary design system that adapts to your product.
          Five themes, one palette, infinite combinations.
        </p>
        <div style={{ marginTop: 40, display: "flex", gap: 12, justifyContent: isEditorial ? "flex-start" : "center" }}>
          <button className="btn-primary">Get started →</button>
          <button className="btn-secondary">View on GitHub</button>
        </div>
      </div>
    </section>
  );
}
window.Hero = Hero;
