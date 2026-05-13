# Architecture

WikiNest is a single-page application with no backend. All state lives in a Git repository (GitHub or GitLab): content in `docs/`, site config in `config.json`, the page index in `tree.json`. The browser talks directly to the provider REST API; the active provider is set by `config.json → provider`.

---

## Data flow

### GitHub

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Sidebar  │  │  Editor  │  │  Search  │  │ Settings / PW │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       └─────────────┴─────────────┴─────────────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼──────────────┐   ┌───────────▼──────────────┐
    │  raw.githubusercontent  │   │      api.github.com       │
    │  .com/HEAD/{path}       │   │  /repos/{owner}/{repo}/   │
    │  (read: tree.json,      │   │  contents/{path}          │
    │   .md files)            │   │  (write: PUT, DELETE)     │
    └─────────┬──────────────┘   └───────────┬──────────────┘
              └───────────────┬───────────────┘
                              │ commit to main
                    ┌─────────▼──────────┐
                    │   GitHub Actions   │
                    │  build-tree.yml    │
                    │  → tree.json       │
                    │  deploy.yml        │
                    │  → GitHub Pages    │
                    └────────────────────┘
```

### GitLab

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Sidebar  │  │  Editor  │  │  Search  │  │ Settings / PW │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       └─────────────┴─────────────┴─────────────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼──────────────┐   ┌───────────▼──────────────────┐
    │  gitlab.com/{ns}/{repo} │   │  gitlab.com/api/v4/projects/  │
    │  /-/raw/main/{path}     │   │  {ns}%2F{repo}/repository/    │
    │  (read: tree.json,      │   │  files/{path}                 │
    │   .md files)            │   │  (write: POST, PUT, DELETE)   │
    └─────────┬──────────────┘   └───────────┬──────────────────┘
              └───────────────┬───────────────┘
                              │ commit to main
                    ┌─────────▼──────────┐
                    │   GitLab CI/CD     │
                    │  build-tree job    │
                    │  → tree.json       │
                    │  pages job         │
                    │  → GitLab Pages    │
                    └────────────────────┘
```

### Read path

1. `init()` fetches `config.json` (same-origin, Pages CDN), sets `cfg.provider`
2. `loadTree()` calls `rawUrl('tree.json')` → fetches from the provider's raw CDN with `cache: 'no-cache'`
3. `openPage()` calls `rawUrl(currentPath)` → fetches the `.md` file the same way
4. Content is rendered locally via `marked.js`

### Write path

1. `startEdit()` calls `apiGetFile(path)` → normalised `{ sha, content }` regardless of provider
2. User edits; live preview updates in the split-view panel
3. `savePage()` calls `apiPutFile(path, message, content, sha)` → returns `{ sha }` of the new commit
4. `currentSha` is updated immediately so re-saves work without a page reload
5. `watchDeploy()` polls `fetchLatestRun()` until a new CI run appears and completes

---

## CDN caching

Both `raw.githubusercontent.com` (GitHub) and `gitlab.com/-/raw/` (GitLab) cache raw file responses for approximately 30–60 seconds regardless of `Cache-Control` headers. This means:

- After a save, the post-save render uses the **local editor value**, not a re-fetch
- `tree.json` after deploy may be stale for up to 60 s — the deploy watcher reloads it only after CI confirms success
- `config.json` is served from the Pages CDN, so config changes may lag by the same amount

---

## File map

### `index.html`

All application logic. No build step, no modules, no bundler.

#### Globals

| Variable | Type | Purpose |
|---|---|---|
| `cfg` | object | Merged config: `config.json` + `localStorage` overrides |
| `i18n` | object | Current language strings from `i18n/<lang>.json` |
| `tree` | array | Page index loaded from `tree.json` |
| `currentPath` | string\|null | Full repo path of the open page (`docs/foo/bar.md`) |
| `currentSha` | string\|null | Provider blob/commit SHA for the open page; required for write operations |
| `unlocked` | bool | Whether the edit password has been entered this session |
| `editorDirty` | bool | True if the editor has unsaved changes vs. `originalContent` |
| `originalContent` | string\|null | Raw markdown as loaded from the API; restored on cancel |

#### Functions

**Bootstrap**

| Function | Description |
|---|---|
| `init()` | Entry point. Loads config → i18n → tree. Registers keyboard shortcuts and `beforeunload`. |
| `loadI18n(lang)` | Fetches `i18n/<lang>.json`, sets `i18n`. |
| `applyI18n()` | Stamps all `lbl-*` elements with translated strings. |
| `switchLang(lang)` | Persists language choice, reloads strings, re-applies. |
| `showSetupBanner()` | Replaces the empty-state placeholder when `config.json` has no owner/repo. |

**Tree**

| Function | Description |
|---|---|
| `loadTree()` | Fetches `tree.json`, calls `renderTree()`, then `showEmpty()` if no page is open. |
| `renderTree(pages)` | Converts the flat page array into a nested object, then calls `renderNode()`. |
| `renderNode(node, el, depth)` | Recursively builds sidebar DOM. Folders are collapsible. |
| `getFolderTitle(node, key)` | Reads `folder_titles` from the nearest descendant page entry. |

**Page lifecycle**

| Function | Description |
|---|---|
| `openPage(page)` | Sets `currentPath`, updates breadcrumb, fetches and renders the page. |
| `renderView(md)` | Parses markdown, writes to `#view`, calls `buildToc()`. |
| `buildToc()` | Reads `h2`/`h3` from `#view`, assigns IDs, builds TOC, scrolls to `location.hash`. |
| `tocClick(id)` | Smooth-scrolls to heading, updates `location.hash` via `history.replaceState`. |
| `startEdit()` | Requires unlock, fetches content + SHA, stores `originalContent`, activates split-view. |
| `cancelEdit()` | Restores `originalContent`, removes split-view, resets dirty state. |
| `savePage()` | Calls `apiPutFile()`, updates `currentSha` from the response, calls `watchDeploy()`. |

**Page management**

| Function | Description |
|---|---|
| `openNewPage()` | Opens the New Page modal. |
| `createPage()` | Requires unlock, creates the file via PUT, reloads tree, opens the new page. |
| `deletePage()` | Opens a modal confirmation. |
| `doDelete()` | Requires unlock, fetches SHA, DELETEs the file, resets state, calls `showEmpty()`. |
| `openRenamePage()` | Opens the Rename modal with the current path pre-filled. |
| `doRename()` | Requires unlock, creates the file at the new path, DELETEs the old one, navigates. |

**Empty state**

| Function | Description |
|---|---|
| `showEmpty()` | Shows `#empty`. If `tree` entries have `updated_at`, renders the 5 most recent; otherwise shows the placeholder icon. |

**Search**

| Function | Description |
|---|---|
| `openSearch()` / `closeSearch()` | Toggles `#search-overlay`. |
| `runSearch(q)` | Filters `tree` by title and excerpt, renders highlighted results. |
| `searchKey(e)` | Closes search on Escape. |

**Authentication**

| Function | Description |
|---|---|
| `requireUnlock()` | Returns a Promise. Resolves immediately if `unlocked`; otherwise shows `#pw-overlay`. |
| `submitPw()` | Hashes the input, checks against `cfg.edit_password_hash`, decrypts the token on success. |
| `closePw()` | Dismisses `#pw-overlay`. |
| `checkPassword(pw)` | SHA-256 hashes `pw`, compares to `cfg.edit_password_hash`. |
| `encrypt(str, key)` | XOR-obfuscates `str` with `key`, returns base64. Used only for the PAT in localStorage. |
| `decrypt(enc, key)` | Inverse of `encrypt`. |

**API layer**

| Function | Description |
|---|---|
| `ghFetch(path, method, body)` | Authenticated fetch against `api.github.com/repos/{owner}/{repo}/{path}`. Uses `Authorization: Bearer`. Throws on non-2xx. |
| `glFetch(path, method, body)` | Authenticated fetch against `gitlab.com/api/v4/projects/{owner}%2F{repo}/{path}`. Uses `PRIVATE-TOKEN`. Returns `null` for 204 / DELETE responses. |
| `rawUrl(path)` | Returns the correct raw-content URL for the active provider. |
| `apiGetFile(path)` | Fetches file metadata via the provider API; normalises to `{ sha, content }`. For GitLab maps `last_commit_id → sha`. |
| `apiPutFile(path, message, content, sha)` | Creates (no sha) or updates (with sha) a file. GitHub: `PUT contents/`. GitLab: `POST` or `PUT repository/files/`, then re-fetches to get the new SHA. Returns `{ sha }`. |
| `apiDeleteFile(path, message, sha)` | Deletes a file on the active provider. |
| `normalizeRun(run)` | Maps a GitLab pipeline object to the GitHub-shaped `{ id, status, conclusion, html_url }` that `pollActions` and `renderStatus` expect. Statuses: `running/preparing → in_progress`, `pending/created/… → queued`, `success/failed/canceled → completed + conclusion`. |
| `b64enc(s)` | UTF-8 → base64 (required by both provider APIs for file content). |
| `b64dec(s)` | base64 → UTF-8 (for decoding API responses). |

**CI status**

| Function | Description |
|---|---|
| `fetchLatestRun()` | GitHub: fetches `actions/runs?per_page=3`. GitLab: fetches `pipelines?per_page=3` and passes the result through `normalizeRun()`. Returns the watched run or the latest. |
| `renderStatus(run)` | Updates `#actions-status` badge with dot + label + link. Works identically for both providers after normalisation. |
| `pollActions(onDone)` | Polls every 5 s while run is active (`in_progress` or `queued`); every 30 s otherwise. Calls `onDone` on success. |
| `watchDeploy()` | Called after save/create/delete/rename. Records `beforeId`, waits for a new CI run to appear, then calls `pollActions`. |

**Settings**

| Function | Description |
|---|---|
| `openSettings()` | Renders and opens the settings modal. |
| `saveSettings()` | Encrypts token if a password is provided, persists language pref, reloads tree. |

**UI helpers**

| Function | Description |
|---|---|
| `openModal()` / `closeModal()` | Show/hide `#modal-overlay`. |
| `toast(msg)` | Shows a bottom-right toast for 2.5 s. |
| `toggleSidebar()` | Toggles the mobile sidebar and overlay. |

---

### `style.css`

No preprocessor. All layout uses CSS Flexbox and Grid.

| Selector | Purpose |
|---|---|
| `:root` | Light-mode CSS variables (colors, dimensions) |
| `@media (prefers-color-scheme: dark)` | Dark-mode variable overrides |
| `#layout` | Flex row: sidebar + content |
| `#panels` | Flex row: `#view-wrap` + `#editor-wrap` + `#toc` |
| `#panels.split` | Grid 1fr 1fr: editor and preview side by side |
| `#panels.split #toc` | Hidden in split mode |
| `#panels.split #view-wrap` | Right border separating preview from editor |
| `@media (max-width: 768px)` | Mobile: sidebar off-canvas, split collapses to editor-only |

---

### `tree.json`

Auto-generated by `build-tree.yml` (GitHub) or the `build-tree` CI job (GitLab). Never edit by hand.

```jsonc
[
  {
    "path": "setup/installation",      // relative to docs/, no .md
    "title": "Installation",           // from first # heading
    "excerpt": "WikiNest requires…",   // first non-heading line, max 140 chars
    "parts": ["setup", "installation"],// path.split('/') — used for tree rendering
    "folder_titles": {
      "setup": "Setup & Installation"  // display name from _meta.json
    },
    "updated_at": "2026-05-13T10:22:00+03:00" // ISO 8601, from git log -1 --format=%cI
  }
]
```

---

### `config.json`

Public. Committed to the repository. **Never put secrets here.**

```jsonc
{
  "site_name": "WikiNest",
  "lang": "en",
  "provider": "github",     // "github" (default) or "gitlab"
  "owner": "your-username", // GitHub username/org or GitLab namespace
  "repo": "wikinest",
  "edit_password_hash": ""  // SHA-256 hex of the edit password; empty = no password
}
```

---

## Token encryption

The PAT is stored in `localStorage` as `wn_enc_token`. The encryption is XOR with the edit password as a repeating key, then base64-encoded:

```js
encrypt(str, key) → btoa([...str].map((c, i) =>
  String.fromCharCode(c.charCodeAt(0) ^ key.charCodeAt(i % key.length))
).join(''))
```

This is **obfuscation, not encryption**. It protects against casual inspection of localStorage and prevents the raw PAT from sitting in plaintext. It does not protect against an attacker who has read access to localStorage and knows the password. For a private internal wiki this is an acceptable trade-off; for high-security contexts, consider replacing with `AES-GCM` via the Web Crypto API.

The PAT is decrypted into memory (`cfg.token`) only after the correct password is entered. It is never written back to localStorage in plaintext.

---

## CI workflows

Both providers run the same Python tree-generation script. The logic is identical; only the CI syntax and push mechanism differ.

**Python script (shared logic)**

Walks `docs/`, reads `_meta.json` files for folder aliases, extracts `title` from the first `# heading` and `excerpt` from the first non-heading line (max 140 chars), runs `git log -1 --format=%cI -- {file}` per page to get `updated_at`, writes `tree.json`.

---

### GitHub Actions

**`build-tree.yml`**

Trigger: push to `main` that touches `docs/**`.

1. Checkout with `fetch-depth: 0` — required for `git log` timestamps
2. `git pull origin main`
3. Run Python script → write `tree.json`
4. `git commit tree.json && git push` if changed

Requires **Read and write permissions** under Settings → Actions → General.

**`deploy.yml`**

Trigger: every push to `main`.

1. Runs the same build-tree logic
2. Deploys to GitHub Pages via `actions/deploy-pages`

---

### GitLab CI/CD (`.gitlab-ci.yml`)

**`build-tree` job** — stage: `build`

Trigger: push to the default branch that touches `docs/**`.

1. `git remote set-url origin` with `GITLAB_TOKEN` for authenticated push
2. Run Python script → write `tree.json`
3. `git commit tree.json && git push` if changed

Requires a CI/CD variable `GITLAB_TOKEN` with `api` + `write_repository` scope (Settings → CI/CD → Variables).

**`pages` job** — stage: `deploy`

Trigger: every push to the default branch.

1. Copies `index.html`, `style.css`, `config.json`, `tree.json`, `i18n/`, `docs/` into `public/`
2. GitLab Pages serves the `public/` artifact automatically
