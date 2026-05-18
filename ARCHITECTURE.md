# Architecture

WikiNest is a single-page application with no backend. All state lives in a Git repository (GitHub or GitLab): content in `docs/`, site config in `config.json`, the page index in `tree.json` and full-text index in `search.json`. The browser talks directly to the provider REST API; the active provider is set by `config.json → provider`.

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
    │   search.json, .md)     │   │  (write: PUT, DELETE)     │
    └─────────┬──────────────┘   └───────────┬──────────────┘
              └───────────────┬───────────────┘
                              │ commit to main
                    ┌─────────▼──────────┐
                    │   GitHub Actions   │
                    │  build-tree.yml    │
                    │  → tree.json       │
                    │  → search.json     │
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
    │   search.json, .md)     │   │  (write: POST, PUT, DELETE)   │
    └─────────┬──────────────┘   └───────────┬──────────────────┘
              └───────────────┬───────────────┘
                              │ commit to main
                    ┌─────────▼──────────┐
                    │   GitLab CI/CD     │
                    │  build-tree job    │
                    │  → tree.json       │
                    │  → search.json     │
                    │  pages job         │
                    │  → GitLab Pages    │
                    └────────────────────┘
```

### Read path

1. `init()` loads display prefs from `localStorage`, then fetches `config.json` (same-origin, Pages CDN), sets `cfg.provider`
2. `loadTree()` calls `rawUrl('tree.json')` → fetches from the provider's raw CDN with `cache: 'no-cache'`. After rendering the tree, if no page is currently open: looks for a page with `path === 'home'` (i.e. `docs/home.md`); if found, calls `openPage(homePage)`; otherwise calls `showEmpty()`
3. `openPage()` calls `rawUrl(currentPath)` → fetches the `.md` file; `renderView()` parses frontmatter then renders via `marked.js`
4. `ensureSearchIndex()` lazily fetches `search.json` on first search open

### Write path

1. `startEdit()` calls `requireUnlock()`, then `apiGetFile(path)` → normalised `{ sha, content }` regardless of provider. Respects `displayPrefs.splitPreview` for panel layout
2. User edits; `renderPreviewDebounced` (150 ms debounce) updates `#view`; `saveDraftDebounced` (500 ms) writes to `localStorage`
3. `savePage()` calls `apiPutFile(path, message, content, sha)` → returns `{ sha }` of the new commit; `currentSha` updated immediately
4. `watchDeploy()` captures `currentPath` and a generation counter, sets the tree-row indicator to `●`, then polls `fetchLatestRun()` until a new CI run appears and completes; on success shows `✓` for 3.5 s; on failure leaves `✗`

---

## CDN caching

Both `raw.githubusercontent.com` (GitHub) and `gitlab.com/-/raw/` (GitLab) cache raw file responses for approximately 30–60 seconds regardless of `Cache-Control` headers. This means:

- After a save, the post-save render uses the **local editor value**, not a re-fetch
- `tree.json` and `search.json` after deploy may be stale — the deploy watcher reloads them only after CI confirms success
- Optimistic tree updates (create / rename / delete) patch the local `tree[]` array and re-render the sidebar immediately, without waiting for CI

---

## File map

### `index.html`

All application logic. No build step, no modules, no bundler.

#### Globals


| Variable                 | Type           | Purpose                                                                                                                                               |
| ------------------------ | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cfg`                    | object         | Merged config:`config.json` + `localStorage` overrides                                                                                                |
| `i18n`                   | object         | Current language strings from`i18n/<lang>.json`                                                                                                       |
| `tree`                   | array          | Page index loaded from`tree.json`                                                                                                                     |
| `currentPath`            | string\|null   | Full repo path of the open page (`docs/foo/bar.md`)                                                                                                   |
| `currentSha`             | string\|null   | Provider blob/commit SHA for the open page; required for write operations                                                                             |
| `unlocked`               | bool           | Whether the edit password has been entered this session                                                                                               |
| `editorDirty`            | bool           | True if the editor has unsaved changes vs.`originalContent`                                                                                           |
| `originalContent`        | string\|null   | Raw markdown as loaded from the API; restored on cancel                                                                                               |
| `searchIndex`            | object\|null   | Lazy-loaded`search.json` map of `path → raw markdown`; `null` until first search open                                                                |
| `dragDropInit`           | bool           | Guard flag;`initDragDrop()` is a no-op after the first call                                                                                           |
| `displayPrefs`           | object         | `{ showToc: bool, splitPreview: bool }` — loaded from `localStorage` on init                                                                         |
| `watchDeployGen`         | number         | Incremented on each`watchDeploy()` call; stale polling loops bail when generation changes                                                             |
| `pollTimer`              | number\|null   | `setTimeout` handle for the periodic Actions/CI poll                                                                                                  |
| `watchingRunId`          | number\|null   | ID of the CI run currently being tracked                                                                                                              |
| `pwResolve`              | function\|null | Promise resolver for the password dialog; called by`submitPw()`                                                                                       |
| `wikiCompleteIdx`        | number         | Keyboard-selected index in the`[[` autocomplete dropdown                                                                                              |
| `wikiCompleteItems`      | array          | Current page matches shown in the`[[` autocomplete                                                                                                    |
| `_pendingRestoreContent` | string\|null   | Holds the raw markdown content for`restoreVersion()`. Set before calling it; avoids embedding potentially large content in `onclick` HTML attributes. |
| `_pendingFolderPath`     | string\|null   | Holds the relative folder path (e.g.`ops/servers`) for `doFolderRename()`. Set by `openFolderRename()`.                                               |

#### Functions

**Bootstrap**


| Function            | Description                                                                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `init()`            | Entry point. Calls`loadDisplayPrefs()`, fetches `config.json`, loads i18n, loads tree. Registers ⌘K, ⌘S, Escape shortcuts and `beforeunload`. |
| `loadI18n(lang)`    | Fetches`i18n/<lang>.json`, sets `i18n`.                                                                                                         |
| `applyI18n()`       | Stamps all`lbl-*` elements with translated strings via null-safe `set(id, val)` helper.                                                         |
| `switchLang(lang)`  | Persists language choice to`localStorage`, reloads strings, re-applies.                                                                         |
| `showSetupBanner()` | Replaces the empty-state placeholder when`config.json` has no `owner`/`repo`.                                                                   |

**Display preferences**


| Function                    | Description                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `loadDisplayPrefs()`        | Reads`wn_display` from `localStorage` and merges into `displayPrefs`. Called at the top of `init()`.                                        |
| `saveDisplayPref(key, val)` | Sets`displayPrefs[key]`, persists the whole object to `localStorage`.                                                                       |
| `setDisplayPref(key, val)`  | Calls`saveDisplayPref`, then applies side-effects: `showToc` immediately calls `buildToc()`; `splitPreview` takes effect on next edit open. |

**Tree**


| Function                            | Description                                                                                                                                                                                      |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `loadTree()`                        | Fetches`tree.json` with `cache: 'no-cache'`, calls `renderTree()`, then `showEmpty()` if no page is open.                                                                                        |
| `renderTree(pages)`                 | Converts the flat page array into a nested object, then calls`renderNode()`.                                                                                                                     |
| `renderNode(node, el, depth)`       | Recursively builds sidebar DOM. Leaf rows get`data-path` attribute for per-file status targeting. Folders are collapsible.                                                                       |
| `getFolderTitle(node, key)`         | Reads`folder_titles` from the nearest descendant page entry.                                                                                                                                     |
| `setTreeRowStatus(relPath, status)` | Finds the leaf row by`data-path`, removes any existing `.tree-status` child, appends a new one with class `tree-status--{pending|success|failure}`. Uses `CSS.escape()` for path-safe selection. |
| `clearAllTreeStatuses()`            | Removes all`.tree-status` elements from the sidebar (called at the start of each `watchDeploy()`).                                                                                               |

**Page lifecycle**


| Function                 | Description                                                                                                                                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `openPage(page)`         | Guards with`editorDirty` confirmation dialog. Sets `currentPath`, updates breadcrumb, shows `btn-print`, fetches and renders the page.                                                                                                           |
| `renderView(md)`         | Calls`parseFrontmatter()`, renders meta/tags bar, writes `marked.parse(body)` to `#view`, calls `buildToc()`.                                                                                                                                    |
| `buildToc()`             | Respects`displayPrefs.showToc`. Reads `h2`/`h3` from `#view`, assigns IDs (with `-2`/`-3` suffixes for duplicates), builds TOC list, scrolls to `location.hash`.                                                                                 |
| `tocClick(id)`           | Smooth-scrolls to heading, updates`location.hash` via `history.replaceState`.                                                                                                                                                                    |
| `_activateEditorPanel()` | Shared helper called by both`startEdit()` and `restoreVersion()`. Applies `displayPrefs.splitPreview`, shows `#editor-wrap`, hides view-mode buttons, assigns the debounced `oninput` handler, calls `initDragDrop()`, and focuses the textarea. |
| `startEdit()`            | Requires unlock, fetches content + SHA via`apiGetFile()`, stores `originalContent`. Checks for existing draft and shows `#draft-banner` if found. Calls `_activateEditorPanel()`.                                                                |
| `cancelEdit()`           | Re-renders`originalContent` (if set), clears dirty state, removes split-view, restores view-mode buttons including `btn-print`.                                                                                                                  |
| `savePage()`             | Calls`apiPutFile()`, updates `currentSha` from the response, clears draft, calls `cancelEdit()` then `watchDeploy()`.                                                                                                                            |

**Page management**


| Function                       | Description                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `openNewPage()`                | Opens the New Page modal.                                                                                                                                                                                                                                                                                                                                                 |
| `createPage()`                 | Requires unlock. Validates path with a strict allowlist regex (`/^[a-zA-Z0-9_\-][a-zA-Z0-9_\-\/]*$/`) before any API call. Creates file via `apiPutFile(…, null)` (no SHA = create). Optimistically pushes to `tree[]`, re-renders sidebar, opens the new page.                                                                                                          |
| `deletePage()`                 | Opens a modal confirmation.                                                                                                                                                                                                                                                                                                                                               |
| `doDelete()`                   | Requires unlock. Fetches current SHA, calls`apiDeleteFile()`. Optimistically removes from `tree[]`, re-renders sidebar, calls `showEmpty()`.                                                                                                                                                                                                                              |
| `openRenamePage()`             | Opens the Rename modal with the current path pre-filled.                                                                                                                                                                                                                                                                                                                  |
| `doRename()`                   | Requires unlock. Validates the new path with the same allowlist regex as`createPage()`. `apiPutFile()` at new path (no SHA), `apiDeleteFile()` at old path. Optimistically updates `tree[]` and navigates to renamed page. Non-atomic: if DELETE fails, both paths exist until CI rebuilds the tree.                                                                      |
| `openFolderRename(folderPath)` | Opens the folder-rename modal. Sets`_pendingFolderPath`. Pre-fills the input with the current display name read from `folder_titles[segKey]` on any descendant page in `tree[]`.                                                                                                                                                                                          |
| `doFolderRename()`             | Reads`_pendingFolderPath`. Requires unlock. Attempts `apiGetFile(metaPath)` to obtain the existing `_meta.json` SHA (falls back to `null` for a new file). Calls `apiPutFile` with `{ title }` JSON. Optimistically updates `folder_titles[segKey]` on all pages whose path starts with the folder prefix, then re-renders the sidebar and calls `watchDeploy(metaPath)`. |

**Empty state**


| Function      | Description                                                                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `showEmpty()` | Shows`#empty`. If tree entries have `updated_at`, renders the 5 most recently modified as clickable items; otherwise shows the placeholder icon. |

**Drafts**


| Function                                  | Description                                                                                      |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `saveDraft(path, content)`                | Writes`{ content, ts }` to `localStorage` under `wn_draft_{path}`.                               |
| `loadDraft(path)`                         | Returns parsed draft object or`null`.                                                            |
| `clearDraft(path)`                        | Removes the draft key. Called on successful save and on discard.                                 |
| `saveDraftDebounced`                      | 500 ms debounced wrapper around`saveDraft`. Assigned as the draft-save side-effect in `oninput`. |
| `showDraftBanner()` / `hideDraftBanner()` | Adds/removes`.show` from `#draft-banner`.                                                        |
| `restoreDraft()`                          | Loads draft content into the editor and fires`input` event.                                      |
| `discardDraft()`                          | Calls`clearDraft()` and hides the banner.                                                        |

**Frontmatter**


| Function               | Description                                                                                                                                    |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `parseFrontmatter(md)` | Strips a leading`---…---` block. Returns `{ meta, body }`. Supported keys: `tags` (array or comma-separated string), `author`, `description`. |

**Search**


| Function                         | Description                                                                                                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ensureSearchIndex()`            | Lazily fetches`search.json` into `searchIndex` on first call. No-op thereafter.                                                                                     |
| `openSearch()` / `closeSearch()` | Toggles`#search-overlay`; `openSearch()` triggers `ensureSearchIndex()`.                                                                                            |
| `runSearch(q)`                   | Filters`tree` by title/excerpt (title hits), then extends with `searchIndex` full-content matches (full-text hits). Deduplicates, highlights, limits to 12 results. |
| `searchKey(e)`                   | Closes search on Escape.                                                                                                                                            |

**Page history**


| Function                     | Description                                                                                                                                                                      |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `openHistory()`              | Calls`requireUnlock()` first. Opens modal, calls `fetchHistory()`.                                                                                                               |
| `fetchHistory()`             | GitHub:`ghFetch('commits?path=…&per_page=20')`. GitLab: `glFetch('repository/commits?path=…&per_page=20')`. Normalises to `{ sha, short, message, author, date }`.             |
| `renderHistoryList(commits)` | Renders the commit list with click handlers for`previewCommit()`.                                                                                                                |
| `previewCommit(sha)`         | Fetches file at the given SHA, renders markdown in the modal, offers "Restore this version".                                                                                     |
| `restoreVersion(content)`    | Calls`requireUnlock()`, fetches the current SHA, loads `content` (read from `_pendingRestoreContent`) into the editor with `editorDirty = true`. Calls `_activateEditorPanel()`. |

**Wiki links**


| Constant / Function         | Description                                                                                                                                                                                                                                                                   |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `wikiLinkExtension`         | `marked.js` v9 inline extension. Matches `[[Title]]`. Resolves against `tree` by title or path (case-insensitive). Renders as `<a class="wiki-link">` or `<span class="wiki-link broken">`. Registered via `marked.use({ extensions: [wikiLinkExtension] })` at script start. |
| `initWikiAutocomplete()`    | Attaches`keyup`/`keydown` listeners to `#editor`. On `[[` pattern match, queries `tree` and renders `#wiki-complete` dropdown. Arrow keys navigate, Enter inserts, Escape dismisses.                                                                                          |
| `insertWikiLink(title)`     | Replaces the partial`[[…` text at cursor with `[[title]]`.                                                                                                                                                                                                                   |
| `updateWikiActive()`        | Toggles`.active` class on the currently-selected dropdown item.                                                                                                                                                                                                               |
| `hideWikiComplete()`        | Hides`#wiki-complete`, resets index and items.                                                                                                                                                                                                                                |
| `getOrCreateWikiComplete()` | Lazily creates and appends`#wiki-complete` to `<body>` on first call.                                                                                                                                                                                                         |

**Editor toolbar**


| Function                          | Description                                                                                                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fmt(before, after, placeholder)` | Wraps selection (or inserts placeholder) with`before`/`after`. Used for Bold, Italic, Strikethrough, Inline code, Code block, Link, Image, HR.                   |
| `fmtLine(prefix)`                 | Toggles a line prefix on the current line (e.g.`# `, `## `, `### `, `> `, `- `, `1. `, `- [ ] `). If the line already starts with the prefix, removes it.        |
| `fmtTable()`                      | Calls`fmt()` with a 3-row Markdown table template.                                                                                                               |
| `renderPreviewDebounced`          | 150 ms debounced function that parses frontmatter from the editor value and updates`#view` via `marked.parse()`. Shared by `startEdit()` and `restoreVersion()`. |

**Drag-and-drop image upload**


| Function         | Description                                                                                                                                                                                                                                               |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `initDragDrop()` | Attaches`dragover`, `dragleave`, `drop` listeners to `#editor-wrap`. Guard: no-op if already initialised (`dragDropInit`).                                                                                                                                |
| *(drop handler)* | Filters dropped files to`image/*`. Calls `requireUnlock()`. Reads each file as `ArrayBuffer`, base64-encodes it, calls `apiPutFile('docs/assets/{ts}-{name}', …, null)` to commit the image, inserts `![name](rawUrl)` at the cursor via `setRangeText`. |

**Authentication**


| Function            | Description                                                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `requireUnlock()`   | Returns a Promise. Resolves immediately if`unlocked`; otherwise shows `#pw-overlay` and stores the resolver in `pwResolve`.                                                |
| `submitPw()`        | Hashes the input with`sha256()`. If no `edit_password_hash` or hash matches: sets `unlocked = true`, decrypts token from `localStorage`. Otherwise shows "Wrong password". |
| `closePw()`         | Dismisses`#pw-overlay`.                                                                                                                                                    |
| `checkPassword(pw)` | SHA-256 hashes`pw`, compares to `cfg.edit_password_hash`.                                                                                                                  |
| `encrypt(str, key)` | XOR-obfuscates`str` with `key`, returns base64. If `key` is falsy, returns `str` as-is (plaintext).                                                                        |
| `decrypt(enc, key)` | Inverse of`encrypt`. If `key` is falsy, returns `enc` as-is (symmetric with `encrypt`). If `enc` is falsy, returns `''`.                                                   |

> **Symmetry invariant:** `decrypt(encrypt(s, k), k) === s` for all `s` and `k`, including `k = ''`.

**API layer**


| Function                                  | Description                                                                                                                                                                                    |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ghFetch(path, method, body)`             | Authenticated fetch against`api.github.com/repos/{owner}/{repo}/{path}`. Uses `Authorization: Bearer`. Throws on non-2xx.                                                                      |
| `glFetch(path, method, body)`             | Authenticated fetch against`gitlab.com/api/v4/projects/{owner}%2F{repo}/{path}`. Uses `PRIVATE-TOKEN`. Returns `null` for 204 / DELETE responses.                                              |
| `rawUrl(path)`                            | Returns the correct raw-content URL for the active provider.                                                                                                                                   |
| `apiGetFile(path)`                        | Fetches file metadata via the provider API; normalises to`{ sha, content }`. For GitLab maps `last_commit_id → sha`.                                                                          |
| `apiPutFile(path, message, content, sha)` | Creates (`sha = null`) or updates (with `sha`) a file. GitHub: `PUT contents/`. GitLab: `POST` or `PUT repository/files/`, then re-fetches to get the new `last_commit_id`. Returns `{ sha }`. |
| `apiDeleteFile(path, message, sha)`       | Deletes a file on the active provider.                                                                                                                                                         |
| `normalizeRun(run)`                       | Maps a GitLab pipeline object to the GitHub-shaped`{ id, status, conclusion, html_url }` that `pollActions` and `renderStatus` expect.                                                         |
| `b64enc(s)`                               | UTF-8 → base64 (required by both provider APIs for file content).                                                                                                                             |
| `b64dec(s)`                               | base64 → UTF-8 (for decoding API responses).                                                                                                                                                  |

**CI status**


| Function                      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fetchLatestRun()`            | GitHub:`actions/runs?per_page=3`. GitLab: `pipelines?per_page=3` → `normalizeRun()`. Returns the watched run (by `watchingRunId`) or the latest.                                                                                                                                                                                                                                                                                          |
| `renderStatus(run)`           | Updates`#actions-status` header badge with dot emoji + label + link.                                                                                                                                                                                                                                                                                                                                                                       |
| `pollActions(onDone, onFail)` | Polls every 5 s while run is active; every 30 s otherwise. Calls`onDone` on success conclusion, `onFail` on any non-success conclusion.                                                                                                                                                                                                                                                                                                    |
| `watchDeploy()`               | Called after save / create / delete / rename. Captures`currentPath` as `savedRel`, calls `clearAllTreeStatuses()`, marks the saved file `pending`. Increments `watchDeployGen`; stale loops bail on generation mismatch. Waits (up to 20 × 4 s) for a new CI run, then polls via `pollActions`. On success: marks file `success`, schedules auto-clear after 3.5 s, toasts, calls `loadTree()`. On failure: marks file `failure`, toasts. |

**Settings**


| Function         | Description                                                                                                                                                                                                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `openSettings()` | Renders and opens the settings modal, including a "Display preferences" section with checkboxes pre-populated from`displayPrefs`.                                                                                                                                                        |
| `saveSettings()` | Three-branch token persistence: (1) password provided →`encrypt(token, pw)` → store + unlock; (2) no password hash configured → store token as plaintext + unlock; (3) password hash configured but no password entered → toast error, return. Persists language pref, reloads tree. |

**UI helpers**


| Function            | Description                                                                                                    |
| ------------------- | -------------------------------------------------------------------------------------------------------------- |
| `closeModal()`      | Hides`#modal-overlay`.                                                                                         |
| `toast(msg)`        | Shows a bottom-right auto-dismissing toast for 2.5 s.                                                          |
| `toggleSidebar()`   | Toggles the mobile sidebar and overlay.                                                                        |
| `escHtml(s)`        | Escapes`&`, `<`, `>`, `"` for safe HTML interpolation.                                                         |
| `relativeDate(iso)` | Converts an ISO 8601 date to a human-readable relative string ("just now", "3 hours ago", …).                 |
| `debounce(fn, ms)`  | Standard leading-edge-off debounce. Returns a new function; the original is called after`ms` ms of inactivity. |

---

### `style.css`

No preprocessor. All layout uses CSS Flexbox and Grid.


| Selector                              | Purpose                                                                                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `:root`                               | Light-mode CSS variables (colours, dimensions)                                                                                                                                  |
| `@media (prefers-color-scheme: dark)` | Dark-mode variable overrides                                                                                                                                                    |
| `#layout`                             | Flex row:`#sidebar` + `#content`                                                                                                                                                |
| `#panels`                             | Flex row:`#view-wrap` + `#editor-wrap` + `#toc`                                                                                                                                 |
| `#panels.split`                       | CSS Grid`1fr 1fr`: editor and preview side by side                                                                                                                              |
| `#panels.split #toc`                  | Hidden in split mode                                                                                                                                                            |
| `#panels.split #view-wrap`            | Right border separating preview from editor                                                                                                                                     |
| `#md-toolbar`                         | Flex row with`flex-wrap: wrap`; hidden until `#editor-wrap.edit-active`                                                                                                         |
| `.tb-btn`                             | Toolbar button: 28×28 px, transparent background, hover tinted                                                                                                                 |
| `.tb-sep`                             | 1 px vertical separator between toolbar groups                                                                                                                                  |
| `#draft-banner`                       | Yellow warning bar; shown via`.show` class                                                                                                                                      |
| `.drag-over`                          | Dashed blue outline on`#editor-wrap` during file drag                                                                                                                           |
| `#wiki-complete` / `.wc-item`         | `[[` autocomplete dropdown, positioned via `getBoundingClientRect`                                                                                                              |
| `.wiki-link`                          | Rendered wiki link anchor                                                                                                                                                       |
| `.wiki-link.broken`                   | Red strikethrough for unresolved`[[links]]`                                                                                                                                     |
| `.tag-chip` / `.page-tags`            | Frontmatter tag chips below the page path                                                                                                                                       |
| `.sr-ft-badge`                        | "Full text" badge on search results                                                                                                                                             |
| `.history-list` / `.history-item`     | Commit list in the History modal                                                                                                                                                |
| `.tree-status`                        | Per-file deploy indicator inside a`.tree-row` (right-aligned via `margin-left: auto` on flex parent)                                                                            |
| `.tree-status--pending`               | Pulsing grey`●` via `ts-pulse` keyframe animation                                                                                                                              |
| `.tree-status--success`               | Green`✓`                                                                                                                                                                       |
| `.tree-status--failure`               | Red`✗`                                                                                                                                                                         |
| `.recent-title` / `.recent-item`      | Recently-modified list in the empty state                                                                                                                                       |
| `.page-meta`                          | Author + path line above page content                                                                                                                                           |
| `.field-sep`                          | Horizontal rule inside the settings modal                                                                                                                                       |
| `.toggle-row`                         | Flex row with checkbox + label for display preference toggles                                                                                                                   |
| `@media (max-width: 768px)`           | Mobile: sidebar off-canvas, split collapses to editor-only                                                                                                                      |
| `@media print`                        | Hides all chrome; renders only`#view` with print typography (11 pt, scaled headings, pre-wrap, URL expansion after external links, `break-inside: avoid` on tables/blockquotes) |

---

### `tree.json`

Auto-generated by `build-tree.yml` (GitHub) or the `build-tree` CI job (GitLab). Never edit by hand.

```jsonc
[
  {
    "path": "setup/installation",       // relative to docs/, no .md
    "title": "Installation",            // from first # heading, else capitalised filename
    "excerpt": "WikiNest requires…",    // first non-heading line, max 140 chars
    "parts": ["setup", "installation"], // path.split('/') — used for tree rendering
    "folder_titles": {
      "setup": "Setup & Installation"   // display name from _meta.json
    },
    "updated_at": "2026-05-13T10:22:00+03:00", // ISO 8601, from git log -1 --format=%cI
    "tags": ["ops", "getting-started"], // from frontmatter
    "author": "Alex"                    // from frontmatter
  }
]
```

### `search.json`

Auto-generated alongside `tree.json`. Maps relative page paths to their full raw markdown content.

```jsonc
{
  "setup/installation": "# Installation\n\nWikiNest requires…"
}
```

Fetched lazily on the first search open. Not loaded on page load to avoid a large network request.

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

When `key` is falsy (no password configured), `encrypt` returns `str` unchanged (plaintext) and `decrypt` returns `enc` unchanged — the two functions are symmetric in all cases.

This is **obfuscation, not encryption**. It protects against casual inspection of localStorage and prevents the raw PAT from sitting as a clearly-labelled plaintext value. It does not protect against an attacker who has read access to localStorage and knows the password. For a private internal wiki this is an acceptable trade-off; for high-security contexts, consider replacing with `AES-GCM` via the Web Crypto API.

The PAT is decrypted into memory (`cfg.token`) only after the correct password is entered. It is never written back to localStorage in plaintext when a password is configured.

---

## Security model

### XSS prevention

All user-controlled strings that appear in `innerHTML` are passed through `escHtml()`, which escapes `&`, `<`, `>`, and `"`. Elements that carry dynamic event handlers (e.g. tag chips) are created via the DOM API (`document.createElement`, `.textContent`, `.onclick = fn`) rather than HTML interpolation.

Specific sites hardened:


| Site                              | Fix                                                                                                  |
| --------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Sidebar tree (`renderNode`)       | Page titles and folder names passed through`escHtml()`                                               |
| Breadcrumb                        | Path segments and page title via`escHtml()`                                                          |
| Page-meta line                    | `currentPath` and `meta.author` via `escHtml()`                                                      |
| Tag chips                         | Rebuilt via DOM API;`chip.textContent = tag`                                                         |
| TOC anchors (`buildToc`)          | Text set via`.textContent` not `.innerHTML`                                                          |
| Error toasts / API error messages | `escHtml(e.message)` before interpolation                                                            |
| `_pendingRestoreContent`          | Large version content stored in a module variable rather than embedded in an`onclick="…"` attribute |

### Content Security Policy note

`marked.parse()` writes user-authored markdown into `#view` via `innerHTML`. Malicious content in a page could execute script if the repository is compromised. For highest-security deployments, add DOMPurify (CSP-compatible) as a sanitisation pass between `marked.parse()` and the `innerHTML` assignment. This is a known architectural gap documented in the threat model; it is acceptable for the target use-case of a password-controlled internal wiki.

### Path traversal

`createPage()` and `doRename()` validate the user-supplied path against `/^[a-zA-Z0-9_\-][a-zA-Z0-9_\-\/]*$/` before constructing an API URL. This prevents `../` traversal sequences from reaching the provider API.

### Subresource Integrity

The only CDN dependency (`marked.js`) is loaded with a `sha512` integrity hash and `crossorigin="anonymous"`. All other code is inline in `index.html` (served same-origin from GitHub/GitLab Pages).

### Token lifecycle

1. Editor enters password → SHA-256 hash compared to `cfg.edit_password_hash`
2. On match: `decrypt(localStorage.wn_enc_token, password)` → `cfg.token` (in-memory only)
3. `cfg.token` is passed as `Authorization: Bearer` / `PRIVATE-TOKEN`; never written back to localStorage in plaintext when a password hash is configured
4. Session ends / tab closes → `cfg.token` is garbage-collected; only the encrypted blob remains in localStorage

---

## CI workflows

Both providers run the same Python tree-generation script. The logic is identical; only the CI syntax and push mechanism differ.

**Python script (shared logic)**

1. Walks `docs/`, skips `_meta.json` and files starting with `_`
2. Reads `_meta.json` files for folder `title` aliases
3. Calls `parse_frontmatter()` to extract `tags` and `author` from YAML front matter
4. Extracts `title` from the first `# heading` (else capitalised filename) and `excerpt` from the first non-heading line (max 140 chars)
5. Runs `git log -1 --format=%cI -- {file}` per page to get `updated_at`
6. Writes `tree.json` (array of page objects) and `search.json` (path → raw content dict)

---

### GitHub Actions

**`build-tree.yml`**

Trigger: push to `main` that touches `docs/**`.

1. Checkout with `fetch-depth: 0` — required for `git log` timestamps
2. `git pull origin main`
3. Run Python script → write `tree.json` + `search.json`
4. `git add tree.json search.json && git commit && git push` if either file changed

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
2. Run Python script → write `tree.json` + `search.json`
3. `git commit && git push` if either file changed

Requires a CI/CD variable `GITLAB_TOKEN` with `api` + `write_repository` scope (Settings → CI/CD → Variables).

**`pages` job** — stage: `deploy`

Trigger: every push to the default branch.

1. Copies `index.html`, `style.css`, `config.json`, `tree.json`, `search.json`, `i18n/`, `docs/` into `public/`
2. GitLab Pages serves the `public/` artifact automatically
