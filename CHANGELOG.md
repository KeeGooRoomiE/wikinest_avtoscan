# Changelog

All notable changes to WikiNest are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) · Versioning: [Semantic Versioning](https://semver.org/)

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
