import { useState, useEffect, useRef, useCallback, createContext, useContext } from "react";

// ============================================================
// ██████╗  ██████╗  ██████╗ ████████╗    ██████╗ ██████╗
// ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝   ██╔══██╗██╔══██╗
// ██████╔╝██║   ██║██║   ██║   ██║      ██║  ██║██████╔╝
// ██╔══██╗██║   ██║██║   ██║   ██║      ██║  ██║██╔══██╗
// ██║  ██║╚██████╔╝╚██████╔╝   ██║      ██████╔╝██████╔╝
// ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝      ╚═════╝ ╚═════╝
//
// Generic Company Website Template
// Stack: Next.js 15 (App Router) · Tailwind CSS · Supabase · Vercel
//
// HOW TO ADAPT THIS TEMPLATE:
//   1. Edit SITE_CONFIG  → brand, content, nav, theme
//   2. Edit SUPABASE_CONFIG → your project URL + anon key
//   3. Replace mock supabaseClient with real @supabase/supabase-js
//   4. Run `supabase db push` with schema at bottom of file
//   5. Deploy to Vercel — set env vars NEXT_PUBLIC_SUPABASE_URL + ANON_KEY
// ============================================================

// ============================================================
// SITE CONFIG — edit this object for each client / deployment
// ============================================================
const SITE_CONFIG = {
  brand: {
    name: "Acme Corp",
    shortName: "AC",
    tagline: "Built to Last. Designed to Scale.",
    subTagline: "Enterprise solutions for the modern workforce.",
    description:
      "We help ambitious companies architect, build, and scale products that matter — combining deep technical expertise with sharp business instinct.",
    founded: "2015",
    location: "Singapore",
    phone: "+65 6000 0000",
    email: "hello@acmecorp.com",
    address: "1 Raffles Place, #20-00, Singapore 048616",
    industry: "Technology & Consulting",
  },

  theme: {
    bg:        "#09090f",   // void black
    surface:   "#0f0f1a",   // deep navy surface
    card:      "#141421",   // card background
    border:    "rgba(255,255,255,0.07)",
    accent:    "#6d28d9",   // violet — swap to retheme
    accentLit: "#8b5cf6",   // lighter violet for hover
    cyan:      "#22d3ee",   // complementary highlight
    text:      "#f8fafc",
    muted:     "#94a3b8",
    subtle:    "#334155",
  },

  nav: ["Services", "Work", "About", "Team", "Careers", "Contact"],

  stats: [
    { value: "200+", label: "Projects Shipped" },
    { value: "98%",  label: "Client Retention" },
    { value: "40+",  label: "Team Members" },
    { value: "12",   label: "Countries Served" },
  ],

  services: [
    {
      icon: "◈",
      title: "Product Engineering",
      desc: "End-to-end development of web and mobile products — from architecture through deployment, built for performance and scale.",
      tags: ["Next.js", "React Native", "Node.js", "PostgreSQL"],
    },
    {
      icon: "◉",
      title: "AI & Data Systems",
      desc: "Custom machine learning pipelines, LLM integrations, and data infrastructure that turns raw information into competitive advantage.",
      tags: ["LLMs", "RAG", "Python", "Supabase pgvector"],
    },
    {
      icon: "◐",
      title: "Cloud Architecture",
      desc: "Infrastructure design and migration to modern cloud platforms — scalable, observable, and cost-efficient from day one.",
      tags: ["AWS", "Vercel", "Terraform", "Docker"],
    },
    {
      icon: "◑",
      title: "Growth & Analytics",
      desc: "Data-driven growth frameworks: funnel instrumentation, A/B testing pipelines, and executive dashboards built on real-time data.",
      tags: ["PostHog", "Metabase", "dbt", "BigQuery"],
    },
    {
      icon: "◒",
      title: "Design Systems",
      desc: "Scalable component libraries and design tokens that unify brand expression across every product surface.",
      tags: ["Figma", "Storybook", "Radix UI", "Tailwind"],
    },
    {
      icon: "◓",
      title: "Technical Advisory",
      desc: "Fractional CTO and architecture review engagements — strategic guidance for critical technical decisions.",
      tags: ["Due Diligence", "Roadmapping", "Code Audit"],
    },
  ],

  work: [
    {
      label: "Fintech",
      title: "Real-time Payment Reconciliation Engine",
      desc: "Designed and built a sub-100ms reconciliation system processing 4M daily transactions for a Southeast Asian neobank.",
      metric: "4M txns/day",
      tags: ["PostgreSQL", "Redis", "Kafka"],
    },
    {
      label: "SaaS",
      title: "Multi-tenant Analytics Platform",
      desc: "Greenfield platform serving 300+ enterprise tenants with row-level security, custom dashboards, and SSO integration.",
      metric: "300+ tenants",
      tags: ["Next.js", "Supabase RLS", "Recharts"],
    },
    {
      label: "AI",
      title: "Document Intelligence System",
      desc: "RAG-powered document processing pipeline that extracts, classifies, and answers queries across 500K+ enterprise documents.",
      metric: "500K+ docs",
      tags: ["Claude API", "pgvector", "LangGraph"],
    },
  ],

  team: [
    { name: "Jordan Lee",    role: "Chief Executive Officer",     initials: "JL" },
    { name: "Sam Rivera",   role: "Chief Technology Officer",    initials: "SR" },
    { name: "Alex Chen",    role: "Head of Engineering",         initials: "AC" },
    { name: "Maya Patel",   role: "Head of Design",              initials: "MP" },
    { name: "Chris Tanaka", role: "Head of Data & AI",           initials: "CT" },
    { name: "Dana Brooks",  role: "Head of Client Success",      initials: "DB" },
  ],

  testimonials: [
    {
      quote: "They didn't just build what we asked for — they challenged our assumptions and delivered something far better.",
      author: "VP Engineering, Series B Fintech",
    },
    {
      quote: "Technical depth is rare at this level. They understood our architecture in days and were shipping improvements in a week.",
      author: "CTO, Enterprise SaaS",
    },
    {
      quote: "The AI system they built reduced our document review time by 80%. It paid for itself in the first month.",
      author: "COO, Legal Tech Startup",
    },
  ],

  careers: [
    { title: "Senior Full-Stack Engineer",    type: "Full-time", location: "Remote / Singapore", dept: "Engineering" },
    { title: "AI/ML Engineer",               type: "Full-time", location: "Remote",              dept: "AI & Data" },
    { title: "Product Designer",             type: "Full-time", location: "Singapore",           dept: "Design" },
    { title: "Solutions Architect",          type: "Contract",  location: "Remote / Hybrid",     dept: "Engineering" },
    { title: "Business Development Manager", type: "Full-time", location: "Singapore",           dept: "Growth" },
  ],

  social: {
    linkedin: "https://linkedin.com",
    twitter:  "https://twitter.com",
    github:   "https://github.com",
  },
};

// ============================================================
// SUPABASE CONFIG
// In production Next.js: use environment variables
//   NEXT_PUBLIC_SUPABASE_URL
//   NEXT_PUBLIC_SUPABASE_ANON_KEY
//
// Production init (replace mock below):
//   import { createClient } from '@supabase/supabase-js'
//   export const supabase = createClient(
//     process.env.NEXT_PUBLIC_SUPABASE_URL,
//     process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
//   )
//
// Database schema (run in Supabase SQL editor):
//   CREATE TABLE contacts (
//     id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
//     name text NOT NULL,
//     email text NOT NULL,
//     company text,
//     service text,
//     message text NOT NULL,
//     created_at timestamptz DEFAULT now()
//   );
//   CREATE TABLE applications (
//     id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
//     job_title text NOT NULL,
//     name text NOT NULL,
//     email text NOT NULL,
//     linkedin_url text,
//     message text,
//     created_at timestamptz DEFAULT now()
//   );
//   CREATE TABLE subscribers (
//     id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
//     email text UNIQUE NOT NULL,
//     created_at timestamptz DEFAULT now()
//   );
//   -- Enable RLS
//   ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
//   ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
//   ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
//   -- Allow anonymous inserts (public form submissions)
//   CREATE POLICY "allow_insert" ON contacts FOR INSERT WITH CHECK (true);
//   CREATE POLICY "allow_insert" ON applications FOR INSERT WITH CHECK (true);
//   CREATE POLICY "allow_insert" ON subscribers FOR INSERT WITH CHECK (true);
// ============================================================

const SUPABASE_CONFIG = {
  url:     "https://YOUR_PROJECT.supabase.co",
  anonKey: "YOUR_ANON_KEY",
};

// ── MOCK SUPABASE CLIENT (artifact only) ──────────────────────
// In production, replace with real createClient() from @supabase/supabase-js
// This mock simulates the exact same API surface
const mockDB = { contacts: [], applications: [], subscribers: [] };

const supabase = {
  from: (table) => ({
    insert: async (data) => {
      await new Promise(r => setTimeout(r, 800));
      if (Math.random() > 0.05) {
        mockDB[table]?.push({ ...data, id: crypto.randomUUID(), created_at: new Date().toISOString() });
        return { data: mockDB[table], error: null };
      }
      return { data: null, error: { message: "Insert failed" } };
    },
    select: async () => {
      await new Promise(r => setTimeout(r, 400));
      return { data: mockDB[table] || [], error: null };
    },
    upsert: async (data) => {
      await new Promise(r => setTimeout(r, 800));
      return { data, error: null };
    },
  }),
  auth: {
    _session: null,
    signInWithPassword: async ({ email, password }) => {
      await new Promise(r => setTimeout(r, 1000));
      if (email && password.length >= 6) {
        const session = { user: { email, id: crypto.randomUUID(), role: "authenticated" } };
        supabase.auth._session = session;
        supabase.auth._listeners.forEach(fn => fn("SIGNED_IN", session));
        return { data: session, error: null };
      }
      return { data: null, error: { message: "Invalid credentials" } };
    },
    signUp: async ({ email, password }) => {
      await new Promise(r => setTimeout(r, 1000));
      if (email && password.length >= 6) {
        return { data: { user: { email } }, error: null };
      }
      return { data: null, error: { message: "Password must be at least 6 characters" } };
    },
    signOut: async () => {
      supabase.auth._session = null;
      supabase.auth._listeners.forEach(fn => fn("SIGNED_OUT", null));
      return { error: null };
    },
    getSession: async () => ({ data: { session: supabase.auth._session } }),
    onAuthStateChange: (fn) => {
      supabase.auth._listeners = supabase.auth._listeners || [];
      supabase.auth._listeners.push(fn);
      return { data: { subscription: { unsubscribe: () => {} } } };
    },
    _listeners: [],
  },
};

// ============================================================
// DESIGN TOKENS
// ============================================================
const T = SITE_CONFIG.theme;

// ============================================================
// AUTH CONTEXT
// ============================================================
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => setSession(s));
    return () => subscription.unsubscribe();
  }, []);

  const signIn  = (email, password) => supabase.auth.signInWithPassword({ email, password });
  const signUp  = (email, password) => supabase.auth.signUp({ email, password });
  const signOut = () => supabase.auth.signOut();

  return (
    <AuthContext.Provider value={{ session, loading, signIn, signOut, signUp, user: session?.user }}>
      {children}
    </AuthContext.Provider>
  );
}

const useAuth = () => useContext(AuthContext);

// ============================================================
// HOOKS
// ============================================================
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
// PRIMITIVE UI COMPONENTS
// ============================================================
function Reveal({ children, delay = 0, y = 24 }) {
  const [ref, inView] = useInView();
  return (
    <div ref={ref} style={{
      opacity: inView ? 1 : 0,
      transform: inView ? "translateY(0)" : `translateY(${y}px)`,
      transition: `opacity 0.65s cubic-bezier(.16,1,.3,1) ${delay}s, transform 0.65s cubic-bezier(.16,1,.3,1) ${delay}s`,
    }}>
      {children}
    </div>
  );
}

function Label({ children }) {
  return (
    <p style={{
      fontFamily: "'Syne', sans-serif", fontWeight: 700,
      fontSize: "0.7rem", letterSpacing: "0.22em",
      textTransform: "uppercase", color: T.accent,
      marginBottom: "0.75rem",
    }}>{children}</p>
  );
}

function H2({ children }) {
  return (
    <h2 style={{
      fontFamily: "'Syne', sans-serif", fontWeight: 800,
      fontSize: "clamp(2rem, 4.5vw, 3.5rem)",
      lineHeight: 1.05, letterSpacing: "-0.025em",
      color: T.text, marginBottom: "1rem",
    }}>{children}</h2>
  );
}

function Muted({ children, style = {} }) {
  return (
    <p style={{
      fontFamily: "'DM Sans', sans-serif", color: T.muted,
      fontSize: "1rem", lineHeight: 1.75, ...style,
    }}>{children}</p>
  );
}

function Divider() {
  return <div style={{ width: 40, height: 2, background: `linear-gradient(90deg, ${T.accent}, ${T.cyan})`, marginBottom: "1.75rem", borderRadius: 2 }} />;
}

function Tag({ children }) {
  return (
    <span style={{
      display: "inline-block",
      background: `${T.accent}14`, color: T.accentLit,
      border: `1px solid ${T.accent}30`,
      borderRadius: 3, padding: "2px 9px",
      fontSize: "0.68rem", fontWeight: 600,
      letterSpacing: "0.06em", textTransform: "uppercase",
      marginRight: 6, marginTop: 6,
      fontFamily: "'DM Sans', sans-serif",
    }}>{children}</span>
  );
}

function Btn({ children, onClick, variant = "primary", size = "md", type = "button", disabled = false, full = false }) {
  const styles = {
    primary: { background: T.accent, color: "#fff", border: "none" },
    ghost:   { background: "transparent", color: T.text, border: `1px solid ${T.border}` },
    outline: { background: "transparent", color: T.accentLit, border: `1px solid ${T.accent}60` },
  };
  const sizes = {
    sm: { padding: "0.45rem 1rem", fontSize: "0.8rem" },
    md: { padding: "0.7rem 1.5rem", fontSize: "0.875rem" },
    lg: { padding: "0.9rem 2.25rem", fontSize: "1rem" },
  };
  return (
    <button type={type} onClick={onClick} disabled={disabled} style={{
      ...styles[variant], ...sizes[size],
      fontFamily: "'Syne', sans-serif", fontWeight: 700,
      letterSpacing: "0.05em", textTransform: "uppercase",
      borderRadius: 5, cursor: disabled ? "not-allowed" : "pointer",
      transition: "all 0.2s", opacity: disabled ? 0.5 : 1,
      width: full ? "100%" : "auto",
      display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
    }}
      onMouseOver={e => { if (!disabled) e.currentTarget.style.opacity = "0.85"; }}
      onMouseOut={e => { e.currentTarget.style.opacity = "1"; }}
    >{children}</button>
  );
}

function Input({ label, name, type = "text", value, onChange, placeholder, required, as = "input" }) {
  const shared = {
    width: "100%", background: T.surface, border: `1px solid ${T.border}`,
    borderRadius: 5, padding: "0.7rem 1rem", color: T.text,
    fontFamily: "'DM Sans', sans-serif", fontSize: "0.9rem",
    outline: "none", boxSizing: "border-box", transition: "border-color 0.2s",
    colorScheme: "dark",
  };
  return (
    <div style={{ marginBottom: "1.1rem" }}>
      <label style={{
        display: "block", color: T.muted, fontFamily: "'DM Sans', sans-serif",
        fontSize: "0.75rem", fontWeight: 500, letterSpacing: "0.08em",
        textTransform: "uppercase", marginBottom: "0.4rem",
      }}>{label}{required && <span style={{ color: T.accent }}> *</span>}</label>
      {as === "textarea"
        ? <textarea name={name} value={value} onChange={onChange} placeholder={placeholder} rows={4} required={required}
            style={{ ...shared, resize: "vertical" }}
            onFocus={e => e.target.style.borderColor = T.accent}
            onBlur={e => e.target.style.borderColor = T.border}
          />
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
      background: "rgba(0,0,0,0.7)", backdropFilter: "blur(6px)",
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: "1.5rem",
    }} onClick={onClose}>
      <div style={{
        background: T.card, borderRadius: 10,
        border: `1px solid ${T.border}`,
        boxShadow: `0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px ${T.accent}20`,
        padding: "2.5rem", maxWidth: 440, width: "100%",
        position: "relative",
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

function Toast({ message, type = "success" }) {
  const colors = { success: T.cyan, error: "#f87171" };
  return (
    <div style={{
      position: "fixed", bottom: "1.5rem", left: "50%",
      transform: "translateX(-50%)",
      background: T.card, border: `1px solid ${colors[type]}40`,
      borderLeft: `3px solid ${colors[type]}`,
      borderRadius: 6, padding: "0.9rem 1.5rem",
      boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
      zIndex: 9999, fontFamily: "'DM Sans', sans-serif",
      fontSize: "0.875rem", color: T.text,
      display: "flex", alignItems: "center", gap: "0.75rem",
      whiteSpace: "nowrap",
      animation: "toastIn 0.3s cubic-bezier(.16,1,.3,1)",
    }}>
      <span style={{ color: colors[type], fontWeight: 700 }}>
        {type === "success" ? "✓" : "✕"}
      </span>
      {message}
    </div>
  );
}

// ============================================================
// AUTH MODAL
// ============================================================
function AuthModal({ open, onClose }) {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState("signin"); // signin | signup
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handle = async () => {
    setLoading(true); setError(""); setSuccess("");
    const fn = mode === "signin" ? signIn : signUp;
    const { error, data } = await fn(form.email, form.password);
    setLoading(false);
    if (error) { setError(error.message); return; }
    if (mode === "signup") {
      setSuccess("Account created! Check your email to confirm.");
    } else {
      onClose();
    }
  };

  return (
    <Modal open={open} onClose={onClose}>
      <div style={{ marginBottom: "1.75rem" }}>
        <Label>Admin Access</Label>
        <h3 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: "1.5rem", color: T.text, marginBottom: "0.4rem" }}>
          {mode === "signin" ? "Sign In" : "Create Account"}
        </h3>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.85rem", color: T.muted }}>
          {mode === "signin"
            ? "Access the admin dashboard via Supabase Auth."
            : "Sign up with email — confirm via Supabase email flow."}
        </p>
      </div>

      <Input label="Email" type="email" value={form.email} onChange={set("email")} placeholder="you@company.com" required />
      <Input label="Password" type="password" value={form.password} onChange={set("password")} placeholder="••••••••" required />

      {error && <p style={{ color: "#f87171", fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", marginBottom: "1rem" }}>⚠ {error}</p>}
      {success && <p style={{ color: T.cyan, fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", marginBottom: "1rem" }}>✓ {success}</p>}

      <Btn onClick={handle} disabled={loading} full>
        {loading ? "Processing…" : mode === "signin" ? "Sign In" : "Create Account"}
      </Btn>

      <p style={{
        fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", color: T.muted,
        textAlign: "center", marginTop: "1.25rem",
      }}>
        {mode === "signin" ? "No account? " : "Already have one? "}
        <button onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setError(""); setSuccess(""); }}
          style={{ background: "none", border: "none", color: T.accentLit, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem" }}>
          {mode === "signin" ? "Sign up" : "Sign in"}
        </button>
      </p>

      <div style={{ marginTop: "1.5rem", padding: "1rem", background: T.surface, borderRadius: 5, border: `1px solid ${T.border}` }}>
        <p style={{ fontFamily: "'DM Sans', monospace", fontSize: "0.72rem", color: T.subtle }}>
          // Production: Supabase handles email confirmation,<br />
          // OAuth (Google, GitHub), and magic link flows.<br />
          // Session persisted via httpOnly cookies (Next.js SSR).
        </p>
      </div>
    </Modal>
  );
}

// ============================================================
// APPLY MODAL (Career Applications → Supabase)
// ============================================================
function ApplyModal({ open, onClose, job }) {
  const [form, setForm] = useState({ name: "", email: "", linkedin_url: "", message: "" });
  const [status, setStatus] = useState("idle"); // idle | loading | success | error

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const submit = async () => {
    setStatus("loading");
    const { error } = await supabase.from("applications").insert({
      job_title: job,
      name: form.name,
      email: form.email,
      linkedin_url: form.linkedin_url,
      message: form.message,
    });
    setStatus(error ? "error" : "success");
  };

  if (status === "success") return (
    <Modal open={open} onClose={() => { onClose(); setStatus("idle"); setForm({ name: "", email: "", linkedin_url: "", message: "" }); }}>
      <div style={{ textAlign: "center", padding: "1rem 0" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎯</div>
        <h3 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: "1.4rem", color: T.text, marginBottom: "0.75rem" }}>
          Application Received
        </h3>
        <Muted>Stored in Supabase <code style={{ color: T.cyan }}>applications</code> table. We'll be in touch within 3 business days.</Muted>
        <div style={{ marginTop: "1.5rem" }}>
          <Btn onClick={() => { onClose(); setStatus("idle"); }}>Close</Btn>
        </div>
      </div>
    </Modal>
  );

  return (
    <Modal open={open} onClose={onClose}>
      <Label>Apply Now</Label>
      <h3 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: "1.25rem", color: T.text, marginBottom: "0.4rem" }}>{job}</h3>
      <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", color: T.muted, marginBottom: "1.5rem" }}>
        Submission goes to <code style={{ color: T.cyan }}>supabase.from("applications").insert()</code>
      </p>

      <Input label="Full Name" value={form.name} onChange={set("name")} placeholder="Your name" required />
      <Input label="Email" type="email" value={form.email} onChange={set("email")} placeholder="you@email.com" required />
      <Input label="LinkedIn URL" value={form.linkedin_url} onChange={set("linkedin_url")} placeholder="https://linkedin.com/in/..." />
      <Input label="Cover Note" as="textarea" value={form.message} onChange={set("message")} placeholder="Why you're a great fit..." />

      {status === "error" && <p style={{ color: "#f87171", fontSize: "0.8rem", fontFamily: "'DM Sans', sans-serif", marginBottom: "0.75rem" }}>Submission failed. Try again.</p>}

      <Btn onClick={submit} disabled={status === "loading" || !form.name || !form.email} full>
        {status === "loading" ? "Submitting…" : "Submit Application"}
      </Btn>
    </Modal>
  );
}

// ============================================================
// NAV
// ============================================================
function Nav({ onAuthOpen }) {
  const scrollY = useScrollY();
  const { user, signOut } = useAuth();
  const scrolled = scrollY > 50;

  const scrollTo = useCallback((id) => {
    document.getElementById(id.toLowerCase())?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return (
    <nav style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 999,
      background: scrolled ? `${T.bg}f0` : "transparent",
      backdropFilter: scrolled ? "blur(12px)" : "none",
      borderBottom: scrolled ? `1px solid ${T.border}` : "1px solid transparent",
      transition: "all 0.3s ease",
    }}>
      <div style={{
        maxWidth: 1280, margin: "0 auto", padding: "0 1.5rem",
        display: "flex", alignItems: "center", justifyContent: "space-between", height: 64,
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          <div style={{
            width: 34, height: 34, borderRadius: 6,
            background: `linear-gradient(135deg, ${T.accent}, ${T.cyan})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'Syne', sans-serif", fontWeight: 800,
            color: "#fff", fontSize: "0.8rem", letterSpacing: "0.02em",
          }}>
            {SITE_CONFIG.brand.shortName}
          </div>
          <span style={{
            fontFamily: "'Syne', sans-serif", fontWeight: 700,
            fontSize: "0.95rem", color: T.text,
          }}>
            {SITE_CONFIG.brand.name}
          </span>
        </div>

        {/* Links — hidden on mobile for brevity */}
        <div style={{ display: "flex", alignItems: "center", gap: "1.75rem" }}>
          {SITE_CONFIG.nav.map(item => (
            <button key={item} onClick={() => scrollTo(item)} style={{
              background: "none", border: "none", cursor: "pointer",
              color: T.muted, fontFamily: "'DM Sans', sans-serif",
              fontSize: "0.875rem", fontWeight: 500, letterSpacing: "0.01em",
              transition: "color 0.2s", padding: "4px 0",
            }}
              onMouseOver={e => e.target.style.color = T.text}
              onMouseOut={e => e.target.style.color = T.muted}
            >{item}</button>
          ))}
        </div>

        {/* Auth + CTA */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {user ? (
            <>
              <span style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: "0.75rem",
                color: T.cyan, background: `${T.cyan}12`,
                border: `1px solid ${T.cyan}30`, borderRadius: 20,
                padding: "3px 10px",
              }}>
                ● {user.email}
              </span>
              <Btn variant="ghost" size="sm" onClick={signOut}>Sign Out</Btn>
            </>
          ) : (
            <Btn variant="ghost" size="sm" onClick={onAuthOpen}>Admin</Btn>
          )}
          <Btn size="sm" onClick={() => scrollTo("Contact")}>Get Started</Btn>
        </div>
      </div>
    </nav>
  );
}

// ============================================================
// HERO
// ============================================================
function Hero() {
  return (
    <section id="hero" style={{
      minHeight: "100vh", background: T.bg,
      display: "flex", alignItems: "center",
      position: "relative", overflow: "hidden",
    }}>
      {/* Dot grid */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `radial-gradient(${T.subtle}55 1px, transparent 1px)`,
        backgroundSize: "28px 28px",
        maskImage: "radial-gradient(ellipse 70% 80% at 50% 50%, black 30%, transparent 100%)",
      }} />

      {/* Gradient orbs */}
      <div style={{ position: "absolute", top: "15%", right: "8%", width: 500, height: 500, background: `radial-gradient(circle, ${T.accent}1a 0%, transparent 65%)`, borderRadius: "50%", pointerEvents: "none" }} />
      <div style={{ position: "absolute", bottom: "5%", left: "-5%", width: 400, height: 400, background: `radial-gradient(circle, ${T.cyan}12 0%, transparent 65%)`, borderRadius: "50%", pointerEvents: "none" }} />

      {/* Diagonal accent line */}
      <div style={{
        position: "absolute", top: 0, right: "30%",
        width: 1, height: "40vh",
        background: `linear-gradient(180deg, transparent, ${T.accent}40, transparent)`,
      }} />

      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "7rem 1.5rem 5rem", position: "relative", zIndex: 1, width: "100%" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "4rem", alignItems: "center" }}>
          {/* Left — headline */}
          <div>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: "0.5rem",
              background: `${T.accent}15`, border: `1px solid ${T.accent}30`,
              borderRadius: 20, padding: "4px 14px 4px 10px",
              marginBottom: "2rem",
              animation: "fadeUp 0.5s ease both",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: T.cyan, display: "inline-block" }} />
              <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.75rem", color: T.cyan, fontWeight: 500 }}>
                Est. {SITE_CONFIG.brand.founded} · {SITE_CONFIG.brand.location}
              </span>
            </div>

            <h1 style={{
              fontFamily: "'Syne', sans-serif", fontWeight: 800,
              fontSize: "clamp(2.75rem, 6vw, 5.25rem)",
              lineHeight: 1.0, letterSpacing: "-0.03em",
              color: T.text, marginBottom: "1.5rem",
              animation: "fadeUp 0.6s ease 0.1s both",
            }}>
              {SITE_CONFIG.brand.tagline}
            </h1>

            <p style={{
              fontFamily: "'DM Sans', sans-serif", color: T.muted,
              fontSize: "clamp(1rem, 1.4vw, 1.15rem)", lineHeight: 1.75,
              maxWidth: 500, marginBottom: "2.5rem",
              animation: "fadeUp 0.6s ease 0.2s both",
            }}>
              {SITE_CONFIG.brand.description}
            </p>

            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", animation: "fadeUp 0.6s ease 0.3s both" }}>
              <Btn size="lg" onClick={() => document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" })}>
                Start a Project
              </Btn>
              <Btn variant="ghost" size="lg" onClick={() => document.getElementById("work")?.scrollIntoView({ behavior: "smooth" })}>
                View Our Work →
              </Btn>
            </div>
          </div>

          {/* Right — stats card stack */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1px", animation: "fadeUp 0.7s ease 0.35s both" }}>
            {SITE_CONFIG.stats.map((s, i) => (
              <div key={i} style={{
                background: i % 2 === 0 ? T.surface : T.card,
                padding: "1.75rem 2rem",
                display: "flex", alignItems: "center", justifyContent: "space-between",
                borderRadius: i === 0 ? "8px 8px 0 0" : i === SITE_CONFIG.stats.length - 1 ? "0 0 8px 8px" : 0,
                border: `1px solid ${T.border}`,
                borderBottom: i < SITE_CONFIG.stats.length - 1 ? "none" : `1px solid ${T.border}`,
              }}>
                <span style={{ fontFamily: "'DM Sans', sans-serif", color: T.muted, fontSize: "0.875rem" }}>
                  {s.label}
                </span>
                <span style={{
                  fontFamily: "'Syne', sans-serif", fontWeight: 800,
                  fontSize: "2rem", color: T.text,
                  background: `linear-gradient(135deg, ${T.text}, ${T.accentLit})`,
                  WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                }}>
                  {s.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ============================================================
// SERVICES
// ============================================================
function Services() {
  return (
    <section id="services" style={{ background: T.surface, padding: "7rem 1.5rem" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <Reveal>
          <Label>What We Do</Label>
          <H2>Services</H2>
          <Divider />
          <Muted style={{ maxWidth: 520, marginBottom: "3.5rem" }}>
            From zero to production — we work across the full stack of product and data problems.
          </Muted>
        </Reveal>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))",
          gap: "1px",
          background: T.border,
          borderRadius: 8, overflow: "hidden",
        }}>
          {SITE_CONFIG.services.map((s, i) => (
            <Reveal key={i} delay={i * 0.06}>
              <div style={{
                background: T.card, padding: "2.25rem",
                transition: "background 0.25s",
                height: "100%",
              }}
                onMouseOver={e => e.currentTarget.style.background = `${T.accent}0a`}
                onMouseOut={e => e.currentTarget.style.background = T.card}
              >
                <div style={{
                  width: 44, height: 44, borderRadius: 8,
                  background: `${T.accent}15`,
                  border: `1px solid ${T.accent}25`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "1.4rem", marginBottom: "1.25rem",
                  color: T.accent,
                }}>
                  {s.icon}
                </div>
                <h3 style={{
                  fontFamily: "'Syne', sans-serif", fontWeight: 700,
                  fontSize: "1.15rem", color: T.text,
                  marginBottom: "0.75rem", lineHeight: 1.3,
                }}>
                  {s.title}
                </h3>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif", color: T.muted,
                  fontSize: "0.875rem", lineHeight: 1.7, marginBottom: "1.25rem",
                }}>
                  {s.desc}
                </p>
                <div>{s.tags.map(t => <Tag key={t}>{t}</Tag>)}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// WORK / CASE STUDIES
// ============================================================
function Work() {
  return (
    <section id="work" style={{ background: T.bg, padding: "7rem 1.5rem" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <Reveal>
          <Label>Case Studies</Label>
          <H2>Selected Work</H2>
          <Divider />
        </Reveal>

        <div style={{ display: "flex", flexDirection: "column", gap: "1px", marginTop: "2rem" }}>
          {SITE_CONFIG.work.map((w, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <div style={{
                background: T.card,
                border: `1px solid ${T.border}`,
                borderRadius: i === 0 ? "8px 8px 0 0" : i === SITE_CONFIG.work.length - 1 ? "0 0 8px 8px" : 0,
                borderBottom: i < SITE_CONFIG.work.length - 1 ? "none" : `1px solid ${T.border}`,
                padding: "2.25rem 2.5rem",
                display: "grid",
                gridTemplateColumns: "auto 1fr auto",
                alignItems: "center",
                gap: "2.5rem",
                transition: "background 0.2s",
                cursor: "default",
              }}
                onMouseOver={e => e.currentTarget.style.background = `${T.accent}08`}
                onMouseOut={e => e.currentTarget.style.background = T.card}
              >
                <div style={{
                  fontFamily: "'Syne', sans-serif", fontWeight: 800,
                  fontSize: "clamp(1.75rem, 3vw, 2.5rem)",
                  color: `${T.subtle}`,
                  minWidth: 32, textAlign: "center", lineHeight: 1,
                }}>
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div>
                  <p style={{
                    color: T.accent, fontFamily: "'DM Sans', sans-serif",
                    fontSize: "0.75rem", fontWeight: 600,
                    letterSpacing: "0.15em", textTransform: "uppercase",
                    marginBottom: "0.5rem",
                  }}>
                    {w.label}
                  </p>
                  <h3 style={{
                    fontFamily: "'Syne', sans-serif", fontWeight: 700,
                    fontSize: "1.25rem", color: T.text,
                    marginBottom: "0.5rem",
                  }}>
                    {w.title}
                  </h3>
                  <p style={{ fontFamily: "'DM Sans', sans-serif", color: T.muted, fontSize: "0.875rem", lineHeight: 1.6 }}>
                    {w.desc}
                  </p>
                  <div style={{ marginTop: "0.75rem" }}>{w.tags.map(t => <Tag key={t}>{t}</Tag>)}</div>
                </div>
                <div style={{
                  fontFamily: "'Syne', sans-serif", fontWeight: 800,
                  fontSize: "1.25rem", color: T.cyan,
                  whiteSpace: "nowrap", textAlign: "right",
                }}>
                  {w.metric}
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
// ABOUT
// ============================================================
function About() {
  return (
    <section id="about" style={{ background: T.surface, padding: "7rem 1.5rem" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "5rem", alignItems: "center" }}>
        {/* Left — text */}
        <Reveal>
          <Label>Our Story</Label>
          <H2>Who We Are</H2>
          <Divider />
          <Muted style={{ marginBottom: "1.5rem" }}>
            Founded in {SITE_CONFIG.brand.founded} in {SITE_CONFIG.brand.location}, we set out to close the gap between
            engineering craft and business outcomes. Too many companies were building the wrong things
            quickly. We help build the right things — reliably.
          </Muted>
          <Muted style={{ marginBottom: "2rem" }}>
            We operate as an embedded partner, not a vendor — sitting inside your roadmap, your standups,
            and your architecture decisions until the problem is solved.
          </Muted>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            {["Remote-first", "Engineering-led", "Product-focused", "Outcome-driven"].map(t => <Tag key={t}>{t}</Tag>)}
          </div>
        </Reveal>

        {/* Right — value props */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {[
            { n: "01", t: "Depth over breadth", d: "We go deep on a focused set of technologies rather than spreading thin across every stack." },
            { n: "02", t: "Transparent by default", d: "Weekly async updates, shared Notion workspaces, and no black-box work. You always know where things stand." },
            { n: "03", t: "Ship, then improve", d: "We favour working software over perfect architecture. Iterate with data, not assumptions." },
          ].map((v, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <div style={{
                background: T.card, border: `1px solid ${T.border}`,
                borderRadius: 8, padding: "1.5rem",
                display: "flex", gap: "1.25rem", alignItems: "flex-start",
              }}>
                <span style={{
                  fontFamily: "'Syne', sans-serif", fontWeight: 800,
                  fontSize: "0.8rem", color: T.accent, minWidth: 24,
                }}>{v.n}</span>
                <div>
                  <p style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.95rem", marginBottom: "0.4rem" }}>{v.t}</p>
                  <p style={{ fontFamily: "'DM Sans', sans-serif", color: T.muted, fontSize: "0.85rem", lineHeight: 1.6 }}>{v.d}</p>
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
// TEAM
// ============================================================
function Team() {
  return (
    <section id="team" style={{ background: T.bg, padding: "7rem 1.5rem" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <Reveal>
          <Label>People</Label>
          <H2>The Team</H2>
          <Divider />
        </Reveal>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "1px", background: T.border,
          borderRadius: 8, overflow: "hidden",
          marginTop: "2.5rem",
        }}>
          {SITE_CONFIG.team.map((p, i) => (
            <Reveal key={i} delay={i * 0.06}>
              <div style={{
                background: T.card, padding: "2rem 1.5rem",
                textAlign: "center",
                transition: "background 0.2s",
              }}
                onMouseOver={e => e.currentTarget.style.background = `${T.accent}0a`}
                onMouseOut={e => e.currentTarget.style.background = T.card}
              >
                <div style={{
                  width: 60, height: 60, borderRadius: "50%",
                  background: `linear-gradient(135deg, ${T.accent}30, ${T.cyan}20)`,
                  border: `2px solid ${T.accent}30`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 1rem",
                  fontFamily: "'Syne', sans-serif", fontWeight: 800,
                  fontSize: "1rem", color: T.accentLit,
                }}>
                  {p.initials}
                </div>
                <p style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.95rem", marginBottom: "0.3rem" }}>
                  {p.name}
                </p>
                <p style={{ fontFamily: "'DM Sans', sans-serif", color: T.muted, fontSize: "0.8rem" }}>
                  {p.role}
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
// TESTIMONIALS
// ============================================================
function Testimonials() {
  const [active, setActive] = useState(0);
  const t = SITE_CONFIG.testimonials[active];

  return (
    <section style={{ background: T.surface, padding: "6rem 1.5rem", borderTop: `1px solid ${T.border}` }}>
      <div style={{ maxWidth: 860, margin: "0 auto", textAlign: "center" }}>
        <Reveal>
          <Label>What Clients Say</Label>
          <div style={{
            marginTop: "2rem",
            background: T.card, border: `1px solid ${T.border}`,
            borderRadius: 12, padding: "3rem 3rem 2.5rem",
            position: "relative",
          }}>
            <div style={{
              fontSize: "4rem", lineHeight: 1,
              color: T.accent, fontFamily: "'Syne', sans-serif",
              position: "absolute", top: "1.5rem", left: "2rem",
              opacity: 0.4,
            }}>"</div>
            <p style={{
              fontFamily: "'Syne', sans-serif", fontWeight: 600,
              fontSize: "clamp(1.1rem, 2vw, 1.4rem)", color: T.text,
              lineHeight: 1.5, marginBottom: "1.5rem",
              fontStyle: "italic",
            }}>
              {t.quote}
            </p>
            <p style={{ fontFamily: "'DM Sans', sans-serif", color: T.muted, fontSize: "0.85rem" }}>
              — {t.author}
            </p>

            {/* Dots */}
            <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", marginTop: "1.75rem" }}>
              {SITE_CONFIG.testimonials.map((_, i) => (
                <button key={i} onClick={() => setActive(i)} style={{
                  width: i === active ? 24 : 8, height: 8,
                  borderRadius: 4, border: "none", cursor: "pointer",
                  background: i === active ? T.accent : T.subtle,
                  transition: "all 0.3s",
                }} />
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

// ============================================================
// CAREERS (with Supabase apply flow)
// ============================================================
function Careers() {
  const [applyJob, setApplyJob] = useState(null);

  return (
    <section id="careers" style={{ background: T.bg, padding: "7rem 1.5rem" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <Reveal>
          <Label>Join Us</Label>
          <H2>Open Roles</H2>
          <Divider />
          <Muted style={{ maxWidth: 500, marginBottom: "3rem" }}>
            We're always looking for people who combine technical depth with clear thinking.
            Applications go straight to Supabase — no ATS.
          </Muted>
        </Reveal>

        {/* Tech indicator */}
        <Reveal>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "0.75rem",
            background: T.surface, border: `1px solid ${T.border}`,
            borderRadius: 6, padding: "0.6rem 1rem",
            marginBottom: "2rem",
          }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: T.cyan, display: "inline-block" }} />
            <code style={{ fontFamily: "'DM Mono', monospace", fontSize: "0.75rem", color: T.muted }}>
              supabase.from(<span style={{ color: T.cyan }}>"applications"</span>).insert(payload)
            </code>
          </div>
        </Reveal>

        <div style={{ display: "flex", flexDirection: "column", gap: "1px", background: T.border, borderRadius: 8, overflow: "hidden" }}>
          {SITE_CONFIG.careers.map((job, i) => (
            <Reveal key={i} delay={i * 0.06}>
              <div style={{
                background: T.card, padding: "1.5rem 2rem",
                display: "flex", alignItems: "center",
                justifyContent: "space-between", flexWrap: "wrap", gap: "1rem",
                transition: "background 0.2s",
              }}
                onMouseOver={e => e.currentTarget.style.background = `${T.accent}08`}
                onMouseOut={e => e.currentTarget.style.background = T.card}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.4rem" }}>
                    <h4 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: "1.05rem", color: T.text }}>{job.title}</h4>
                    <Tag>{job.dept}</Tag>
                  </div>
                  <div style={{ display: "flex", gap: "1.25rem" }}>
                    <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", color: T.muted }}>📍 {job.location}</span>
                    <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", color: job.type === "Full-time" ? T.cyan : T.accentLit }}>
                      {job.type === "Full-time" ? "●" : "◑"} {job.type}
                    </span>
                  </div>
                </div>
                <Btn variant="outline" size="sm" onClick={() => setApplyJob(job.title)}>
                  Apply →
                </Btn>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.2}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.85rem", color: T.muted, marginTop: "1.5rem" }}>
            Don't see a fit? Send a speculative application to{" "}
            <a href={`mailto:${SITE_CONFIG.brand.email}`} style={{ color: T.accentLit, textDecoration: "none" }}>
              {SITE_CONFIG.brand.email}
            </a>
          </p>
        </Reveal>
      </div>

      <ApplyModal open={!!applyJob} onClose={() => setApplyJob(null)} job={applyJob} />
    </section>
  );
}

// ============================================================
// CONTACT (form → Supabase contacts table)
// ============================================================
function Contact() {
  const [form, setForm] = useState({ name: "", email: "", company: "", service: "", message: "" });
  const [status, setStatus] = useState("idle");
  const [toast, setToast] = useState(null);

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const submit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    const { error } = await supabase.from("contacts").insert({
      name: form.name,
      email: form.email,
      company: form.company || null,
      service: form.service || null,
      message: form.message,
    });
    if (error) {
      setStatus("idle");
      showToast("Submission failed. Please try again.", "error");
    } else {
      setStatus("success");
      showToast("Message sent — we'll respond within 1 business day.");
    }
  };

  return (
    <section id="contact" style={{ background: T.surface, padding: "7rem 1.5rem" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1.1fr", gap: "5rem", alignItems: "start" }}>

        {/* Left — info */}
        <Reveal>
          <Label>Get In Touch</Label>
          <H2>Start a Conversation</H2>
          <Divider />
          <Muted style={{ marginBottom: "2.5rem" }}>
            Tell us about your project. We'll reply with a clear assessment and, where it makes sense, a proposal.
          </Muted>

          {[
            { icon: "✉", label: "Email", val: SITE_CONFIG.brand.email },
            { icon: "📞", label: "Phone", val: SITE_CONFIG.brand.phone },
            { icon: "📍", label: "Address", val: SITE_CONFIG.brand.address },
          ].map((c, i) => (
            <Reveal key={i} delay={i * 0.07}>
              <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start", marginBottom: "1.5rem" }}>
                <div style={{
                  width: 38, height: 38, background: `${T.accent}12`,
                  border: `1px solid ${T.accent}25`, borderRadius: 6,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "0.9rem", flexShrink: 0,
                }}>{c.icon}</div>
                <div>
                  <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.7rem", color: T.muted, textTransform: "uppercase", letterSpacing: "0.12em", marginBottom: "0.2rem" }}>{c.label}</p>
                  <p style={{ fontFamily: "'DM Sans', sans-serif", color: T.text, fontSize: "0.9rem" }}>{c.val}</p>
                </div>
              </div>
            </Reveal>
          ))}

          {/* Supabase badge */}
          <Reveal delay={0.25}>
            <div style={{
              marginTop: "2rem", padding: "1rem 1.25rem",
              background: T.card, border: `1px solid ${T.border}`,
              borderRadius: 8,
            }}>
              <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.75rem", color: T.muted, marginBottom: "0.3rem" }}>
                Powered by Supabase
              </p>
              <code style={{ fontFamily: "'DM Mono', monospace", fontSize: "0.72rem", color: T.subtle, display: "block" }}>
                contacts table · RLS enabled · anon insert policy
              </code>
            </div>
          </Reveal>
        </Reveal>

        {/* Right — form */}
        <Reveal delay={0.12}>
          {status === "success" ? (
            <div style={{
              background: T.card, border: `1px solid ${T.cyan}30`,
              borderRadius: 10, padding: "3rem 2.5rem", textAlign: "center",
            }}>
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>✅</div>
              <h3 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: "1.5rem", color: T.text, marginBottom: "0.75rem" }}>
                Message Received
              </h3>
              <Muted>Stored in Supabase. Expect a reply within 1 business day.</Muted>
              <div style={{ marginTop: "1.5rem" }}>
                <Btn variant="ghost" onClick={() => { setStatus("idle"); setForm({ name: "", email: "", company: "", service: "", message: "" }); }}>
                  Send Another
                </Btn>
              </div>
            </div>
          ) : (
            <form onSubmit={submit} style={{
              background: T.card, border: `1px solid ${T.border}`,
              borderRadius: 10, padding: "2.5rem",
            }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 1rem" }}>
                <Input label="Full Name" name="name" value={form.name} onChange={set("name")} placeholder="Your name" required />
                <Input label="Email" name="email" type="email" value={form.email} onChange={set("email")} placeholder="you@company.com" required />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 1rem" }}>
                <Input label="Company" name="company" value={form.company} onChange={set("company")} placeholder="Acme Inc." />
                <div style={{ marginBottom: "1.1rem" }}>
                  <label style={{
                    display: "block", color: T.muted,
                    fontFamily: "'DM Sans', sans-serif", fontSize: "0.75rem",
                    fontWeight: 500, letterSpacing: "0.08em",
                    textTransform: "uppercase", marginBottom: "0.4rem",
                  }}>Service</label>
                  <select value={form.service} onChange={set("service")} style={{
                    width: "100%", background: T.surface,
                    border: `1px solid ${T.border}`, borderRadius: 5,
                    padding: "0.7rem 1rem", color: form.service ? T.text : T.muted,
                    fontFamily: "'DM Sans', sans-serif", fontSize: "0.9rem",
                    outline: "none", boxSizing: "border-box", colorScheme: "dark",
                  }}>
                    <option value="">Select a service…</option>
                    {SITE_CONFIG.services.map(s => <option key={s.title} value={s.title}>{s.title}</option>)}
                  </select>
                </div>
              </div>
              <Input label="Message" name="message" as="textarea" value={form.message} onChange={set("message")} placeholder="Tell us about your project, timeline, and goals…" required />
              <Btn type="submit" disabled={status === "loading"} full size="lg">
                {status === "loading" ? "Sending…" : "Send Message"}
              </Btn>
            </form>
          )}
        </Reveal>
      </div>

      {toast && <Toast message={toast.msg} type={toast.type} />}
    </section>
  );
}

// ============================================================
// FOOTER
// ============================================================
function Footer({ onAuthOpen }) {
  const { user, signOut } = useAuth();
  const year = new Date().getFullYear();

  return (
    <footer style={{
      background: T.bg, borderTop: `1px solid ${T.border}`,
      padding: "3rem 1.5rem",
    }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "2rem", marginBottom: "3rem" }}>

          {/* Brand */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: "0.75rem" }}>
              <div style={{
                width: 30, height: 30, borderRadius: 5,
                background: `linear-gradient(135deg, ${T.accent}, ${T.cyan})`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "'Syne', sans-serif", fontWeight: 800,
                color: "#fff", fontSize: "0.7rem",
              }}>{SITE_CONFIG.brand.shortName}</div>
              <span style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.9rem" }}>
                {SITE_CONFIG.brand.name}
              </span>
            </div>
            <p style={{ fontFamily: "'DM Sans', sans-serif", color: T.muted, fontSize: "0.8rem", maxWidth: 240, lineHeight: 1.6 }}>
              {SITE_CONFIG.brand.subTagline}
            </p>
          </div>

          {/* Nav columns */}
          <div style={{ display: "flex", gap: "3rem", flexWrap: "wrap" }}>
            <div>
              <p style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.8rem", marginBottom: "1rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Sitemap
              </p>
              {SITE_CONFIG.nav.map(item => (
                <button key={item} onClick={() => document.getElementById(item.toLowerCase())?.scrollIntoView({ behavior: "smooth" })} style={{
                  display: "block", background: "none", border: "none",
                  color: T.muted, fontFamily: "'DM Sans', sans-serif",
                  fontSize: "0.85rem", cursor: "pointer", marginBottom: "0.6rem",
                  textAlign: "left",
                }}
                  onMouseOver={e => e.target.style.color = T.text}
                  onMouseOut={e => e.target.style.color = T.muted}
                >{item}</button>
              ))}
            </div>
            <div>
              <p style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, color: T.text, fontSize: "0.8rem", marginBottom: "1rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Connect
              </p>
              {[
                { label: "LinkedIn", href: SITE_CONFIG.social.linkedin },
                { label: "Twitter / X", href: SITE_CONFIG.social.twitter },
                { label: "GitHub", href: SITE_CONFIG.social.github },
              ].map(s => (
                <a key={s.label} href={s.href} target="_blank" rel="noopener noreferrer" style={{
                  display: "block", color: T.muted, fontFamily: "'DM Sans', sans-serif",
                  fontSize: "0.85rem", textDecoration: "none", marginBottom: "0.6rem",
                  transition: "color 0.2s",
                }}
                  onMouseOver={e => e.target.style.color = T.text}
                  onMouseOut={e => e.target.style.color = T.muted}
                >{s.label}</a>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          flexWrap: "wrap", gap: "1rem",
          borderTop: `1px solid ${T.border}`, paddingTop: "1.5rem",
        }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "0.8rem", color: T.muted }}>
            © {year} {SITE_CONFIG.brand.name}. All rights reserved.
          </p>

          {/* Stack badge */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            {["Next.js", "Supabase", "Vercel"].map(s => (
              <span key={s} style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: "0.7rem",
                color: T.subtle, background: T.surface,
                border: `1px solid ${T.border}`, borderRadius: 3,
                padding: "2px 8px",
              }}>{s}</span>
            ))}
          </div>

          {/* Admin link */}
          <button onClick={user ? signOut : onAuthOpen} style={{
            background: "none", border: "none", cursor: "pointer",
            color: T.subtle, fontFamily: "'DM Sans', sans-serif",
            fontSize: "0.75rem", transition: "color 0.2s",
          }}
            onMouseOver={e => e.target.style.color = T.muted}
            onMouseOut={e => e.target.style.color = T.subtle}
          >
            {user ? `⊙ Signed in as ${user.email}` : "⊙ Admin"}
          </button>
        </div>
      </div>
    </footer>
  );
}

// ============================================================
// ROOT APP
// ============================================================
export default function App() {
  const [authOpen, setAuthOpen] = useState(false);

  return (
    <AuthProvider>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&family=DM+Mono&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { background: ${T.bg}; color: ${T.text}; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
        ::selection { background: ${T.accent}; color: #fff; }
        input, textarea, select { color-scheme: dark; }
        input::placeholder, textarea::placeholder { color: ${T.subtle}; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes toastIn { from { opacity: 0; transform: translate(-50%, 12px); } to { opacity: 1; transform: translate(-50%, 0); } }
        @media (max-width: 900px) {
          section > div { grid-template-columns: 1fr !important; gap: 2.5rem !important; }
        }
        @media (max-width: 640px) {
          nav > div > div:nth-child(2) { display: none !important; }
        }
      `}</style>

      <Nav onAuthOpen={() => setAuthOpen(true)} />
      <Hero />
      <Services />
      <Work />
      <About />
      <Team />
      <Testimonials />
      <Careers />
      <Contact />
      <Footer onAuthOpen={() => setAuthOpen(true)} />
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </AuthProvider>
  );
}
