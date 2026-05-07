/**
 * HayahaiLogo — Hayah-AI brand logo component
 *
 * Props:
 *   tagline  {string|null}  — Tagline text below the logo. Pass null/undefined to hide. Default: null
 *   scale    {number}       — Scale multiplier for width/height. Default: 1
 *   className {string}      — Optional CSS class on the <svg> element
 *
 * Usage:
 *   <HayahaiLogo />
 *   <HayahaiLogo tagline="industrial intell" />
 *   <HayahaiLogo tagline="business automation" scale={1.5} />
 *   <HayahaiLogo tagline={null} />   // mark + wordmark only, no tagline
 */
export default function HayahaiLogo({ tagline = null, scale = 1, className = '' }) {
  const BASE_W = 344;
  const BASE_H = tagline ? 96 : 68;
  const w = BASE_W * scale;
  const h = BASE_H * scale;

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={`0 0 ${BASE_W} ${BASE_H}`}
      width={w}
      height={h}
      role="img"
      aria-label={`Hayah-AI${tagline ? ` — ${tagline}` : ''}`}
      className={className}
    >
      {/* ── Logo Mark: arc + coral dot ── */}
      <path
        d="M 12 52 A 28 28 0 0 1 52 12"
        fill="none"
        stroke="#0a3d3a"
        strokeWidth="8"
        strokeLinecap="round"
      />
      <circle cx="52" cy="12" r="6" fill="#ff6b47" />

      {/* ── Wordmark: hayah-ai ── */}
      <text
        x="68"
        y="48"
        fontFamily="DM Serif Display, Georgia, serif"
        fontSize="44"
        fontWeight="400"
        fill="#0a3d3a"
        letterSpacing="-1.2"
      >
        hayah
        <tspan fill="#7a9b96">-</tspan>
        <tspan fill="#ff6b47" fontStyle="italic">ai</tspan>
      </text>

      {/* ── Tagline: variable per project ── */}
      {tagline && (
        <text
          x="0"
          y="84"
          fontFamily="Inter, Helvetica Neue, sans-serif"
          fontSize="15"
          fontWeight="300"
          fill="#0a3d3a"
          textLength="230"
          lengthAdjust="spacing"
        >
          {tagline}
        </text>
      )}
    </svg>
  );
}
