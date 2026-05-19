import { useState, useEffect, useRef, useCallback } from "react";

// ============================================================
//  ██╗      ██████╗  ██████╗ █████╗ ██╗
//  ██║     ██╔═══██╗██╔════╝██╔══██╗██║
//  ██║     ██║   ██║██║     ███████║██║
//  ██║     ██║   ██║██║     ██╔══██║██║
//  ███████╗╚██████╔╝╚██████╗██║  ██║███████╗
//  ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝
//
//  Local Business / Service Shop Template
//  Stack: Next.js 15 · Tailwind · Supabase · Vercel
//
//  Use for: restaurant, salon, clinic, automotive, plumber, contractor,
//  spa, gym, dental, vet, photographer, tutor — any local service biz.
//  Highest-volume PH SME segment.
//
//  Primary CTA: book / reserve / call. Phone number is always visible.
//
//  HOW TO ADAPT:
//    1. Edit SITE_CONFIG — brand, services, hours, gallery items
//    2. Pick a Hayah variant (Coral recommended for warm, Classic for premium)
//    3. Wire SUPABASE → bookings table (schema at bottom)
//    4. In Phase B: add Cloudflare Turnstile to /api/booking
//    5. Embed Google Maps iframe — replace MAP_EMBED_URL with real location
// ============================================================

const SITE_CONFIG = {
  brand: {
    name: "Hayah Glow Studio",
    shortName: "HG",
    tagline: "Effortless beauty, the Hayah way.",
    subTagline: "Skin, hair, and wellness — done well, in the heart of BGC.",
    description:
      "A modern beauty studio focused on natural, sustainable results. Walk in for a quick refresh or book a full day of self-care — our team will guide you through every step.",
    founded: "2021",
    location: "BGC, Taguig",
    phone: "+63 917 123 4567",
    email: "hello@hayahglow.ph",
    address: "2F, The Fort Strip, Bonifacio Global City, Taguig, Metro Manila 1634",
    industry: "Beauty & Wellness",
    mapEmbedUrl: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3861.0!2d121.05!3d14.55!2m3!1f0!2f0!3f0",
    // Production: replace with actual `&output=embed` URL from Google Maps share
  },

  // Coral Hayah variant — warm + approachable for beauty/wellness/F&B/local biz
  theme: {
    bg:        "#faf7f5",
    surface:   "#ffffff",
    card:      "#fff8f5",
    border:    "rgba(10,61,58,0.10)",
    accent:    "#ff6b47",
    accentLit: "#ff8c70",
    cyan:      "#0a3d3a",
    text:      "#1a1a1a",
    muted:     "#5a5a5a",
    subtle:    "#a8a8a8",
  },

  nav: ["Services", "Gallery", "Reviews", "Visit", "Book"],

  hours: [
    { day: "Monday",    hours: "10:00 AM – 8:00 PM" },
    { day: "Tuesday",   hours: "10:00 AM – 8:00 PM" },
    { day: "Wednesday", hours: "10:00 AM – 8:00 PM" },
    { day: "Thursday",  hours: "10:00 AM – 9:00 PM" },
    { day: "Friday",    hours: "10:00 AM – 9:00 PM" },
    { day: "Saturday",  hours: "9:00 AM – 9:00 PM" },
    { day: "Sunday",    hours: "10:00 AM – 6:00 PM" },
  ],

  services: [
    {
      category: "Skin",
      items: [
        { name: "Signature Hayah Facial",        duration: "60 min", price: "₱2,500", desc: "Customised cleanse, exfoliation, mask, and massage." },
        { name: "Deep-Clean Acne Treatment",     duration: "75 min", price: "₱2,950", desc: "Extractions, calming serum, blue-light therapy." },
        { name: "Glow-Up Brightening Facial",    duration: "90 min", price: "₱3,400", desc: "Vitamin C peel + hydration boost for dull skin." },
      ],
    },
    {
      category: "Hair",
      items: [
        { name: "Cut + Blow-Dry",                duration: "45 min", price: "₱1,200", desc: "Consultation, wash, precision cut, finish." },
        { name: "Full Colour + Toner",           duration: "2.5 hrs", price: "₱4,800", desc: "Premium ammonia-free colour with gloss toner." },
        { name: "Keratin Smoothing Treatment",   duration: "3 hrs",  price: "₱6,500", desc: "Frizz-free, salon-finish hair for up to 4 months." },
      ],
    },
    {
      category: "Wellness",
      items: [
        { name: "Relaxation Massage",            duration: "60 min", price: "₱1,800", desc: "Swedish-style full body with aromatherapy." },
        { name: "Deep Tissue Therapeutic",       duration: "75 min", price: "₱2,400", desc: "Targets chronic tension. Strong pressure." },
        { name: "Couples Wellness Package",      duration: "90 min", price: "₱4,500", desc: "Side-by-side massage + tea ceremony for two." },
      ],
    },
  ],

  gallery: [
    { caption: "Interior — front lounge",   palette: ["#ff6b47", "#0a3d3a"] },
    { caption: "Skin treatment room",       palette: ["#ff8c70", "#faf7f5"] },
    { caption: "Hair station",              palette: ["#0a3d3a", "#fff8f5"] },
    { caption: "Massage suite",             palette: ["#ff6b47", "#fff8f5"] },
    { caption: "Retail wall",               palette: ["#0a3d3a", "#ff6b47"] },
    { caption: "Reception & tea bar",       palette: ["#fff8f5", "#ff8c70"] },
  ],

  reviews: [
    { name: "Maria S.",   rating: 5, text: "Hands down the best facial I've had in the Philippines. The team listens — they don't just sell upsells. Coming back for sure.",         source: "Google" },
    { name: "James L.",   rating: 5, text: "Brought my wife for the couples package on her birthday. Spotless space, excellent therapists, and surprisingly affordable for BGC.", source: "Google" },
    { name: "Andrea P.",  rating: 5, text: "I've been going monthly for 6 months. My skin has genuinely never looked better. Bea, the lead esthetician, is incredible.",         source: "Facebook" },
    { name: "Kuya Ronald",rating: 5, text: "The keratin treatment lasted me 5 months. Worth every peso. Booking system on the website is also super easy — no chat required.",    source: "Google" },
  ],

  about: {
    title: "A studio built for the way you actually live.",
    body: "We started Hayah Glow in 2021 because Manila deserves a beauty studio that combines clinical-grade results with the warmth of a friend's living room. No upselling. No rushed sessions. Just calm, expert care — whether you have 45 minutes between meetings or a full day to disappear.",
    highlights: [
      { icon: "✦", label: "Licensed therapists",  desc: "All team members hold valid TESDA certifications and undergo monthly skill calibration." },
      { icon: "✧", label: "Clean, vegan products", desc: "We use only cruelty-free, paraben-free brands — most are also locally made." },
      { icon: "◎", label: "Single-use disposables",desc: "Sterile, single-use tools for every client. Hospital-grade cleaning between sessions." },
    ],
  },

  social: { facebook: "https://facebook.com", instagram: "https://instagram.com", tiktok: "https://tiktok.com" },
};

// ============================================================
// SUPABASE — mock client
// Schema:
//   CREATE TABLE bookings (
//     id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
//     name text NOT NULL,
//     phone text NOT NULL,
//     email text,
//     service text NOT NULL,
//     preferred_date date NOT NULL,
//     preferred_time text NOT NULL,
//     notes text,
//     consent_dpa boolean DEFAULT false,
//     created_at timestamptz DEFAULT now()
//   );
//   ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
//   CREATE POLICY "allow_insert" ON bookings FOR INSERT WITH CHECK (true);
//   -- Production: add rate limiting + Turnstile in /api/booking route
// ============================================================

const mockDB = { bookings: [] };
const supabase = {
  from: (table) => ({
    insert: async (data) => {
      await new Promise(r => setTimeout(r, 800));
      if (Math.random() > 0.04) {
        mockDB[table]?.push({ ...data, id: crypto.randomUUID(), created_at: new Date().toISOString() });
        return { data: mockDB[table], error: null };
      }
      return { data: null, error: { message: "Insert failed" } };
    },
  }),
};

// ============================================================
// TOKENS + HOOKS
// ============================================================
const T = SITE_CONFIG.theme;

function useInView(threshold = 0.12) {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { setInView(true); obs.disconnect(); }
    }, { threshold });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [threshold]);
  return [ref, inView];
}

function useScrollY() {
  const [y, setY] = useState(0);
  useEffect(() => {
    const fn = () => setY(window.scrollY);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);
  return y;
}

// ============================================================
// PRIMITIVES
// ============================================================
function Reveal({ children, delay = 0, y = 20 }) {
  const [ref, inView] = useInView();
  return (
    <div ref={ref} style={{
      opacity: inView ? 1 : 0,
      transform: inView ? "translateY(0)" : `translateY(${y}px)`,
      transition: `opacity 0.65s cubic-bezier(.16,1,.3,1) ${delay}s, transform 0.65s cubic-bezier(.16,1,.3,1) ${delay}s`,
    }}>{children}</div>
  );
}

function Label({ children }) {
  return <p style={{
    fontFamily: "'Fraunces', serif", fontStyle: "italic", fontWeight: 400,
    fontSize: "0.95rem", color: T.accent, marginBottom: "0.75rem",
  }}>— {children}</p>;
}

function H2({ children }) {
  return <h2 style={{
    fontFamily: "'Fraunces', serif", fontWeight: 500,
    fontSize: "clamp(2rem, 4.5vw, 3.25rem)",
    lineHeight: 1.1, letterSpacing: "-0.02em",
    color: T.text, marginBottom: "1.25rem",
  }}>{children}</h2>;
}

function Muted({ children, style = {} }) {
  return <p style={{
    fontFamily: "'Inter', sans-serif", color: T.muted,
    fontSize: "1rem", lineHeight: 1.75, ...style,
  }}>{children}</p>;
}

function Btn({ children, onClick, variant = "primary", size = "md", type = "button", disabled = false, full = false }) {
  const styles = {
    primary: { background: T.accent, color: "#fff", border: "none" },
    dark:    { background: T.cyan, color: "#fff", border: "none" },
    ghost:   { background: "transparent", color: T.text, border: `1px solid ${T.text}40` },
    outline: { background: "transparent", color: T.accent, border: `1.5px solid ${T.accent}` },
  };
  const sizes = {
    sm: { padding: "0.5rem 1.1rem", fontSize: "0.82rem" },
    md: { padding: "0.75rem 1.6rem", fontSize: "0.9rem" },
    lg: { padding: "0.95rem 2.25rem", fontSize: "1rem" },
  };
  return (
    <button type={type} onClick={onClick} disabled={disabled} style={{
      ...styles[variant], ...sizes[size],
      fontFamily: "'Inter', sans-serif", fontWeight: 500,
      letterSpacing: "0.02em", borderRadius: 999,
      cursor: disabled ? "not-allowed" : "pointer",
      transition: "all 0.2s", opacity: disabled ? 0.55 : 1,
      width: full ? "100%" : "auto",
      display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "0.45rem",
    }}
      onMouseOver={e => { if (!disabled) e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseOut={e => { e.currentTarget.style.transform = "translateY(0)"; }}
    >{children}</button>
  );
}

function Input({ label, name, type = "text", value, onChange, placeholder, required, as = "input" }) {
  const shared = {
    width: "100%", background: "#fff", border: `1px solid ${T.border}`,
    borderRadius: 10, padding: "0.75rem 1rem", color: T.text,
    fontFamily: "'Inter', sans-serif", fontSize: "0.92rem",
    outline: "none", boxSizing: "border-box", transition: "border-color 0.2s",
  };
  return (
    <div style={{ marginBottom: "1rem" }}>
      {label && <label style={{
        display: "block", color: T.muted, fontFamily: "'Inter', sans-serif",
        fontSize: "0.78rem", fontWeight: 500, marginBottom: "0.4rem",
      }}>{label}{required && <span style={{ color: T.accent }}> *</span>}</label>}
      {as === "textarea"
        ? <textarea name={name} value={value} onChange={onChange} placeholder={placeholder} rows={3} required={required}
            style={{ ...shared, resize: "vertical" }}
            onFocus={e => e.target.style.borderColor = T.accent}
            onBlur={e => e.target.style.borderColor = T.border}
          />
        : as === "select"
        ? null
        : <input name={name} type={type} value={value} onChange={onChange} placeholder={placeholder} required={required}
            style={shared}
            onFocus={e => e.target.style.borderColor = T.accent}
            onBlur={e => e.target.style.borderColor = T.border}
          />
      }
    </div>
  );
}

function Modal({ open, onClose, children }) {
  useEffect(() => {
    const fn = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", fn);
    return () => window.removeEventListener("keydown", fn);
  }, [onClose]);
  if (!open) return null;
  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 9990,
      background: "rgba(10,61,58,0.55)", backdropFilter: "blur(6px)",
      display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem",
    }} onClick={onClose}>
      <div style={{
        background: T.bg, borderRadius: 16, border: `1px solid ${T.border}`,
        boxShadow: "0 32px 80px rgba(0,0,0,0.25)",
        padding: "2.25rem", maxWidth: 480, width: "100%", position: "relative",
        maxHeight: "90vh", overflowY: "auto",
      }} onClick={e => e.stopPropagation()}>
        <button onClick={onClose} style={{
          position: "absolute", top: "1rem", right: "1rem",
          background: "none", border: "none", color: T.muted,
          fontSize: "1.5rem", cursor: "pointer", lineHeight: 1,
        }}>×</button>
        {children}
      </div>
    </div>
  );
}

function Stars({ n = 5 }) {
  return (
    <div style={{ display: "flex", gap: 2, color: T.accent, fontSize: "0.9rem" }}>
      {[1, 2, 3, 4, 5].map(i => <span key={i}>{i <= n ? "★" : "☆"}</span>)}
    </div>
  );
}

// ============================================================
// NAV
// ============================================================
function Nav({ onBookOpen }) {
  const scrollY = useScrollY();
  const scrolled = scrollY > 40;
  const scrollTo = useCallback((id) =>
    document.getElementById(id.toLowerCase())?.scrollIntoView({ behavior: "smooth" }), []);

  return (
    <nav style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 999,
      background: scrolled ? `${T.bg}f5` : "transparent",
      backdropFilter: scrolled ? "blur(14px)" : "none",
      borderBottom: scrolled ? `1px solid ${T.border}` : "1px solid transparent",
      transition: "all 0.3s",
    }}>
      <div style={{
        maxWidth: 1200, margin: "0 auto", padding: "0 1.5rem",
        display: "flex", alignItems: "center", justifyContent: "space-between", height: 72,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          <div style={{
            width: 38, height: 38, borderRadius: "50%",
            background: `linear-gradient(135deg, ${T.accent}, ${T.cyan})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'Fraunces', serif", fontWeight: 500,
            color: "#fff", fontSize: "0.95rem", letterSpacing: "0.02em",
          }}>{SITE_CONFIG.brand.shortName}</div>
          <span style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.15rem", color: T.text, letterSpacing: "-0.01em" }}>
            {SITE_CONFIG.brand.name}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1.75rem" }}>
          {SITE_CONFIG.nav.map(item => (
            <button key={item} onClick={() => scrollTo(item)} style={{
              background: "none", border: "none", cursor: "pointer",
              color: T.muted, fontFamily: "'Inter', sans-serif",
              fontSize: "0.88rem", fontWeight: 500, padding: "4px 0",
              transition: "color 0.2s",
            }}
              onMouseOver={e => e.target.style.color = T.text}
              onMouseOut={e => e.target.style.color = T.muted}
            >{item}</button>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <a href={`tel:${SITE_CONFIG.brand.phone}`} style={{
            display: "flex", alignItems: "center", gap: 6,
            color: T.text, textDecoration: "none",
            fontFamily: "'Inter', sans-serif", fontWeight: 500, fontSize: "0.85rem",
          }}>
            <span style={{ color: T.accent }}>☎</span>
            {SITE_CONFIG.brand.phone}
          </a>
          <Btn size="sm" onClick={onBookOpen}>Book now</Btn>
        </div>
      </div>
    </nav>
  );
}

// ============================================================
// HERO
// ============================================================
function Hero({ onBookOpen }) {
  return (
    <section style={{
      minHeight: "100vh", background: T.bg,
      display: "flex", alignItems: "center",
      position: "relative", overflow: "hidden",
      paddingTop: 72,
    }}>
      {/* Soft warm gradient orbs */}
      <div style={{ position: "absolute", top: "10%", right: "-5%", width: 500, height: 500, background: `radial-gradient(circle, ${T.accent}22, transparent 70%)`, borderRadius: "50%", pointerEvents: "none" }} />
      <div style={{ position: "absolute", bottom: "-15%", left: "-10%", width: 600, height: 600, background: `radial-gradient(circle, ${T.cyan}14, transparent 70%)`, borderRadius: "50%", pointerEvents: "none" }} />

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "4rem 1.5rem", position: "relative", zIndex: 1, width: "100%" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "4rem", alignItems: "center" }}>

          {/* Left — headline */}
          <div>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: "0.5rem",
              background: "#fff", border: `1px solid ${T.border}`,
              borderRadius: 999, padding: "5px 14px 5px 10px",
              marginBottom: "2rem", boxShadow: "0 4px 12px rgba(0,0,0,0.04)",
              animation: "fadeUp 0.5s ease both",
            }}>
              <span style={{ color: T.accent }}>📍</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.78rem", color: T.text, fontWeight: 500 }}>
                {SITE_CONFIG.brand.location} · Est. {SITE_CONFIG.brand.founded}
              </span>
            </div>

            <h1 style={{
              fontFamily: "'Fraunces', serif", fontWeight: 400,
              fontSize: "clamp(2.5rem, 6vw, 5rem)",
              lineHeight: 1.05, letterSpacing: "-0.03em",
              color: T.text, marginBottom: "1.5rem",
              animation: "fadeUp 0.6s ease 0.1s both",
            }}>
              {SITE_CONFIG.brand.tagline}
            </h1>

            <p style={{
              fontFamily: "'Inter', sans-serif", color: T.muted,
              fontSize: "clamp(1rem, 1.3vw, 1.15rem)", lineHeight: 1.7,
              maxWidth: 480, marginBottom: "2.5rem",
              animation: "fadeUp 0.6s ease 0.2s both",
            }}>
              {SITE_CONFIG.brand.description}
            </p>

            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", animation: "fadeUp 0.6s ease 0.3s both" }}>
              <Btn size="lg" onClick={onBookOpen}>Book a session →</Btn>
              <Btn variant="ghost" size="lg" onClick={() => document.getElementById("services")?.scrollIntoView({ behavior: "smooth" })}>
                See services
              </Btn>
            </div>

            {/* Quick info */}
            <div style={{ display: "flex", gap: "2rem", marginTop: "3rem", flexWrap: "wrap", animation: "fadeUp 0.6s ease 0.4s both" }}>
              {[
                { label: "Open today", value: "10am – 8pm" },
                { label: "Walk-ins",   value: "Welcome" },
                { label: "Rating",     value: "4.9 ★ (340+ reviews)" },
              ].map(s => (
                <div key={s.label}>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.72rem", color: T.subtle, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.25rem" }}>{s.label}</p>
                  <p style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1rem", color: T.text }}>{s.value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right — visual block */}
          <div style={{ animation: "fadeUp 0.7s ease 0.35s both" }}>
            <div style={{
              background: `linear-gradient(135deg, ${T.accent}, ${T.cyan})`,
              borderRadius: 24, aspectRatio: "4/5",
              position: "relative", overflow: "hidden",
              boxShadow: "0 30px 60px rgba(0,0,0,0.15)",
            }}>
              {/* Decorative inner */}
              <div style={{
                position: "absolute", inset: "8%",
                border: "1.5px solid rgba(255,255,255,0.35)",
                borderRadius: 18,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <div style={{ textAlign: "center", color: "#fff" }}>
                  <div style={{ fontFamily: "'Fraunces', serif", fontStyle: "italic", fontSize: "clamp(2rem, 4vw, 3rem)", fontWeight: 400, lineHeight: 1.1 }}>
                    Glow.<br />Rest.<br />Repeat.
                  </div>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.85rem", marginTop: "1rem", opacity: 0.9 }}>
                    Replace with hero photo
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============================================================
// SERVICES — categorised, with prices
// ============================================================
function Services() {
  return (
    <section id="services" style={{ background: T.surface, padding: "6rem 1.5rem", borderTop: `1px solid ${T.border}` }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "4rem" }}>
            <Label>Services & Pricing</Label>
            <H2>What we offer</H2>
            <Muted style={{ maxWidth: 540, margin: "0 auto" }}>
              All prices are in ₱ and inclusive of taxes. Service durations are estimates — we'll customise to your needs at no extra cost.
            </Muted>
          </div>
        </Reveal>

        {SITE_CONFIG.services.map((cat, idx) => (
          <Reveal key={cat.category} delay={idx * 0.06}>
            <div style={{ marginBottom: idx < SITE_CONFIG.services.length - 1 ? "3.5rem" : 0 }}>
              <h3 style={{
                fontFamily: "'Fraunces', serif", fontWeight: 500,
                fontSize: "1.5rem", color: T.text,
                marginBottom: "1.5rem", letterSpacing: "-0.01em",
                borderBottom: `1px solid ${T.border}`, paddingBottom: "0.75rem",
              }}>
                {cat.category}
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {cat.items.map(item => (
                  <div key={item.name} style={{
                    display: "grid", gridTemplateColumns: "1fr auto",
                    gap: "1.5rem", padding: "1.25rem 0",
                    borderBottom: `1px solid ${T.border}`,
                    alignItems: "start",
                  }}>
                    <div>
                      <div style={{ display: "flex", gap: "0.75rem", alignItems: "baseline", marginBottom: "0.35rem", flexWrap: "wrap" }}>
                        <p style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.1rem", color: T.text }}>
                          {item.name}
                        </p>
                        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.75rem", color: T.subtle }}>
                          · {item.duration}
                        </span>
                      </div>
                      <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.9rem", lineHeight: 1.6 }}>
                        {item.desc}
                      </p>
                    </div>
                    <p style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.2rem", color: T.accent, whiteSpace: "nowrap" }}>
                      {item.price}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

// ============================================================
// GALLERY
// ============================================================
function Gallery() {
  return (
    <section id="gallery" style={{ background: T.bg, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <Label>The Space</Label>
            <H2>Step inside</H2>
          </div>
        </Reveal>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
          {SITE_CONFIG.gallery.map((g, i) => (
            <Reveal key={i} delay={i * 0.05}>
              <div style={{
                aspectRatio: i === 0 || i === 3 ? "1/1" : "4/5",
                background: `linear-gradient(135deg, ${g.palette[0]}, ${g.palette[1]})`,
                borderRadius: 14, overflow: "hidden",
                position: "relative", cursor: "pointer",
                transition: "transform 0.3s",
              }}
                onMouseOver={e => e.currentTarget.style.transform = "scale(1.02)"}
                onMouseOut={e => e.currentTarget.style.transform = "scale(1)"}
              >
                <div style={{
                  position: "absolute", bottom: 0, left: 0, right: 0,
                  background: "linear-gradient(180deg, transparent, rgba(0,0,0,0.5))",
                  padding: "2rem 1.25rem 1rem",
                  fontFamily: "'Inter', sans-serif", fontSize: "0.8rem",
                  color: "#fff", fontWeight: 500,
                }}>
                  {g.caption}
                </div>
              </div>
            </Reveal>
          ))}
        </div>

        <p style={{ textAlign: "center", marginTop: "2rem", fontFamily: "'Inter', sans-serif", color: T.subtle, fontSize: "0.85rem" }}>
          Replace gradient placeholders with real photography — recommended size: 800×1000 px @ 1x.
        </p>
      </div>
    </section>
  );
}

// ============================================================
// ABOUT
// ============================================================
function About() {
  const a = SITE_CONFIG.about;
  return (
    <section style={{ background: T.surface, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center" }}>
        <Reveal>
          <Label>About us</Label>
          <H2>{a.title}</H2>
          <Muted>{a.body}</Muted>
        </Reveal>

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {a.highlights.map((h, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <div style={{
                background: T.card, borderRadius: 12,
                border: `1px solid ${T.border}`,
                padding: "1.5rem", display: "flex", gap: "1.25rem",
              }}>
                <div style={{
                  width: 44, height: 44, borderRadius: "50%",
                  background: `${T.accent}18`, color: T.accent,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "1.25rem", flexShrink: 0,
                }}>{h.icon}</div>
                <div>
                  <p style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.05rem", color: T.text, marginBottom: "0.35rem" }}>
                    {h.label}
                  </p>
                  <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.88rem", lineHeight: 1.6 }}>
                    {h.desc}
                  </p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// REVIEWS
// ============================================================
function Reviews() {
  return (
    <section id="reviews" style={{ background: T.bg, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <Label>Reviews</Label>
            <H2>What clients say</H2>
            <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", marginTop: "1rem" }}>
              <Stars n={5} />
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.9rem", color: T.text, fontWeight: 500 }}>
                4.9 average · 340+ reviews on Google & Facebook
              </span>
            </div>
          </div>
        </Reveal>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem" }}>
          {SITE_CONFIG.reviews.map((r, i) => (
            <Reveal key={i} delay={i * 0.06}>
              <div style={{
                background: T.surface, border: `1px solid ${T.border}`,
                borderRadius: 14, padding: "1.5rem", height: "100%",
              }}>
                <Stars n={r.rating} />
                <p style={{ fontFamily: "'Inter', sans-serif", color: T.text, fontSize: "0.92rem", lineHeight: 1.7, margin: "0.75rem 0 1.25rem" }}>
                  "{r.text}"
                </p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "0.75rem", borderTop: `1px solid ${T.border}` }}>
                  <span style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, color: T.text, fontSize: "0.9rem" }}>
                    {r.name}
                  </span>
                  <span style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.72rem", color: T.subtle, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    via {r.source}
                  </span>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// VISIT — hours + map + address
// ============================================================
function Visit() {
  return (
    <section id="visit" style={{ background: T.surface, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
            <Label>Visit us</Label>
            <H2>Find your way here</H2>
          </div>
        </Reveal>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: "3rem", alignItems: "start" }}>
          <Reveal>
            <div>
              <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.3rem", color: T.text, marginBottom: "1rem" }}>
                Hours
              </h3>
              <div style={{ marginBottom: "2rem" }}>
                {SITE_CONFIG.hours.map(h => (
                  <div key={h.day} style={{
                    display: "flex", justifyContent: "space-between",
                    padding: "0.6rem 0", borderBottom: `1px solid ${T.border}`,
                    fontFamily: "'Inter', sans-serif", fontSize: "0.9rem",
                  }}>
                    <span style={{ color: T.text, fontWeight: 500 }}>{h.day}</span>
                    <span style={{ color: T.muted }}>{h.hours}</span>
                  </div>
                ))}
              </div>

              <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.3rem", color: T.text, marginBottom: "1rem" }}>
                Address
              </h3>
              <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.95rem", lineHeight: 1.7, marginBottom: "1.5rem" }}>
                {SITE_CONFIG.brand.address}
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                <a href={`tel:${SITE_CONFIG.brand.phone}`} style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: T.text, textDecoration: "none", fontFamily: "'Inter', sans-serif", fontSize: "0.92rem" }}>
                  <span style={{ color: T.accent, width: 24 }}>☎</span> {SITE_CONFIG.brand.phone}
                </a>
                <a href={`mailto:${SITE_CONFIG.brand.email}`} style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: T.text, textDecoration: "none", fontFamily: "'Inter', sans-serif", fontSize: "0.92rem" }}>
                  <span style={{ color: T.accent, width: 24 }}>✉</span> {SITE_CONFIG.brand.email}
                </a>
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <div style={{ borderRadius: 14, overflow: "hidden", border: `1px solid ${T.border}`, aspectRatio: "1/1", background: T.card, position: "relative" }}>
              {/* Placeholder map — replace mapEmbedUrl in SITE_CONFIG */}
              <div style={{
                position: "absolute", inset: 0,
                display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                background: `linear-gradient(135deg, ${T.card}, ${T.surface})`,
                color: T.muted, fontFamily: "'Inter', sans-serif", fontSize: "0.9rem",
                textAlign: "center", padding: "2rem",
              }}>
                <div style={{ fontSize: "3rem", color: T.accent, marginBottom: "1rem" }}>📍</div>
                <p style={{ fontWeight: 500, color: T.text, marginBottom: "0.5rem" }}>Map placeholder</p>
                <p style={{ fontSize: "0.8rem" }}>
                  Replace the &lt;iframe&gt; below with the embed URL from<br />
                  Google Maps → Share → Embed a map
                </p>
              </div>
              {/* Production:
              <iframe
                src={SITE_CONFIG.brand.mapEmbedUrl}
                width="100%" height="100%"
                style={{ border: 0 }}
                allowFullScreen=""
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
              */}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

// ============================================================
// BOOKING MODAL (form → Supabase bookings table)
// ============================================================
function BookingModal({ open, onClose }) {
  const [form, setForm] = useState({
    name: "", phone: "", email: "", service: "",
    preferred_date: "", preferred_time: "", notes: "", consent: false,
  });
  const [status, setStatus] = useState("idle");
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value }));

  const allServices = SITE_CONFIG.services.flatMap(c => c.items.map(i => `${c.category} · ${i.name}`));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.consent) return;
    setStatus("loading");
    const { error } = await supabase.from("bookings").insert({
      name: form.name, phone: form.phone, email: form.email || null,
      service: form.service,
      preferred_date: form.preferred_date,
      preferred_time: form.preferred_time,
      notes: form.notes || null,
      consent_dpa: form.consent,
    });
    setStatus(error ? "error" : "success");
  };

  if (status === "success") return (
    <Modal open={open} onClose={() => { onClose(); setStatus("idle"); setForm({ name: "", phone: "", email: "", service: "", preferred_date: "", preferred_time: "", notes: "", consent: false }); }}>
      <div style={{ textAlign: "center", padding: "0.75rem 0" }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>✨</div>
        <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.4rem", color: T.text, marginBottom: "0.6rem" }}>
          Booking received
        </h3>
        <Muted>We'll call you within 1 hour to confirm. For urgent slots, ring us at <a href={`tel:${SITE_CONFIG.brand.phone}`} style={{ color: T.accent }}>{SITE_CONFIG.brand.phone}</a>.</Muted>
        <div style={{ marginTop: "1.5rem" }}>
          <Btn onClick={() => { onClose(); setStatus("idle"); }} full>Close</Btn>
        </div>
      </div>
    </Modal>
  );

  return (
    <Modal open={open} onClose={onClose}>
      <Label>Book a session</Label>
      <h3 style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1.5rem", color: T.text, marginBottom: "0.5rem" }}>
        Reserve your slot
      </h3>
      <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.85rem", marginBottom: "1.5rem" }}>
        We confirm bookings within 1 hour during business hours.
      </p>

      <form onSubmit={submit}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 1rem" }}>
          <Input label="Full name" value={form.name} onChange={set("name")} placeholder="Juan dela Cruz" required />
          <Input label="Mobile number" type="tel" value={form.phone} onChange={set("phone")} placeholder="0917 123 4567" required />
        </div>

        <Input label="Email (optional)" type="email" value={form.email} onChange={set("email")} placeholder="you@email.com" />

        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", color: T.muted, fontFamily: "'Inter', sans-serif", fontSize: "0.78rem", fontWeight: 500, marginBottom: "0.4rem" }}>
            Service <span style={{ color: T.accent }}>*</span>
          </label>
          <select value={form.service} onChange={set("service")} required style={{
            width: "100%", background: "#fff", border: `1px solid ${T.border}`,
            borderRadius: 10, padding: "0.75rem 1rem", color: form.service ? T.text : T.subtle,
            fontFamily: "'Inter', sans-serif", fontSize: "0.92rem", outline: "none", boxSizing: "border-box",
          }}>
            <option value="">Select a service…</option>
            {allServices.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 1rem" }}>
          <Input label="Preferred date" type="date" value={form.preferred_date} onChange={set("preferred_date")} required />
          <Input label="Preferred time" type="time" value={form.preferred_time} onChange={set("preferred_time")} required />
        </div>

        <Input label="Notes (optional)" as="textarea" value={form.notes} onChange={set("notes")} placeholder="Allergies, preferred therapist, etc." />

        <label style={{ display: "flex", gap: "0.6rem", alignItems: "flex-start", fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.78rem", lineHeight: 1.5, marginBottom: "1.25rem", cursor: "pointer" }}>
          <input type="checkbox" checked={form.consent} onChange={set("consent")} required style={{ marginTop: 3, accentColor: T.accent }} />
          <span>I consent to {SITE_CONFIG.brand.name} contacting me about my booking and to the processing of my personal data per RA 10173 (PH Data Privacy Act).</span>
        </label>

        {status === "error" && <p style={{ color: "#dc2626", fontFamily: "'Inter', sans-serif", fontSize: "0.82rem", marginBottom: "0.75rem" }}>Booking failed — please try again or call us directly.</p>}

        <Btn type="submit" disabled={status === "loading" || !form.consent} full size="lg">
          {status === "loading" ? "Sending…" : "Request booking →"}
        </Btn>
      </form>
    </Modal>
  );
}

// ============================================================
// FOOTER
// ============================================================
function Footer({ onBookOpen }) {
  const year = new Date().getFullYear();
  return (
    <footer style={{ background: T.cyan, color: "#fff", padding: "4rem 1.5rem 2rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr", gap: "3rem", marginBottom: "3rem" }}>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "1rem" }}>
              <div style={{
                width: 38, height: 38, borderRadius: "50%",
                background: `linear-gradient(135deg, ${T.accent}, ${T.accentLit})`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "'Fraunces', serif", fontWeight: 500,
                color: "#fff", fontSize: "0.95rem",
              }}>{SITE_CONFIG.brand.shortName}</div>
              <span style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, color: "#fff", fontSize: "1.15rem" }}>
                {SITE_CONFIG.brand.name}
              </span>
            </div>
            <p style={{ fontFamily: "'Inter', sans-serif", color: "rgba(255,255,255,0.75)", fontSize: "0.9rem", lineHeight: 1.6, maxWidth: 320 }}>
              {SITE_CONFIG.brand.subTagline}
            </p>
            <div style={{ marginTop: "1.5rem" }}>
              <Btn variant="primary" onClick={onBookOpen}>Book a session →</Btn>
            </div>
          </div>

          <div>
            <p style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1rem", marginBottom: "1rem" }}>Visit</p>
            <p style={{ fontFamily: "'Inter', sans-serif", color: "rgba(255,255,255,0.75)", fontSize: "0.88rem", lineHeight: 1.6 }}>
              {SITE_CONFIG.brand.address}<br /><br />
              ☎ <a href={`tel:${SITE_CONFIG.brand.phone}`} style={{ color: "#fff", textDecoration: "none" }}>{SITE_CONFIG.brand.phone}</a><br />
              ✉ <a href={`mailto:${SITE_CONFIG.brand.email}`} style={{ color: "#fff", textDecoration: "none" }}>{SITE_CONFIG.brand.email}</a>
            </p>
          </div>

          <div>
            <p style={{ fontFamily: "'Fraunces', serif", fontWeight: 500, fontSize: "1rem", marginBottom: "1rem" }}>Follow</p>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {[
                { label: "Facebook",  href: SITE_CONFIG.social.facebook },
                { label: "Instagram", href: SITE_CONFIG.social.instagram },
                { label: "TikTok",    href: SITE_CONFIG.social.tiktok },
              ].map(s => (
                <a key={s.label} href={s.href} target="_blank" rel="noopener noreferrer" style={{
                  color: "rgba(255,255,255,0.85)", fontFamily: "'Inter', sans-serif",
                  fontSize: "0.88rem", textDecoration: "none",
                }}>
                  {s.label} →
                </a>
              ))}
            </div>
          </div>
        </div>

        <div style={{
          display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem",
          borderTop: "1px solid rgba(255,255,255,0.15)", paddingTop: "1.5rem",
          fontFamily: "'Inter', sans-serif", fontSize: "0.8rem", color: "rgba(255,255,255,0.6)",
        }}>
          <p>© {year} {SITE_CONFIG.brand.name}. All rights reserved.</p>
          <div style={{ display: "flex", gap: "1.5rem" }}>
            <a href="#" style={{ color: "inherit", textDecoration: "none" }}>Privacy Policy</a>
            <a href="#" style={{ color: "inherit", textDecoration: "none" }}>Terms</a>
            <a href="#" style={{ color: "inherit", textDecoration: "none" }}>DPA Compliance</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============================================================
// ROOT
// ============================================================
export default function App() {
  const [bookOpen, setBookOpen] = useState(false);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Inter:wght@400;500;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { background: ${T.bg}; color: ${T.text}; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
        ::selection { background: ${T.accent}; color: #fff; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 900px) {
          section > div { grid-template-columns: 1fr !important; gap: 2.5rem !important; }
        }
        @media (max-width: 720px) {
          nav > div > div:nth-child(2) { display: none !important; }
          nav > div > div:nth-child(3) > a { display: none !important; }
        }
      `}</style>

      <Nav onBookOpen={() => setBookOpen(true)} />
      <Hero onBookOpen={() => setBookOpen(true)} />
      <Services />
      <Gallery />
      <About />
      <Reviews />
      <Visit />
      <Footer onBookOpen={() => setBookOpen(true)} />

      <BookingModal open={bookOpen} onClose={() => setBookOpen(false)} />
    </>
  );
}
