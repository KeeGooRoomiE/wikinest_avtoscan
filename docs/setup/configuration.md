# Configuration

WikiNest is configured through two places: `config.json` in the repository root, and the settings UI in the browser.

## config.json

```json
{
  "site_name": "WikiNest",
  "lang": "en",
  "edit_password_hash": "",
  "owner": "",
  "repo": ""
}
```

This file is public — committed to the repository and visible to anyone. Do not put secrets here.

### Fields

**`site_name`**
Displayed in the header and the browser tab title. Default: `WikiNest`.

**`lang`**
Default UI language. Supported values: `en`, `ru`. Users can override this via the language switcher in the header — their choice is stored in `localStorage`.

**`edit_password_hash`**
SHA-256 hash of the edit password. Set this via the settings UI — it is computed automatically. If empty, no password is required to edit (not recommended for public repositories).

**`owner`** and **`repo`**
Default GitHub owner and repository name. Each user can override these in the settings UI. Useful when distributing WikiNest as a template — set these to point to your repository so users don't need to configure them manually.

## Settings UI

Click the **⚙** icon in the header. Settings are stored in `localStorage` and are browser-specific.

| Setting | Description |
|---|---|
| GitHub owner | Username or organization that owns the repository |
| Repository name | Name of the repository |
| Personal Access Token | PAT with `repo` scope |
| Edit password | Used to encrypt the token and protect the edit UI |
| Site name | Overrides `config.json` locally |

## Password management

### Setting a password

Enter a password in the settings UI and click Save. The hash is computed automatically and stored in `config.json` via a commit. Other users will see the new password requirement after the next page load.

### Changing a password

Open settings → enter a new password → Save. The token is re-encrypted with the new password.

### Resetting a password

If you forget the edit password, generate a new hash via the browser console:

```js
const pw = 'new-password';
const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(pw));
console.log(Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join(''));
```

Then manually update `edit_password_hash` in `config.json` via GitHub's web UI.

## Customizing the accent color

Edit `style.css`:

```css
:root {
  --accent:        #185FA5;
  --accent2:       #0c447c;
  --accent-bg:     #E6F1FB;
  --accent-border: #B5D4F4;
}

@media (prefers-color-scheme: dark) {
  :root {
    --accent:        #58a6ff;
    --accent2:       #85b7eb;
    --accent-bg:     #0c2744;
    --accent-border: #185FA5;
  }
}
```

## Customizing layout dimensions

```css
:root {
  --sidebar-w: 240px;   /* sidebar width */
  --toc-w:     160px;   /* table of contents panel width */
  --header-h:  48px;    /* header height */
}
```
