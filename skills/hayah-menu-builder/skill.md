---
name: hayah-menu-builder
description: Generates polished, self-contained interactive cooking-menu / recipe HTML files branded with the Hayah-AI Classic theme and logo. Use this skill whenever the user wants to turn a dish, recipe, restaurant menu item, or food photo into a shareable interactive recipe page — especially when they mention "menu", "recipe card", "cooking", "dish", or ask to "save this recipe to HTML/an interactive file" in a branded format. Produces a single self-contained HTML file with a servings stepper that rescales every ingredient, tappable step checkboxes, and per-step countdown timers, all styled in Hayah-AI's dark-teal/coral/mint palette with the embedded SVG logomark. Trigger even if the user doesn't say "Hayah-AI" explicitly but asks for a branded or "my theme" recipe/menu page.
---

# Hayah-AI Menu Builder

Turn any recipe or menu item into a single self-contained, interactive HTML page in the **Hayah-AI Classic** brand. Output is a single HTML file with no build step, mobile-responsive, accessible, and visually consistent with hayah-ai.com. Fonts load from Google Fonts when online and fall back to system serif/sans/mono offline, so the page still renders without a network — the typography just degrades gracefully.

## What the output gives the end user

- **Servings stepper (1–20)** that live-rescales every ingredient amount.
- **Tappable step checkboxes** that strike through and dim completed steps.
- **Per-step countdown timers** (start / pause / reset) with a soft chime on completion.
- **Embedded Hayah-AI logomark** (arc + coral dot) and wordmark — no external image needed.
- **Cook's Notes** callout, prep/cook/difficulty meta bar, allergen/seafood-essence badge.

## Workflow

1. **Gather the recipe data.** From the conversation, an uploaded food photo, a pasted recipe, or a web search. If the source is a photo or a thin menu description, search the web for a faithful technique/ingredient list before generating — don't invent quantities. Extract: dish name, one-line description, allergen note (optional), prep/cook minutes, difficulty, ingredient list (amount + unit + name + optional flag), and ordered steps (title + body + optional timer seconds).

2. **Read the template.** Open `assets/template.html`. It is the canonical layout — do not redesign it. The only things you change are the data inside the `<script>` `DATA` object and the `<title>`.

3. **Fill the `DATA` object.** Replace the placeholder `DATA` block. Schema:

   ```js
   const DATA = {
     title: "Fresh Tomato & Herb Spaghetti",
     subtitle: "Quezo de Bola",          // optional second line, "" to omit
     description: "Spaghetti with a homemade sauce of fresh tomatoes…",
     allergen: "Contains seafood essence", // optional, "" to omit the badge
     prep: 15, cook: 35, difficulty: "Easy",
     baseServings: 4,
     ingredients: [
       // [amount, unit, name, optional?]
       [400, "g", "spaghetti", false],
       [3, "", "anchovy fillets (or 1 tsp patis)", false],
       [0.5, "tsp", "chili flakes", true],
     ],
     steps: [
       // [title, body, timerSeconds|null]
       ["Brown the mushrooms", "Heat half the oil…", 480],
       ["Finish and serve", "Off heat, fold in basil…", null],
     ],
     notes: [
       "Quezo de bola is saltier than parmesan — taste before salting.",
     ],
   };
   ```

   Rules for the data:
   - **Units**: use `g, kg, ml, l, tsp, tbsp, cup, oz, lb, pinch`, or `""` for countable items (fold the counting noun into the name, e.g. `"garlic cloves"`).
   - **Amounts** scale linearly from `baseServings`. The template rounds scaled amounts to 2 decimals and strips trailing zeros (e.g. `0.5`, `1.25`) — it does not render vulgar fractions like ½.
   - **`optional: true`** dims the row and adds an "optional" tag.
   - **Timers** are in seconds; use `null` for active hands-on steps with no waiting.
   - Keep the `description` in the end user's voice — what the dish is, not marketing fluff.

4. **Generate the file.** Read `assets/template.html` (at `~/.claude/skills/hayah-menu-builder/assets/template.html`). Use the Write tool to save a copy to `<cwd>/<slug>.html` — where `<cwd>` is the current working directory (wherever Claude Code is running from) and `<slug>` is a kebab-case version of the dish name. Then use the Edit tool to replace the placeholder `DATA` block with the filled-in recipe object. The comment `/* ============================================================` marks the start of the DATA block.

5. **Present it.** Use `SendUserFile` to surface the generated file with its full path, and give a one-line summary of the interactive features. Do not paste the full HTML into chat.

## Brand tokens (already baked into the template — reference only)

| Token | Hex | Use |
|---|---|---|
| Dark forest teal | `#0a3d3a` | logo stroke, headings, primary text |
| Aqua green | `#1a6b63` | section accents |
| Vibrant coral | `#ff6b47` | logo dot, italic "ai", primary action, amounts |
| Fresh mint | `#7fd1bf` | timers, success/checked state |
| Cream | `#f5efe4` | page background |
| Card | `#fbf8f1` | cards |

Type stack: **Playfair Display** (display/headings), **Inter** (body/UI), **JetBrains Mono** (eyebrows, amounts, labels). The template loads them from Google Fonts with a system-serif/sans fallback so it still renders offline.

Logo: the embedded inline SVG in the template is the canonical arc-logomark + "hayah-ai" wordmark with the `` tagline. Do not substitute a raster image.

## Guardrails

- **Don't redesign the template** per request — keep brand consistency across every menu generated. Adjust only data and (if truly needed) accent hue via the documented CSS variables.
- **Don't invent quantities** from a photo alone; verify with a search.
- One dish per file. For a multi-item menu, generate one card section per dish using the repeatable pattern, or produce separate files and ask the user which they prefer.
- Respect the brand: lowercase `hayah-ai`, coral `ai`, tagline `is cooking`.
