# Deploy & Redeploy — Runbook

Condensed from `~/projects-mvp/isp-billing/sheets-version/okf/runbooks/` and
`SETUP.md` there.

## First deploy (backend)

1. Create the Sheet; add one tab per entity with the exact header row.
   (Via Google Drive MCP `create_file` with an .xlsx: keep it minimal — base64
   blobs over ~5KB passed as literal tool-call params are unreliable; verify
   post-upload with `read_file_content`.)
2. Sheet → **Extensions → Apps Script** → paste `Code.gs` → save.
3. **Deploy → New deployment** → type **Web app** → Execute as **Me** → access
   **Anyone** ("Anyone within org" on Workspace — tighter, prefer when
   available).
4. **The OAuth consent click is a hard human-in-the-loop step** — "Advanced →
   Go to project (unsafe) → Allow" cannot be automated. Hand it to the user and
   wait for the `/exec` URL back.
5. Paste the `/exec` URL into `APPS_SCRIPT_URL` in the frontend (both .jsx and
   .html if both exist).

## Every subsequent Code.gs change — the #1 gotcha

**Deploy → Manage deployments → Edit (pencil) → Version: New version → Deploy.**

Editing/saving the script alone does NOT update the live `/exec` endpoint —
this is the single most common source of "my change did nothing" in this
pattern. Editing the *existing* deployment keeps the URL stable; creating a
*new deployment* mints a new URL and forces a frontend config update. Always
edit, never re-create, unless a URL rotation is the goal.

## API_TOKEN (recommended before the URL leaves your machine)

1. Generate: `openssl rand -hex 16`.
2. Apps Script editor → Project Settings → **Script Properties** → add
   `API_TOKEN` = the value.
3. Redeploy a new version.
4. Set the matching `API_TOKEN` const in the frontend (both files).

Unset property = auth disabled (safe default, can't lock you out mid-setup).
It's a shared secret, not real auth — internal tools only.

## Frontend deploy

The standalone .html deploys anywhere static — `/netlify-deploy` or
`/vercel-deploy` (free tier), or just open the file locally for solo use.
Ensure the committed copy has no real token if the repo is public.

## Post-deploy verification (every redeploy)

1. `curl '<EXEC_URL>?action=getAll&token=<TOKEN>'` — proves deploy + auth
   (expect the tabs as JSON, or `{"error":"Unauthorized"}` if token mismatch).
   Use `curl -L` — Apps Script answers via a 302 redirect.
2. One write via curl (`text/plain` body) — proves lock + validation.
3. The changed flows through the actual UI (`/agent-browser` or
   `/e2e-playwright` against the standalone .html).
4. Idempotent bulk actions: run twice, assert the second run creates 0 rows.
5. Clean up any test rows written to the live Sheet — dev = prod.
