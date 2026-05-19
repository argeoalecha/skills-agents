import { useState, useEffect, useRef, useCallback, createContext, useContext } from "react";

// ============================================================
//  ███████╗ █████╗  █████╗ ███████╗
//  ██╔════╝██╔══██╗██╔══██╗██╔════╝
//  ███████╗███████║███████║███████╗
//  ╚════██║██╔══██║██╔══██║╚════██║
//  ███████║██║  ██║██║  ██║███████║
//  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
//
//  SaaS Product Landing Template
//  Stack: Next.js 15 · Tailwind · Supabase · Vercel
//
//  Use when the client sells software (web app, API, AI tool, dev tool).
//  Pricing-led conversion. Free trial / signup is the primary CTA.
//
//  HOW TO ADAPT:
//    1. Edit SITE_CONFIG — brand, theme, features, pricing tiers
//    2. Wire SUPABASE_CONFIG → real env vars in production
//    3. Run schema (bottom) for signups + waitlist tables
//    4. In Phase B scaffold: convert direct supabase calls to /api routes
//    5. Add rate limiting + Turnstile on signup endpoint (see skill.md)
// ============================================================

const SITE_CONFIG = {
  brand: {
    name: "Flowstack",
    shortName: "FS",
    tagline: "Ship faster. Operate calmer.",
    subTagline: "The all-in-one ops platform for fast-moving teams.",
    description:
      "Flowstack unifies incident response, on-call rotations, and post-mortems in one tool — so your team spends less time on logistics and more time shipping.",
    founded: "2023",
    location: "Manila, Philippines",
    phone: "+63 2 1234 5678",
    email: "hello@flowstack.io",
    address: "BGC, Taguig, Metro Manila",
    industry: "SaaS / DevOps",
  },

  theme: {
    bg:        "#0a3d3a",
    surface:   "#0d4a47",
    card:      "#125754",
    border:    "rgba(255,255,255,0.08)",
    accent:    "#ff6b47",
    accentLit: "#ff8c70",
    cyan:      "#5eead4",
    text:      "#faf7f5",
    muted:     "#a8c4c1",
    subtle:    "#4a6f6c",
  },

  nav: ["Features", "Pricing", "Customers", "FAQ"],

  trustedBy: ["Acme Inc.", "GlobeStream", "PesoPay", "MetroLogix", "Kuya Foods", "Bayan Health"],

  features: [
    { icon: "◈", title: "Incident management",  desc: "Open, triage, and resolve incidents from Slack, web, or mobile — with auto-paging and SLA timers." },
    { icon: "◉", title: "On-call rotations",     desc: "Schedule rotations across teams and timezones. Smart overrides for holidays and PTO." },
    { icon: "◐", title: "Status pages",          desc: "Branded public + private status pages. Auto-update from your monitoring stack." },
    { icon: "◑", title: "Post-mortems",          desc: "Structured templates, action items, and follow-through tracking. AI summary draft included." },
    { icon: "◒", title: "Integrations",          desc: "Slack, Teams, Datadog, Sentry, PagerDuty, Linear, Jira, GitHub. 30+ out of the box." },
    { icon: "◓", title: "SOC 2 ready",           desc: "Audit-ready logs, RBAC, SSO/SAML, and data residency controls for enterprise customers." },
  ],

  howItWorks: [
    { n: "01", t: "Connect your stack",       d: "Plug in Slack, your monitoring tools, and your code repo in under 10 minutes." },
    { n: "02", t: "Set up your rotations",    d: "Import your team, define escalation policies, and pick your incident workflow." },
    { n: "03", t: "Run your first incident", d: "Resolve faster, document automatically, and learn from every outage." },
  ],

  pricing: {
    monthly: [
      {
        name: "Starter",
        price: "₱0",
        period: "/forever",
        desc: "For small teams getting started.",
        features: ["Up to 5 responders", "Slack + email integrations", "Public status page", "30-day incident history", "Community support"],
        cta: "Start free",
        highlighted: false,
      },
      {
        name: "Growth",
        price: "₱1,490",
        period: "/user/month",
        desc: "For scaling engineering teams.",
        features: ["Unlimited responders", "All 30+ integrations", "Private + public status pages", "1-year incident history", "AI post-mortem drafts", "Priority email support"],
        cta: "Start 14-day trial",
        highlighted: true,
      },
      {
        name: "Enterprise",
        price: "Custom",
        period: "",
        desc: "For regulated / large orgs.",
        features: ["Everything in Growth", "SSO / SAML", "SOC 2 reports", "Dedicated CSM", "99.99% uptime SLA", "Data residency (PH / SG / US)"],
        cta: "Talk to sales",
        highlighted: false,
      },
    ],
  },

  testimonials: [
    { quote: "Reduced our mean time to resolution by 60% in the first month. The Slack-first workflow is exactly what we needed.", author: "VP Engineering, Series B Fintech (PH)", avatar: "VE" },
    { quote: "Setup took an afternoon. By the next on-call rotation, the team was running cleaner incidents than ever.", author: "SRE Lead, E-commerce Platform (SG)", avatar: "SL" },
    { quote: "Our post-mortems used to take a week. With Flowstack's AI draft, we ship them in a day with better follow-through.", author: "Head of Platform, Healthtech (MY)", avatar: "HP" },
  ],

  faq: [
    { q: "Is there a free trial?",                a: "Yes — 14 days of the Growth plan, no credit card required. The Starter tier is free forever for up to 5 responders." },
    { q: "Where is my data stored?",              a: "By default, AWS Singapore (ap-southeast-1). Enterprise customers can choose PH (Manila), SG, or US-East." },
    { q: "Do you support GCash / Maya?",          a: "Yes, for PH-based customers paying in ₱. We also accept Stripe (cards), wire, and PO billing on the Enterprise plan." },
    { q: "What's the cancellation policy?",       a: "Cancel any time from the dashboard. No questions, no retention call. We refund the unused portion of annual plans pro-rata." },
    { q: "Is Flowstack SOC 2 certified?",         a: "We're SOC 2 Type II as of Q4 2025. Audit reports available under NDA for Enterprise prospects." },
    { q: "Can I self-host?",                      a: "Not currently. We focus on the hosted product. For air-gapped deployments, contact us about our managed-on-prem option." },
  ],

  social: { linkedin: "https://linkedin.com", twitter: "https://twitter.com", github: "https://github.com" },
};

// ============================================================
// SUPABASE — mock client (artifact only)
// Schema:
//   CREATE TABLE signups (
//     id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
//     email text NOT NULL,
//     company text,
//     team_size text,
//     plan text,
//     created_at timestamptz DEFAULT now()
//   );
//   ALTER TABLE signups ENABLE ROW LEVEL SECURITY;
//   CREATE POLICY "allow_insert" ON signups FOR INSERT WITH CHECK (true);
//   -- Add rate limiting + Turnstile in /api/signup route before production
// ============================================================

const mockDB = { signups: [], contacts: [] };
const supabase = {
  from: (table) => ({
    insert: async (data) => {
      await new Promise(r => setTimeout(r, 700));
      if (Math.random() > 0.04) {
        mockDB[table]?.push({ ...data, id: crypto.randomUUID(), created_at: new Date().toISOString() });
        return { data: mockDB[table], error: null };
      }
      return { data: null, error: { message: "Insert failed" } };
    },
  }),
  auth: {
    _session: null,
    _listeners: [],
    signInWithPassword: async ({ email, password }) => {
      await new Promise(r => setTimeout(r, 800));
      if (email && password.length >= 6) {
        const session = { user: { email, id: crypto.randomUUID() } };
        supabase.auth._session = session;
        supabase.auth._listeners.forEach(fn => fn("SIGNED_IN", session));
        return { data: session, error: null };
      }
      return { data: null, error: { message: "Invalid credentials" } };
    },
    signUp: async ({ email, password }) => {
      await new Promise(r => setTimeout(r, 800));
      if (email && password.length >= 6) return { data: { user: { email } }, error: null };
      return { data: null, error: { message: "Password must be at least 6 characters" } };
    },
    signOut: async () => {
      supabase.auth._session = null;
      supabase.auth._listeners.forEach(fn => fn("SIGNED_OUT", null));
      return { error: null };
    },
    getSession: async () => ({ data: { session: supabase.auth._session } }),
    onAuthStateChange: (fn) => {
      supabase.auth._listeners.push(fn);
      return { data: { subscription: { unsubscribe: () => {} } } };
    },
  },
};

// ============================================================
// TOKENS + CONTEXT + HOOKS
// ============================================================
const T = SITE_CONFIG.theme;
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => setSession(s));
    return () => subscription.unsubscribe();
  }, []);
  return (
    <AuthContext.Provider value={{
      session, user: session?.user,
      signIn: (e, p) => supabase.auth.signInWithPassword({ email: e, password: p }),
      signUp: (e, p) => supabase.auth.signUp({ email: e, password: p }),
      signOut: () => supabase.auth.signOut(),
    }}>{children}</AuthContext.Provider>
  );
}
const useAuth = () => useContext(AuthContext);

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
function Reveal({ children, delay = 0, y = 24 }) {
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
    fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600,
    fontSize: "0.72rem", letterSpacing: "0.18em",
    textTransform: "uppercase", color: T.accent, marginBottom: "0.75rem",
  }}>{children}</p>;
}

function H2({ children }) {
  return <h2 style={{
    fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700,
    fontSize: "clamp(2rem, 4.5vw, 3.25rem)",
    lineHeight: 1.08, letterSpacing: "-0.025em",
    color: T.text, marginBottom: "1rem",
  }}>{children}</h2>;
}

function Muted({ children, style = {} }) {
  return <p style={{
    fontFamily: "'Inter', sans-serif", color: T.muted,
    fontSize: "1rem", lineHeight: 1.7, ...style,
  }}>{children}</p>;
}

function Btn({ children, onClick, variant = "primary", size = "md", type = "button", disabled = false, full = false }) {
  const styles = {
    primary: { background: T.accent, color: "#fff", border: "none" },
    ghost:   { background: "transparent", color: T.text, border: `1px solid ${T.border}` },
    outline: { background: "transparent", color: T.accentLit, border: `1px solid ${T.accent}60` },
    light:   { background: T.text, color: T.bg, border: "none" },
  };
  const sizes = {
    sm: { padding: "0.45rem 1rem", fontSize: "0.8rem" },
    md: { padding: "0.7rem 1.5rem", fontSize: "0.9rem" },
    lg: { padding: "0.95rem 2.25rem", fontSize: "1rem" },
  };
  return (
    <button type={type} onClick={onClick} disabled={disabled} style={{
      ...styles[variant], ...sizes[size],
      fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600,
      letterSpacing: "0", borderRadius: 8,
      cursor: disabled ? "not-allowed" : "pointer",
      transition: "all 0.2s", opacity: disabled ? 0.5 : 1,
      width: full ? "100%" : "auto",
      display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "0.4rem",
    }}
      onMouseOver={e => { if (!disabled) e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseOut={e => { e.currentTarget.style.transform = "translateY(0)"; }}
    >{children}</button>
  );
}

function Tag({ children }) {
  return <span style={{
    display: "inline-block", background: `${T.cyan}14`, color: T.cyan,
    border: `1px solid ${T.cyan}30`, borderRadius: 999,
    padding: "3px 10px", fontSize: "0.7rem", fontWeight: 600,
    letterSpacing: "0.04em", marginRight: 6, marginTop: 6,
    fontFamily: "'Inter', sans-serif",
  }}>{children}</span>;
}

function Input({ label, name, type = "text", value, onChange, placeholder, required }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      {label && <label style={{
        display: "block", color: T.muted, fontFamily: "'Inter', sans-serif",
        fontSize: "0.78rem", fontWeight: 500, marginBottom: "0.4rem",
      }}>{label}{required && <span style={{ color: T.accent }}> *</span>}</label>}
      <input name={name} type={type} value={value} onChange={onChange} placeholder={placeholder} required={required}
        style={{
          width: "100%", background: T.surface, border: `1px solid ${T.border}`,
          borderRadius: 8, padding: "0.75rem 1rem", color: T.text,
          fontFamily: "'Inter', sans-serif", fontSize: "0.9rem",
          outline: "none", boxSizing: "border-box", transition: "border-color 0.2s",
          colorScheme: "dark",
        }}
        onFocus={e => e.target.style.borderColor = T.accent}
        onBlur={e => e.target.style.borderColor = T.border}
      />
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
      background: "rgba(0,0,0,0.6)", backdropFilter: "blur(8px)",
      display: "flex", alignItems: "center", justifyContent: "center", padding: "1.5rem",
    }} onClick={onClose}>
      <div style={{
        background: T.card, borderRadius: 14, border: `1px solid ${T.border}`,
        boxShadow: "0 32px 80px rgba(0,0,0,0.55)",
        padding: "2.25rem", maxWidth: 440, width: "100%", position: "relative",
      }} onClick={e => e.stopPropagation()}>
        <button onClick={onClose} style={{
          position: "absolute", top: "1rem", right: "1rem",
          background: "none", border: "none", color: T.muted,
          fontSize: "1.25rem", cursor: "pointer", lineHeight: 1,
        }}>×</button>
        {children}
      </div>
    </div>
  );
}

// ============================================================
// NAV
// ============================================================
function Nav({ onSignupOpen, onSignInOpen }) {
  const scrollY = useScrollY();
  const { user, signOut } = useAuth();
  const scrolled = scrollY > 40;
  const scrollTo = useCallback((id) =>
    document.getElementById(id.toLowerCase())?.scrollIntoView({ behavior: "smooth" }), []);

  return (
    <nav style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 999,
      background: scrolled ? `${T.bg}ee` : "transparent",
      backdropFilter: scrolled ? "blur(14px)" : "none",
      borderBottom: scrolled ? `1px solid ${T.border}` : "1px solid transparent",
      transition: "all 0.3s ease",
    }}>
      <div style={{
        maxWidth: 1200, margin: "0 auto", padding: "0 1.5rem",
        display: "flex", alignItems: "center", justifyContent: "space-between", height: 68,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          <div style={{
            width: 34, height: 34, borderRadius: 8,
            background: `linear-gradient(135deg, ${T.accent}, ${T.accentLit})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700,
            color: "#fff", fontSize: "0.85rem",
          }}>{SITE_CONFIG.brand.shortName}</div>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1rem", color: T.text }}>
            {SITE_CONFIG.brand.name}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1.75rem" }}>
          {SITE_CONFIG.nav.map(item => (
            <button key={item} onClick={() => scrollTo(item)} style={{
              background: "none", border: "none", cursor: "pointer",
              color: T.muted, fontFamily: "'Inter', sans-serif",
              fontSize: "0.875rem", fontWeight: 500,
              transition: "color 0.2s", padding: "4px 0",
            }}
              onMouseOver={e => e.target.style.color = T.text}
              onMouseOut={e => e.target.style.color = T.muted}
            >{item}</button>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {user ? (
            <Btn variant="ghost" size="sm" onClick={signOut}>Sign Out</Btn>
          ) : (
            <Btn variant="ghost" size="sm" onClick={onSignInOpen}>Sign in</Btn>
          )}
          <Btn size="sm" onClick={onSignupOpen}>Start free</Btn>
        </div>
      </div>
    </nav>
  );
}

// ============================================================
// HERO
// ============================================================
function Hero({ onSignupOpen }) {
  return (
    <section style={{ minHeight: "100vh", background: T.bg, position: "relative", overflow: "hidden", display: "flex", alignItems: "center" }}>
      <div style={{ position: "absolute", inset: 0, backgroundImage: `radial-gradient(${T.subtle}40 1px, transparent 1px)`, backgroundSize: "32px 32px", maskImage: "radial-gradient(ellipse 80% 70% at 50% 40%, black 30%, transparent 100%)" }} />
      <div style={{ position: "absolute", top: "15%", left: "-10%", width: 600, height: 600, background: `radial-gradient(circle, ${T.accent}1a, transparent 65%)`, borderRadius: "50%", pointerEvents: "none" }} />
      <div style={{ position: "absolute", bottom: "-10%", right: "-10%", width: 500, height: 500, background: `radial-gradient(circle, ${T.cyan}14, transparent 65%)`, borderRadius: "50%", pointerEvents: "none" }} />

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "7rem 1.5rem 4rem", position: "relative", zIndex: 1, textAlign: "center", width: "100%" }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: "0.5rem",
          background: `${T.cyan}14`, border: `1px solid ${T.cyan}30`,
          borderRadius: 999, padding: "5px 14px", marginBottom: "1.75rem",
          animation: "fadeUp 0.5s ease both",
        }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: T.cyan }} />
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.78rem", color: T.cyan, fontWeight: 500 }}>
            SOC 2 Type II · 14-day free trial · No credit card
          </span>
        </div>

        <h1 style={{
          fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700,
          fontSize: "clamp(2.5rem, 6vw, 5rem)",
          lineHeight: 1.05, letterSpacing: "-0.03em",
          color: T.text, marginBottom: "1.5rem",
          animation: "fadeUp 0.6s ease 0.08s both",
        }}>
          {SITE_CONFIG.brand.tagline}
        </h1>

        <p style={{
          fontFamily: "'Inter', sans-serif", color: T.muted,
          fontSize: "clamp(1rem, 1.4vw, 1.2rem)", lineHeight: 1.7,
          maxWidth: 620, margin: "0 auto 2.5rem",
          animation: "fadeUp 0.6s ease 0.16s both",
        }}>
          {SITE_CONFIG.brand.description}
        </p>

        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center", flexWrap: "wrap", animation: "fadeUp 0.6s ease 0.24s both" }}>
          <Btn size="lg" onClick={onSignupOpen}>Start free trial →</Btn>
          <Btn variant="ghost" size="lg" onClick={() => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" })}>
            See features
          </Btn>
        </div>

        {/* Product preview mock */}
        <Reveal delay={0.3}>
          <div style={{
            marginTop: "5rem", maxWidth: 980, marginLeft: "auto", marginRight: "auto",
            background: T.card, border: `1px solid ${T.border}`,
            borderRadius: 14, padding: "0.5rem",
            boxShadow: `0 40px 80px rgba(0,0,0,0.4), 0 0 0 1px ${T.accent}20`,
          }}>
            <div style={{ background: T.surface, borderRadius: 10, padding: "1.5rem", aspectRatio: "16/9", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ textAlign: "center", color: T.subtle, fontFamily: "'Inter', sans-serif", fontSize: "0.85rem" }}>
                ⌬ Product screenshot placeholder<br />
                <span style={{ fontSize: "0.75rem" }}>Replace with actual app screenshot</span>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

// ============================================================
// TRUSTED BY
// ============================================================
function TrustedBy() {
  return (
    <section style={{ background: T.bg, padding: "2rem 1.5rem 4rem", borderBottom: `1px solid ${T.border}` }}>
      <div style={{ maxWidth: 1100, margin: "0 auto", textAlign: "center" }}>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.78rem", color: T.subtle, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "1.5rem" }}>
          Trusted by engineering teams at
        </p>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", flexWrap: "wrap", gap: "2.5rem" }}>
          {SITE_CONFIG.trustedBy.map(name => (
            <span key={name} style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: "1.05rem", color: T.muted, opacity: 0.7 }}>{name}</span>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// FEATURES
// ============================================================
function Features() {
  return (
    <section id="features" style={{ background: T.surface, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "4rem" }}>
            <Label>Features</Label>
            <H2>Everything you need to operate calmly</H2>
            <Muted style={{ maxWidth: 600, margin: "0 auto" }}>
              One platform across incident response, on-call, and post-mortems — built by engineers, for engineers.
            </Muted>
          </div>
        </Reveal>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))",
          gap: "1.25rem",
        }}>
          {SITE_CONFIG.features.map((f, i) => (
            <Reveal key={i} delay={i * 0.05}>
              <div style={{
                background: T.card, padding: "2rem",
                borderRadius: 12, border: `1px solid ${T.border}`,
                height: "100%", transition: "all 0.25s",
              }}
                onMouseOver={e => { e.currentTarget.style.borderColor = `${T.accent}40`; e.currentTarget.style.transform = "translateY(-2px)"; }}
                onMouseOut={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.transform = "translateY(0)"; }}
              >
                <div style={{
                  width: 42, height: 42, borderRadius: 10,
                  background: `${T.accent}18`, border: `1px solid ${T.accent}30`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "1.3rem", color: T.accent, marginBottom: "1.25rem",
                }}>{f.icon}</div>
                <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.1rem", color: T.text, marginBottom: "0.5rem" }}>
                  {f.title}
                </h3>
                <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.9rem", lineHeight: 1.65 }}>
                  {f.desc}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// HOW IT WORKS
// ============================================================
function HowItWorks() {
  return (
    <section style={{ background: T.bg, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "4rem" }}>
            <Label>How it works</Label>
            <H2>Live in under an hour</H2>
          </div>
        </Reveal>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "2rem" }}>
          {SITE_CONFIG.howItWorks.map((s, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <div>
                <div style={{
                  fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700,
                  fontSize: "0.85rem", color: T.accent, marginBottom: "0.75rem",
                  letterSpacing: "0.1em",
                }}>{s.n}</div>
                <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.25rem", color: T.text, marginBottom: "0.6rem" }}>
                  {s.t}
                </h3>
                <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.95rem", lineHeight: 1.7 }}>
                  {s.d}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// PRICING
// ============================================================
function Pricing({ onSignupOpen }) {
  return (
    <section id="pricing" style={{ background: T.surface, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
            <Label>Pricing</Label>
            <H2>Simple, transparent, ₱-priced</H2>
            <Muted style={{ maxWidth: 540, margin: "0 auto" }}>
              No hidden fees. No "contact us" for normal teams. Cancel anytime.
            </Muted>
          </div>
        </Reveal>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", maxWidth: 1000, margin: "0 auto" }}>
          {SITE_CONFIG.pricing.monthly.map((tier, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <div style={{
                background: tier.highlighted ? `linear-gradient(180deg, ${T.accent}15, ${T.card})` : T.card,
                border: `1px solid ${tier.highlighted ? T.accent + "60" : T.border}`,
                borderRadius: 14, padding: "2.25rem 1.75rem",
                position: "relative", height: "100%",
                display: "flex", flexDirection: "column",
              }}>
                {tier.highlighted && (
                  <span style={{
                    position: "absolute", top: -10, left: "50%", transform: "translateX(-50%)",
                    background: T.accent, color: "#fff",
                    fontFamily: "'Space Grotesk', sans-serif", fontSize: "0.7rem",
                    fontWeight: 700, padding: "3px 12px", borderRadius: 999,
                    letterSpacing: "0.05em",
                  }}>MOST POPULAR</span>
                )}

                <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.1rem", color: T.text, marginBottom: "0.4rem" }}>
                  {tier.name}
                </h3>
                <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.85rem", marginBottom: "1.5rem" }}>
                  {tier.desc}
                </p>

                <div style={{ marginBottom: "1.75rem" }}>
                  <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "2.5rem", color: T.text }}>
                    {tier.price}
                  </span>
                  <span style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.85rem" }}>
                    {tier.period}
                  </span>
                </div>

                <ul style={{ listStyle: "none", padding: 0, margin: 0, marginBottom: "1.75rem", flex: 1 }}>
                  {tier.features.map(f => (
                    <li key={f} style={{
                      fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.875rem",
                      lineHeight: 1.5, marginBottom: "0.65rem", display: "flex", gap: "0.6rem", alignItems: "flex-start",
                    }}>
                      <span style={{ color: T.cyan, fontWeight: 700, flexShrink: 0 }}>✓</span>
                      {f}
                    </li>
                  ))}
                </ul>

                <Btn variant={tier.highlighted ? "primary" : "ghost"} size="md" full onClick={onSignupOpen}>
                  {tier.cta}
                </Btn>
              </div>
            </Reveal>
          ))}
        </div>

        <p style={{ textAlign: "center", marginTop: "2rem", fontFamily: "'Inter', sans-serif", color: T.subtle, fontSize: "0.8rem" }}>
          Prices in PHP. Stripe (cards), GCash, Maya, and PO billing accepted.
        </p>
      </div>
    </section>
  );
}

// ============================================================
// TESTIMONIALS
// ============================================================
function Testimonials() {
  return (
    <section id="customers" style={{ background: T.bg, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
            <Label>Customers</Label>
            <H2>Loved by ops-conscious teams</H2>
          </div>
        </Reveal>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))", gap: "1.5rem" }}>
          {SITE_CONFIG.testimonials.map((t, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <div style={{
                background: T.card, border: `1px solid ${T.border}`,
                borderRadius: 12, padding: "1.75rem",
                height: "100%",
              }}>
                <p style={{
                  fontFamily: "'Inter', sans-serif", color: T.text,
                  fontSize: "0.95rem", lineHeight: 1.7, marginBottom: "1.5rem",
                }}>"{t.quote}"</p>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: "50%",
                    background: `linear-gradient(135deg, ${T.accent}, ${T.accentLit})`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700,
                    color: "#fff", fontSize: "0.8rem",
                  }}>{t.avatar}</div>
                  <span style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.82rem" }}>
                    {t.author}
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
// FAQ
// ============================================================
function FAQ() {
  const [open, setOpen] = useState(null);
  return (
    <section id="faq" style={{ background: T.surface, padding: "6rem 1.5rem" }}>
      <div style={{ maxWidth: 760, margin: "0 auto" }}>
        <Reveal>
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <Label>FAQ</Label>
            <H2>Common questions</H2>
          </div>
        </Reveal>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {SITE_CONFIG.faq.map((item, i) => (
            <Reveal key={i} delay={i * 0.04}>
              <div style={{
                background: T.card, border: `1px solid ${T.border}`,
                borderRadius: 10, overflow: "hidden",
              }}>
                <button onClick={() => setOpen(open === i ? null : i)} style={{
                  width: "100%", background: "none", border: "none", cursor: "pointer",
                  padding: "1.25rem 1.5rem", textAlign: "left",
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600,
                  fontSize: "0.95rem", color: T.text,
                }}>
                  <span>{item.q}</span>
                  <span style={{ color: T.accent, fontSize: "1.25rem", transition: "transform 0.2s", transform: open === i ? "rotate(45deg)" : "rotate(0)" }}>+</span>
                </button>
                {open === i && (
                  <div style={{ padding: "0 1.5rem 1.25rem", fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.9rem", lineHeight: 1.7 }}>
                    {item.a}
                  </div>
                )}
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// SIGNUP MODAL (form → Supabase signups table)
// ============================================================
function SignupModal({ open, onClose }) {
  const [form, setForm] = useState({ email: "", company: "", team_size: "", consent: false });
  const [status, setStatus] = useState("idle");
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.consent) return;
    setStatus("loading");
    const { error } = await supabase.from("signups").insert({
      email: form.email, company: form.company || null,
      team_size: form.team_size || null, plan: "growth_trial",
    });
    setStatus(error ? "error" : "success");
  };

  if (status === "success") return (
    <Modal open={open} onClose={() => { onClose(); setStatus("idle"); setForm({ email: "", company: "", team_size: "", consent: false }); }}>
      <div style={{ textAlign: "center", padding: "0.5rem 0" }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>✨</div>
        <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.35rem", color: T.text, marginBottom: "0.5rem" }}>
          You're in.
        </h3>
        <Muted>Check your inbox — we just sent your trial workspace link.</Muted>
        <div style={{ marginTop: "1.5rem" }}>
          <Btn onClick={() => { onClose(); setStatus("idle"); }} full>Close</Btn>
        </div>
      </div>
    </Modal>
  );

  return (
    <Modal open={open} onClose={onClose}>
      <Label>Start free trial</Label>
      <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.4rem", color: T.text, marginBottom: "0.4rem" }}>
        14 days, no card required
      </h3>
      <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.85rem", marginBottom: "1.5rem" }}>
        Get the full Growth plan. Downgrade to free Starter at any time.
      </p>

      <form onSubmit={submit}>
        <Input label="Work email" type="email" value={form.email} onChange={set("email")} placeholder="you@company.com" required />
        <Input label="Company" value={form.company} onChange={set("company")} placeholder="Acme Inc." />
        <Input label="Team size" value={form.team_size} onChange={set("team_size")} placeholder="e.g. 5–20 engineers" />

        <label style={{ display: "flex", gap: "0.6rem", alignItems: "flex-start", fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.78rem", lineHeight: 1.5, marginBottom: "1.25rem", cursor: "pointer" }}>
          <input type="checkbox" checked={form.consent} onChange={set("consent")} required style={{ marginTop: 3, accentColor: T.accent }} />
          <span>I agree to the Privacy Policy and to receive product updates. Required for PH DPA / RA 10173 compliance.</span>
        </label>

        {status === "error" && <p style={{ color: "#f87171", fontFamily: "'Inter', sans-serif", fontSize: "0.8rem", marginBottom: "0.75rem" }}>Sign up failed — try again or email us.</p>}

        <Btn type="submit" disabled={status === "loading" || !form.consent} full size="lg">
          {status === "loading" ? "Creating workspace…" : "Start free trial →"}
        </Btn>
      </form>
    </Modal>
  );
}

// ============================================================
// SIGNIN MODAL (existing customers)
// ============================================================
function SignInModal({ open, onClose }) {
  const { signIn } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [status, setStatus] = useState("idle");
  const [err, setErr] = useState("");
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setStatus("loading"); setErr("");
    const { error } = await signIn(form.email, form.password);
    setStatus("idle");
    if (error) setErr(error.message);
    else onClose();
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Label>Sign in</Label>
      <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.4rem", color: T.text, marginBottom: "1.5rem" }}>
        Welcome back
      </h3>
      <form onSubmit={submit}>
        <Input label="Email" type="email" value={form.email} onChange={set("email")} placeholder="you@company.com" required />
        <Input label="Password" type="password" value={form.password} onChange={set("password")} placeholder="••••••••" required />
        {err && <p style={{ color: "#f87171", fontFamily: "'Inter', sans-serif", fontSize: "0.8rem", marginBottom: "0.75rem" }}>{err}</p>}
        <Btn type="submit" disabled={status === "loading"} full size="lg">
          {status === "loading" ? "Signing in…" : "Sign in"}
        </Btn>
      </form>
    </Modal>
  );
}

// ============================================================
// CTA BANNER
// ============================================================
function CTABanner({ onSignupOpen }) {
  return (
    <section style={{ background: T.bg, padding: "5rem 1.5rem", borderTop: `1px solid ${T.border}` }}>
      <div style={{
        maxWidth: 900, margin: "0 auto",
        background: `linear-gradient(135deg, ${T.accent}, ${T.accentLit})`,
        borderRadius: 16, padding: "3.5rem 2rem", textAlign: "center",
      }}>
        <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "clamp(1.5rem, 3vw, 2.25rem)", color: "#fff", marginBottom: "0.75rem", letterSpacing: "-0.02em" }}>
          Ready to ship faster?
        </h3>
        <p style={{ fontFamily: "'Inter', sans-serif", color: "rgba(255,255,255,0.92)", fontSize: "1rem", maxWidth: 500, margin: "0 auto 2rem" }}>
          Start your 14-day trial. Bring your team. Resolve your next incident with Flowstack.
        </p>
        <Btn variant="light" size="lg" onClick={onSignupOpen}>Start free trial →</Btn>
      </div>
    </section>
  );
}

// ============================================================
// FOOTER
// ============================================================
function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer style={{ background: T.bg, borderTop: `1px solid ${T.border}`, padding: "3rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "2rem", marginBottom: "2.5rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: "0.75rem" }}>
              <div style={{
                width: 30, height: 30, borderRadius: 7,
                background: `linear-gradient(135deg, ${T.accent}, ${T.accentLit})`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700,
                color: "#fff", fontSize: "0.75rem",
              }}>{SITE_CONFIG.brand.shortName}</div>
              <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.95rem" }}>
                {SITE_CONFIG.brand.name}
              </span>
            </div>
            <p style={{ fontFamily: "'Inter', sans-serif", color: T.muted, fontSize: "0.85rem", maxWidth: 280, lineHeight: 1.6 }}>
              {SITE_CONFIG.brand.subTagline}
            </p>
          </div>

          <div style={{ display: "flex", gap: "3rem", flexWrap: "wrap" }}>
            {[
              { h: "Product", links: ["Features", "Pricing", "Integrations", "Changelog"] },
              { h: "Company", links: ["About", "Customers", "Careers", "Contact"] },
              { h: "Legal", links: ["Privacy", "Terms", "DPA", "Security"] },
            ].map(col => (
              <div key={col.h}>
                <p style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.8rem", marginBottom: "1rem", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                  {col.h}
                </p>
                {col.links.map(l => (
                  <a key={l} href="#" style={{ display: "block", color: T.muted, fontFamily: "'Inter', sans-serif", fontSize: "0.85rem", textDecoration: "none", marginBottom: "0.55rem" }}>{l}</a>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          flexWrap: "wrap", gap: "1rem",
          borderTop: `1px solid ${T.border}`, paddingTop: "1.5rem",
        }}>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.8rem", color: T.muted }}>
            © {year} {SITE_CONFIG.brand.name}. Built in {SITE_CONFIG.brand.location}.
          </p>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {["Next.js", "Supabase", "Vercel"].map(s => (
              <span key={s} style={{ fontFamily: "'Inter', sans-serif", fontSize: "0.7rem", color: T.subtle, background: T.surface, border: `1px solid ${T.border}`, borderRadius: 4, padding: "2px 8px" }}>{s}</span>
            ))}
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
  const [signupOpen, setSignupOpen] = useState(false);
  const [signInOpen, setSignInOpen] = useState(false);

  return (
    <AuthProvider>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { background: ${T.bg}; color: ${T.text}; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
        ::selection { background: ${T.accent}; color: #fff; }
        input, textarea, select { color-scheme: dark; }
        input::placeholder { color: ${T.subtle}; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 720px) { nav > div > div:nth-child(2) { display: none !important; } }
      `}</style>

      <Nav onSignupOpen={() => setSignupOpen(true)} onSignInOpen={() => setSignInOpen(true)} />
      <Hero onSignupOpen={() => setSignupOpen(true)} />
      <TrustedBy />
      <Features />
      <HowItWorks />
      <Pricing onSignupOpen={() => setSignupOpen(true)} />
      <Testimonials />
      <FAQ />
      <CTABanner onSignupOpen={() => setSignupOpen(true)} />
      <Footer />

      <SignupModal open={signupOpen} onClose={() => setSignupOpen(false)} />
      <SignInModal open={signInOpen} onClose={() => setSignInOpen(false)} />
    </AuthProvider>
  );
}
