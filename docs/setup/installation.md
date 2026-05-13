# Installation

WikiNest requires no build step. Fork the repository, enable GitHub Pages, configure your token — done in under 5 minutes.

## Requirements

- A GitHub account
- A repository with GitHub Pages enabled
- A Personal Access Token with `repo` scope

## Step-by-step

### 1. Fork the repository

Go to [github.com/KeeGooRoomiE/wikinest](https://github.com/KeeGooRoomiE/wikinest) and click **Fork**.

### 2. Enable GitHub Pages

In your forked repository go to **Settings → Pages → Source** and select **GitHub Actions**.

### 3. Set workflow permissions

Go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**. This allows the Actions bot to commit the generated `tree.json`.

### 4. Create a Personal Access Token

Go to **GitHub → Settings → Developer settings → Personal access tokens (classic) → Generate new token**.

Select scope: `repo` ✓

Copy the token — you won't see it again.

### 5. Open the wiki

After the first Actions run completes (~1 min), open your site:

```
https://<your-username>.github.io/wikinest/
```

### 6. Configure WikiNest

Click the **⚙** icon and fill in:

| Field | Value |
|---|---|
| GitHub owner | Your GitHub username or org |
| Repository name | `wikinest` (or your fork's name) |
| Personal Access Token | The token from step 4 |
| Edit password | Any password you choose |

Click **Save**. The sidebar will populate with pages from `docs/`.

## Updating WikiNest

Pull changes from the upstream repository and push to your fork. The Actions workflow handles the rest.

```bash
git remote add upstream https://github.com/KeeGooRoomiE/wikinest.git
git fetch upstream
git merge upstream/main
git push
```
