# Changelog

All notable changes to WikiNest are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) · Versioning: [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Navigation

- **Folder display-name rename** — hovering any folder row in the sidebar reveals a pencil button. Clicking it opens a modal with the current display name pre-filled. On save, WikiNest creates or updates `docs/<folder-path>/_meta.json` with `{ "title": "…" }` (1 API call, atomic). The actual folder path and page URLs do not change. The sidebar updates optimistically; CI rebuilds the authoritative tree after deploy
- **Custom home page** — if `docs/home.md` exists in the tree, it is automatically opened on the first load instead of the empty state / recently-modified list. Create `docs/home.md` in any wiki to set a custom landing page; delete it to revert to the default empty state

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
