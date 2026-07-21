# Changelog

All notable changes to WikiNest are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) · Versioning: [Semantic Versioning](https://semver.org/)

## [2.3.0] — 2026-07-21

### Roles & permissions — new model

- **Permission model reworked** — no more hardcoded "sees everything" roles besides `owner` and `admin`. Director and department heads became ordinary, restrictable roles. `owner` never appears in any visibility/editors checklist (implicit full access); `admin` is always shown, forced-on and undisableable. Anyone in a page's `editors[]` can also see it automatically (edit access implies visibility) and can manage its visibility/editors list — not just the owner
- **Role set reduced to 9** — Владелец, Администратор, Директор, Руководитель отдела, Техническая поддержка, Отдел продаж, Бухгалтерия, Офис-менеджер, Отдел сервиса. Кладовщик/Логист/Установщик removed. Each role has its own password; owner got a distinct one (previously shared with admin, which made admin unreachable at login since login resolves the role by password hash)
- **`POST /api/write/page_visibility`** — narrow endpoint scoped to a single page's `roles[]`/`editors[]`/`isCounting`; requires edit rights on *that page* (per-page `editors[]` or global `can_edit`), re-reads tree.json fresh under the write lock instead of trusting the client's full-tree round-trip. docs.html visibility/editors modals now use it instead of PUTting the whole tree.json
- **Old section-visibility gear removed** — the per-3-role `hidden_sections` mechanism (gear icon on section headers) is fully superseded by folder-level visibility; `hidden_sections` cleared to `[]` for every role
- **Checklist UI** — visibility and editors modals show every restrictable role at once as individual checkboxes; the "Все роли" master toggle removed (empty selection still means unrestricted)

### Content

- Axenta doc moved from Сервисы to Памятки → Техническая поддержка; quick-access "Ссылки" button fixed (pointed at a page path that no longer exists after the links page moved to Сервисы)

## [2.2.0] — 2026-07-20

### Mail features

- **"Предложить статью"** — the suggest-an-article button is live on both paths: docs.html POSTs to `/api/suggest` (backend sends plain-text mail via SMTP), index.html dispatches the reusable `send-mail.yml` GitHub Actions workflow
- **Annual password rotation** — `POST /api/admin/rotate-passwords` (VM-only, owner session required, manual trigger): regenerates every role's password, rewrites `roles.json` hashes, commits via the VM's own git, mails all new passwords to the configured recipients

### Video attachments

- **Video pipeline** — drag-and-drop video upload fixed (silently did nothing when the browser reported an empty/non-standard MIME type, e.g. `.mkv`/`.mov` from Finder — now falls back to extension detection and shows a toast on truly unsupported files); non-browser-playable containers (`.mov`/`.mkv`/`.avi`/`.m4v`/`.3gp`) are transcoded to MP4 (H.264/AAC) by ffmpeg on upload; video files are gitignored and live only on the VM disk (too large for git history), so their URLs are absolute (`VM_PUBLIC_ORIGIN`) and keep working from the GitHub Pages fallback; player width capped at 920px

### Sync

- **Auto-sync before backup push** — the hourly GitHub backup push no longer fails with "fetch first" when GitHub has commits the VM doesn't: it fetches + merges first, and any conflict resolves in favor of the VM (`-X ours`) — the VM is the source of truth while alive, index.html's direct-to-GitHub path is only the outage fallback
- **Git Pull button** — owner's Settings gained a manual `POST /api/sync/pull` trigger (same VM-wins fetch+merge) for pulling in GitHub-only changes on demand; sync status now shows both last push and last pull
- **tree.json/search.json served by the backend** — Caddy reverse-proxies these two paths to Flask instead of single-file bind mounts, eliminating the stale-inode class of bugs (a `git pull` on the VM recreates the file; the old bind mount kept serving the pre-pull copy until a manual `docker compose restart caddy` — this is what made the page-visibility "eye" button look broken)
- **Live tree polling** — docs.html silently re-fetches tree.json every 20s and re-renders on diff, so edits made by other people show up without a reload

## [2.1.0] — 2026-07-16

### Tree management (owner)

- **Folder delete** — recursive, from the tree UI on both paths (`POST /api/write/delete_folder` on the VM; sequential per-file deletes via the git path)
- **Folder rename** — display-title only (`_meta.json.title`), paths and URLs never change
- **Drag-and-drop reorder** — docs.html only: an edit-structure toggle next to «РАЗДЕЛЫ» enters edit mode (drag handles + rename/delete buttons on every folder row); the second click applies all accumulated moves as one batched `POST /api/write/reorder` call/commit. index.html gets the same toggle for the buttons but no dragging (the git path's fire-and-forget writes can't batch)
- Backup push interval to GitHub lowered from 24h to 1h

## [2.0.0] — 2026-07-13/14

### VM hosting path — second, primary deployment

- **`backend/` + `docs.html`** — the wiki now has a second, self-hosted path: a Flask backend (Docker, gunicorn, Caddy with `tls internal` on a NAT-forwarded port) on a company VM. `docs.html` is a copy of `index.html` with the API layer swapped: same-origin CRUD endpoints instead of GitHub workflow dispatches. Every write commits synchronously to the VM's local git (full per-edit history, History modal works from it) and rebuilds tree.json/search.json in-process — no CI bot, no merge conflicts on this path
- **Server-side auth** — password verified by `POST /api/login` (SHA-256 compare on the server), signed HttpOnly session cookie, per-IP login rate limiting; `GET /api/roles` never ships password hashes to the browser (unlike the GitHub path, where client-side compare is acceptable because writes hide behind GitHub's own auth)
- **docx import** — upload a .docx, pandoc converts it to GFM (embedded images extracted to `docs/assets/`), result opens in the editor for review before saving
- **Multipart uploads** — `POST /api/write/upload` streams files to disk (no base64-in-JSON), used by the editor's drag-and-drop
- GitHub remains the hourly backup target and the outage fallback (GitHub Pages + workflow writes)

### UI (both paths)

- **2-level sidebar nesting** — subfolders inside subfolders render as collapsible groups; subfolders are collapsed by default, open state persists per-folder in localStorage
- **Шаблоны + Памятки merged**, sections reordered to match the ТЗ
- PDF/binary links open in a new tab instead of being routed as SPA pages
- PDF drag-and-drop upload; image drops now ask for display size (full / 400px)
- Back-to-top button on long pages

## [1.6.0] — 2026-07-03

### Dashboard & content

- **Homepage widgets** — recently-updated, section counters (`isCounting` frontmatter flag), glossary term count, incidents count parsed from the incidents table
- **Quick append modal** — one-click "add a row" for glossary and incidents tables (full-access roles), no editor round-trip
- **Create from tree** — empty folders render in the sidebar; folders and documents can be created directly from the tree
- Glossary replaced with the curated version (+16 terms); search term display fixed; birthday banner ordering fixes, then banner retired
- All static files served same-origin — `raw.githubusercontent.com` dependency removed (cache-busting included)

## [1.5.0] — 2026-07-01

### Write path & sessions

- **workflow_dispatch writes** — direct GitHub Contents API calls replaced with a `workflow_dispatch`-triggered Actions workflow (`api-write.yml`); the trigger token lives obfuscated in `config.json` instead of a full-power PAT in the browser
- **Persistent login** — role session survives reloads and new tabs (localStorage), including the full role object so no roles.json re-fetch is needed
- **Subfolder grouping** — sidebar groups pages by subfolder; `_meta.json` `pages[]` ordering support
- Dark theme removed entirely; `docs/` restructured to match SECTIONS (tp/ flattened to root); pure-JS SHA-256 fallback for non-HTTPS contexts; deep-link fallback matching by basename; error toasts stay 6s with red background

## [1.4.0] — 2026-05-25

### Navigation

- **Deep-link / direct URL support** — `404.html` added to the repo root. GitHub Pages and GitLab Pages serve it when a path like `site.github.io/repo/setup/installation` has no matching file; the script encodes the requested path as `?p=` and redirects to `index.html`. On startup `init()` reads `?p=`, stores it in `_pendingUrlPage`, and `loadTree()` resolves it to a page after the tree loads. `openPage()` now also calls `history.replaceState` after each successful navigation so the address bar always reflects the current page — making URLs copy-pasteable and shareable. `pathSegmentsToKeep = 1` in `404.html` (change to `0` for custom domains / user-pages). GitLab CI updated to copy `404.html` into `public/`

### Editor

- **Keyboard shortcuts** — new shortcuts in the editor: **Tab** inserts 2 spaces instead of shifting focus (standard indent behaviour); **Ctrl/Cmd+B** applies Bold; **Ctrl/Cmd+I** applies Italic. All three are implemented in `initEditorShortcuts()` as a textarea `keydown` listener that only fires while edit mode is active

### View

- **Share button** — "Share" button added to the content bar alongside Print and History. Clicking it copies the current page URL to the clipboard via the Clipboard API (falls back to a `prompt()` dialog on HTTP contexts without clipboard access). The button is visible only while viewing a page and is hidden in edit mode. Localized in English and Russian

### Navigation

- **Ctrl/Cmd+E** — opens the editor for the current page from view mode (equivalent to clicking the Edit button); no-op when already editing or no page is open
- **Ctrl/Cmd+Enter** — confirms the primary action of any open modal (Create, Save, Rename, Restore version); equivalent to clicking the highlighted button
- **Escape** — behaviour is now context-aware: closes search / wiki autocomplete / modal as before; if no overlay is open and the editor is active, cancels editing (equivalent to Cancel button)

### Bug fixes

- **Ctrl+Z / Ctrl+Y broken in editor** — all toolbar buttons (`fmt()`, `fmtLine()`), drag-and-drop image upload, and wiki-link autocomplete insertion used `setRangeText()` which bypasses the browser's input pipeline and destroys the native undo/redo stack. Replaced with `document.execCommand('insertText')` via a shared `taInsert()` helper; `setRangeText` is kept as a silent fallback only. Undo and redo now work correctly after every toolbar action

## [1.3.0] — 2026-05-22

### Navigation

- **Quick page creation from folder** — hovering any folder row reveals a `+` button alongside the pencil. Clicking it opens the New page dialog with the folder pre-selected. The New page dialog itself was redesigned: a folder dropdown (populated from the current tree) + a page-name input (validated to `[a-zA-Z0-9_\-]+`) + a live "Full path" preview that updates on every keystroke. The `+ New page` button in the sidebar still works identically, defaulting to the root folder
- **Folder display-name rename** — hovering any folder row in the sidebar reveals a pencil button. Clicking it opens a modal with the current display name pre-filled. On save, WikiNest creates or updates `docs/<folder-path>/_meta.json` with `{ "title": "…" }` (1 API call, atomic). The actual folder path and page URLs do not change. The sidebar updates optimistically; CI rebuilds the authoritative tree after deploy
- **Custom home page** — if `docs/home.md` exists in the tree, it is automatically opened on the first load instead of the empty state / recently-modified list. Create `docs/home.md` in any wiki to set a custom landing page; delete it to revert to the default empty state
- **Relative image paths fixed** — `renderView()` now rewrites relative `src` attributes in rendered `<img>` tags to absolute raw-CDN URLs before inserting into the DOM. Paths are resolved against the current file's directory (e.g. `../../assets/img.png` from `docs/setup/page.md` → `docs/assets/img.png` → full raw URL). Paths that are already absolute (`https://`, `//`, `data:`, fragment `#`) are left unchanged. `resolveDocRelative(rel)` helper added

## [1.2.0] — 2026-05-16

### Editor

- **Expanded markdown toolbar** — 16 buttons in 5 semantic groups, up from 10. Added: Strikethrough (`~~text~~`); H1 and H3 (completing the heading trio — all three displayed as text labels for clarity); Blockquote (`> `); Unordered list (`- `); Ordered list (`1. `); Task list (`- [ ] `). Groups: text formatting → headings → blocks/lists → code → insert. All new list/block buttons use `fmtLine()` with toggle semantics (pressing again removes the prefix)
- **Display preferences** — new section in ⚙ settings, saved to `localStorage` under `wn_display`:
  - *Show "On this page" panel* (`showToc`) — hides/shows the TOC panel; takes effect immediately without reopening the page
  - *Split preview while editing* (`splitPreview`) — when off, the editor opens full-width without the live-preview pane; applies on next Edit open

### View

- **Print / PDF** — "Print" button appears in the content bar while viewing a page. Calls `window.print()`. `@media print` CSS hides all chrome (header, sidebar, content bar, TOC, toolbars, modals) and presents only the rendered page content with print-optimised typography: 11 pt body, scaled headings, pre-wrap code blocks, `break-inside: avoid` on tables and blockquotes, external URLs printed in parentheses after links

### Deploy

- **Per-file deploy status in tree** — the file row in the sidebar gets an inline indicator after save: `●` pulsing grey (deploying), `✓` green (deployed, auto-removes after 3.5 s), `✗` red (CI failed, persists until next action). Previous indicators are cleared when a new save starts. The header badge is retained for overall status and on-load state. `pollActions()` gains an `onFail` callback; `watchDeploy()` captures `currentPath` at call time so navigation does not affect the indicator

### Security

- **XSS in sidebar tree** — `renderNode()` inserted `item._page.title` directly into `innerHTML`. All page titles, folder names, and path strings are now passed through `escHtml()` before being interpolated into HTML strings
- **XSS in breadcrumb** — path segment strings were interpolated raw into the breadcrumb `innerHTML`. Fixed: each segment is wrapped in `escHtml()`; the final title segment uses `escHtml(page.title)`
- **XSS in page-meta line** — `currentPath` and `meta.author` were interpolated directly. Fixed with `escHtml()` on both values
- **XSS in tag chips** — tags were embedded in an `onclick="..."` attribute via `JSON.stringify`, making them injectable. Rebuilt using the DOM API: `document.createElement('span')` with `.textContent = tag` and `.onclick = fn`
- **XSS in `buildToc`** — heading text was read from `el.textContent` but written to `anchor.innerHTML`. Fixed: use `anchor.textContent` assignment instead
- **Subresource Integrity on CDN script** — `marked.js` loaded from cdnjs without an integrity attribute; a compromised CDN response would execute arbitrary JS. Added `integrity="sha512-…"` + `crossorigin="anonymous"` to the script tag
- **`JSON.parse` without try/catch in `init()`** — corrupted `wn_cfg` in localStorage threw a SyntaxError that crashed the entire app before the first render. Wrapped in try/catch; bad entries are removed and execution continues
- **API error bodies thrown as HTML** — `ghFetch`/`glFetch` called `r.json()` unconditionally on error responses; GitHub Pages 502s return HTML and the JSON parse threw a SyntaxError that masked the real status. Now wrapped in try/catch with fallback to `r.statusText`
- **`startEdit` double-click race** — clicking Edit twice before the first API call returned fetched the file twice and left the editor in an inconsistent state. `btn-edit` is now disabled on entry and re-enabled only on failure
- **`openHistory` double-click race** — same pattern; History button is disabled for the duration of the fetch
- **`openPage` stale-path race** — `currentPath` was mutated before the file fetch resolved; fast navigation between pages could render content from the wrong file. `targetPath` is now captured in a local constant; the fetch result is discarded if `currentPath` has since changed
- **Image alt-text injection** — drag-dropped image filenames containing `"` were embedded raw into `![name](url)` alt text inserted into the editor. Filenames are now sanitised: non-alphanumeric characters (except `.`, `-`, `_`) are replaced with `-` before insertion
- **Path traversal in `createPage` / `doRename`** — no validation was applied to user-supplied paths, allowing `../../` segments. A strict allowlist regex (`/^[a-zA-Z0-9_\-][a-zA-Z0-9_\-\/]*$/`) now rejects invalid paths before any API call

### Bug fixes

- **`decrypt` / `encrypt` key-symmetry** — `encrypt(str, '')` returned `str` as plaintext, but `decrypt(str, '')` returned `''`; the asymmetry silently erased the token on every session restart in no-password configurations. `decrypt` now returns `enc` unchanged when the key is falsy, matching `encrypt`
- **Token not persisted without password re-entry** — saving a new PAT in Settings without typing the password stored it only in memory (`cfg.token`), not in `localStorage`; on reload it was lost, and the subsequent `requireUnlock()` call overwrote it with the stale encrypted value. Fixed: if a password hash is configured, the password is required to persist a new token (toast shown if omitted); if no hash is configured, the token is stored as plaintext to match the no-key `encrypt` path
- **Duplicate TOC heading IDs** — two headings with identical text both received the same `id`, so TOC clicks always navigated to the first occurrence. `buildToc()` now appends `-2`, `-3`, … suffixes for repeated base IDs
- **Live preview renders on every keystroke** — `marked.parse()` and a full `#view` `innerHTML` replacement fired synchronously for each character typed, causing jank on large documents. Extracted `renderPreviewDebounced` (150 ms debounce) shared by `startEdit()` and `restoreVersion()`; dirty tracking and draft autosave remain immediate
- **No guard when navigating away from a dirty editor** — clicking a tree item while editing silently discarded unsaved changes; `beforeunload` only fired on tab closes, not in-page navigation. `openPage()` now opens a confirmation dialog when `editorDirty` is true
- **`watchDeploy()` race condition** — multiple rapid saves each spawned an independent `waitForNewRun` loop; all shared `watchingRunId` and called `pollActions()` concurrently, causing them to cancel each other's `pollTimer` and potentially skip `loadTree()`. Each `watchDeploy()` call now increments `watchDeployGen`; stale loops check the generation on every tick and self-terminate when superseded
- **History opens without unlock** — `openHistory()` called `fetchHistory()` which used `cfg.token` before the session was unlocked, producing a 401 shown as a raw error string in the modal. `openHistory()` is now `async` and calls `requireUnlock()` before fetching

## [1.1.0] — 2026-05-15

### Editor

- **Offline drafts** — editor auto-saves to `localStorage` every 500 ms (debounced). On re-opening an edited page a yellow banner offers "Restore draft" or "Discard". Drafts survive tab closes and cancelled edits; they are cleared on successful save.
- **Markdown toolbar** — floating toolbar above the editor with Bold, Italic, Inline Code, Code Block, Heading 2, Link, Image, Table, and HR buttons. Toolbar appears only while editing (`edit-active` class). Selection-aware: wraps selected text or inserts a placeholder at the cursor. `fmtLine()` handles prefix-toggling for headings.
- **Drag-and-drop image upload** — drop image files onto the editor panel. Images are uploaded to `docs/assets/<timestamp>-<filename>` via the API, then `![name](rawUrl)` is inserted at the cursor. Non-image files are silently ignored. Visual dashed-blue overlay while dragging.

### Pages

- **Page history** — "History" button (clock icon) in the content bar opens a modal listing the last 20 commits that touched the current file (GitHub and GitLab supported). Click any commit to preview the rendered markdown at that SHA. "Restore this version" loads the historical content into the editor with `editorDirty=true` so the user must explicitly save.
- **Frontmatter (YAML metadata)** — `parseFrontmatter()` strips a leading `---…---` block before rendering. Supported keys: `tags` (array or comma-separated string), `author` (string), `description`. Tags render as clickable chips below the page path; clicking a tag opens search pre-filled with that tag. Author is shown in the page-meta line.
- **Wiki links `[[Page Name]]`** — `[[Title]]` syntax in markdown auto-links to matching pages (by title or path, case-insensitive). Broken links render as a red strikethrough span. A live autocomplete dropdown appears in the editor after typing `[[`; navigate with arrow keys, confirm with Enter, dismiss with Escape.

### Search

- **Full-text search** — `search.json` (generated by `build-tree.yml`) maps page paths to full raw content. The frontend fetches it lazily on first search open and uses it to extend results beyond title/excerpt matches. Full-text-only results are labelled with a "Full text" badge. Results are deduplicated.

### Infrastructure

- **`build-tree.yml`** extended: parses frontmatter from every `.md` file; adds `tags` and `author` fields to each `tree.json` entry; writes `search.json` (path → raw markdown content) alongside `tree.json`; both files are committed in the same step.

## [1.0.0] — 2026-05-13

First stable release. Ships as a single `index.html` + `style.css` with no build step, no npm, no server.

### Editor

- In-browser markdown editor with real-time **split-view**: editor on the left, rendered HTML preview on the right; preview updates on every keystroke
- **Ctrl+S / ⌘S** saves the current page without leaving the keyboard
- Unsaved changes trigger a **`beforeunload` warning** — the browser confirms before the tab closes
- Cancel restores the original rendered view (no stale preview after discarding edits)

### Pages

- **Create** — "New page" button with a path input (`ops/servers/nginx` → `docs/ops/servers/nginx.md`); folders created automatically
- **Edit** — loads content from the GitHub Contents API, writes back as a signed commit
- **Delete** — modal confirmation dialog; no native `confirm()`
- **Rename** — modal with pre-filled current path; creates the file at the new path, deletes the old one, reloads the tree and navigates to the renamed page

### Navigation

- **Sidebar tree** mirrors `docs/` folder structure; unlimited nesting; folders are collapsible
- **Folder aliases** — custom display names via `_meta.json` without renaming directories
- **TOC (table of contents)** — auto-generated from `h2`/`h3` headings; clicking an entry scrolls smoothly and updates `location.hash`; deep links are copy-pasteable
- **Recently modified** — empty state shows the 5 most recently changed pages, sorted by `updated_at` from `tree.json`

### Search

- Client-side full-text search over page titles and excerpts (first ~140 chars)
- **⌘K / Ctrl+K** to open; Escape to close
- Results highlighted inline; click to navigate; keyboard-navigable

### Authentication & Security

- **Edit password** — SHA-256 hash stored in public `config.json`; password unlocks editing for the session
- **PAT encryption** — Personal Access Token is XOR-encrypted with the edit password and stored in `localStorage`; never leaves the browser except to `api.github.com`
- **Multi-maintainer** — `config.json` is the shared source of truth; each editor supplies their own PAT

### UX & Feedback

- **GitHub Actions status badge** in the header — shows live deploy status (queued → deploying → deployed / failed) with a link to the Actions run
- **Deploy watcher** — after each save, polls Actions until the new run appears and completes, then reloads the tree and shows a "Deploy complete" toast
- **Toast notifications** — auto-dismissing (2.5 s) feedback for save, deploy, and error events
- **Dark mode** — follows `prefers-color-scheme`; all colors are CSS variables, trivially overridable
- **Mobile** — sidebar collapses to a hamburger menu; split-view collapses to editor-only on narrow screens
- **Language switcher** — runtime switch without page reload; selection persisted in `localStorage`

### Infrastructure

- **`build-tree.yml`** — triggers on `docs/**` changes; generates `tree.json` with `path`, `title`, `excerpt`, `parts`, `folder_titles`, and `updated_at` (ISO 8601 timestamp from `git log`)
- **`deploy.yml`** — triggers on every push to `main`; runs build-tree, then deploys to GitHub Pages
- **`config.json`** — single public config file; loaded fresh on every page open; no user action needed to pick up changes
- **i18n** — UI strings in `i18n/<lang>.json`; English and Russian included; missing keys fall back to the key name

### Bug fixes (pre-release iterations)

- Fixed stale SHA after save — `currentSha` is now updated from the PUT response, preventing 409 Conflict on immediate re-save without a page reload
- Fixed `cancelEdit()` not restoring the rendered view — now re-renders from `originalContent` captured at edit-open time
- Fixed deploy watcher not tracking new runs — `watchDeploy()` now waits for a run with a different ID before polling
- Fixed raw GitHub CDN cache on page content — post-save render uses the local editor value, not a re-fetch through the CDN
