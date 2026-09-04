/* theme-sisc — Southville International School and Colleges
 * Merge into the project's tailwind.config.js `theme.extend`.
 * Source: post-mtg-08072026/Project_Plan_Details.pptx (extracted 2026-08-19).
 */

module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          100: '#F5F3F6',
          200: '#E4DEED',
          300: '#B49ED1',
          400: '#7449AB',
          500: '#4B2F70',
          600: '#3C255B',
          700: '#301D49',
          800: '#221433',
          900: '#160D21',
          DEFAULT: '#4B2F70',
        },
        primaryLit: '#6A3D9E',
        accent: { DEFAULT: '#D2650F', text: '#AB520C' },
        laurel: { DEFAULT: '#3C875A', lit: '#60B158', text: '#357850' },
        maroon: '#8D2725',
        indigo: { display: '#410BDB' },
        alert: '#AE1029',
        bg: '#FFF8F9',
        surface: '#FFFFFF',
        card: '#FDEEF0',
        border: '#E2C3CA',
        text: '#1E181B',
        muted: { DEFAULT: '#7C6F75', text: '#71656B' },
        subtle: '#958389',
        tint: { violet: '#D9B9EE', violet2: '#C79FE4', blush: '#F6D6DC' },
      },
      fontFamily: {
        display: ['Georgia', 'Gelasio', 'Times New Roman', 'serif'],
        body: ['Arial', 'Arimo', 'Helvetica', 'system-ui', 'sans-serif'],
        mono: ['Courier New', 'Cousine', 'monospace'],
      },
      borderRadius: {
        xs: '0px',
        sm: '0px',
        md: '2px',
        lg: '4px',
        xl: '8px',
      },
      boxShadow: {
        xs: '0 1px 2px rgba(75, 47, 112, 0.05)',
        sm: '0 2px 8px rgba(75, 47, 112, 0.06)',
        md: '0 4px 16px rgba(75, 47, 112, 0.08)',
        lg: '0 8px 32px rgba(75, 47, 112, 0.10)',
        cta: '0 4px 20px rgba(210, 101, 15, 0.40)',
      },
      letterSpacing: {
        kicker: '0.1em',
        numeral: '-0.01em',
      },
    },
  },
};
