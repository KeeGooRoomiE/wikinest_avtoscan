# Contributing to WikiNest

Thanks for taking the time to contribute.

For small fixes (typos, one-liners, docs), open a PR directly. For anything larger — new features, layout changes, workflow modifications — open an issue first to align on approach before writing code.

---

## Setup

No build step, no package manager.

```bash
git clone https://github.com/KeeGooRoomiE/wikinest.git
cd wikinest
```

Open `index.html` in a browser. For GitHub API calls to work, configure your own fork in the ⚙ settings (owner, repo, PAT).

That's it.

---

## Project layout

```
index.html          ← all app logic (one file, vanilla JS)
style.css           ← all styles (CSS variables, Flexbox/Grid, dark mode)
config.json         ← site config, committed to repo, never contains secrets
tree.json           ← auto-generated page index, do not edit by hand
i18n/en.json        ← English UI strings
i18n/ru.json        ← Russian UI strings
docs/               ← wiki content (markdown pages)
.github/workflows/  ← build-tree.yml, deploy.yml
ARCHITECTURE.md     ← full function map, data flow, security model
CHANGELOG.md        ← version history
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for a full function reference and data-flow diagram.

---

## Commit style

```
type: short description
```

| Type | When to use |
|---|---|
| `feat` | New user-visible feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | CSS or formatting, no logic change |
| `chore` | Workflow, tooling, housekeeping |
| `i18n` | Translation additions or corrections |

Examples:
```
feat: add page rename
fix: update currentSha from PUT response
docs: update ARCHITECTURE function table
chore: add updated_at to build-tree.yml
```

---

## Code conventions

**JavaScript**
- Vanilla ES2020+. No TypeScript, no transpiler, no bundler.
- No external libraries beyond `marked.js` (already on CDN). Do not add new CDN scripts without discussion.
- Keep all logic in `index.html`. Do not split into modules — the single-file constraint is intentional.
- No comments explaining *what* the code does. Only add a comment for a non-obvious *why*: a hidden constraint, a CDN quirk, a spec edge case.

**CSS**
- All colors via CSS variables defined in `:root`. Do not hardcode color values.
- Dark mode via `@media (prefers-color-scheme: dark)` — override variables only, no duplicate rules.
- Layout with Flexbox or Grid. No `position: absolute` for layout.

**i18n**
- Every new UI string needs entries in both `i18n/en.json` and `i18n/ru.json`.
- Key names are in English, snake_case. Values in `en.json` are the canonical strings.
- Access strings with `t('key')`, which falls back to the key name if the string is missing.

**Security**
- The PAT and password must never appear in plaintext in `localStorage`, DOM, or console output.
- Do not add new `fetch()` calls to third-party origins.
- Any new feature that touches auth flow needs explicit review.

---

## Before opening a PR

- [ ] Tested in Chrome and Firefox (Safari if possible)
- [ ] Tested in dark mode (`prefers-color-scheme: dark` via devtools)
- [ ] Tested on a narrow viewport (≤ 768 px)
- [ ] Added i18n keys to both `en.json` and `ru.json`
- [ ] No hardcoded colors or strings outside i18n

---

## Adding a language

1. Copy `i18n/en.json` to `i18n/<lang>.json`
2. Translate all values (keys stay in English)
3. Add `<option value="<lang>">XX</option>` to `#lang-switcher` in `index.html`
4. Test by switching to the new language in the UI

Do not add machine-translated strings unless they have been reviewed by a native speaker.

---

## Modifying the GitHub Actions workflows

`build-tree.yml` and `deploy.yml` run with `contents: write` permission. Changes to these files are reviewed carefully. In particular:
- Do not add steps that make outbound network requests to non-GitHub hosts
- Do not store secrets in workflow files; use repository secrets if needed
- Test workflow changes by pushing to a fork before opening a PR against `main`

---

## Reporting bugs

Open a GitHub issue. Include:
- What you expected to happen
- What actually happened
- Browser and OS
- Steps to reproduce (minimal)

If the bug is security-related (e.g., PAT exposure), **do not open a public issue** — email the maintainer directly.
