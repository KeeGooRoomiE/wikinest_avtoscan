"""Local git operations against the data directory.

The data directory is a checkout of this same repo (see docker-compose.yml).
Every write commits locally and immediately — that's what gives us full
per-edit history and the History modal. Pushing to the GitHub remote is a
separate, slower cadence (see push_loop in app.py): it's the offsite backup,
not the source of truth, so it never blocks a write response.
"""
import subprocess


class GitError(Exception):
    pass


def _run(data_dir, args, check=True, timeout=30):
    result = subprocess.run(
        ['git', '-C', data_dir, *args],
        capture_output=True, text=True, timeout=timeout,
    )
    if check and result.returncode != 0:
        raise GitError(result.stderr.strip() or f'git {" ".join(args)} failed')
    return result.stdout


def mark_safe(data_dir):
    """git refuses to operate on a repo owned by a different UID than the
    running process ("detected dubious ownership") unless the directory is
    explicitly trusted. The container runs as root; /data is a bind mount of
    the host checkout, owned by whatever user cloned it there — always a UID
    mismatch by construction, not a one-off deployment quirk. Must run before
    any other git command against data_dir.
    """
    _run(data_dir, ['config', '--global', '--add', 'safe.directory', data_dir])


def ensure_identity(data_dir, name, email):
    _run(data_dir, ['config', 'user.name', name])
    _run(data_dir, ['config', 'user.email', email])


def commit_paths(data_dir, paths, message):
    """Stages the given paths and commits. No-op (returns False) if nothing changed."""
    _run(data_dir, ['add', '--', *paths])
    unchanged = subprocess.run(
        ['git', '-C', data_dir, 'diff', '--cached', '--quiet'],
    ).returncode == 0
    if unchanged:
        return False  # nothing staged
    _run(data_dir, ['commit', '-m', message])
    return True


def push(data_dir, remote='origin', branch='main'):
    _run(data_dir, ['push', remote, f'HEAD:{branch}'], timeout=60)


def log_for_path(data_dir, rel_path, limit=20):
    """Returns commit history for a path, newest first."""
    sep = '\x1f'
    fmt = f'%H{sep}%h{sep}%s{sep}%an{sep}%cI'
    out = _run(data_dir, ['log', f'-n{limit}', f'--format={fmt}', '--', rel_path], check=False)
    commits = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split(sep)
        if len(parts) != 5:
            continue
        sha, short, subject, author, date = parts
        commits.append({'sha': sha, 'short': short, 'message': subject, 'author': author, 'date': date})
    return commits


def show_at(data_dir, rel_path, sha):
    """Returns file content at a given commit."""
    return _run(data_dir, ['show', f'{sha}:{rel_path}'])


def has_remote_changes(data_dir, remote='origin', branch='main'):
    """True if origin/branch has commits not in local HEAD (i.e. push would be rejected)."""
    _run(data_dir, ['fetch', remote, branch], timeout=60)
    ahead = _run(data_dir, ['rev-list', '--count', f'HEAD..{remote}/{branch}']).strip()
    return ahead != '0'


# Files tree_builder regenerates deterministically from docs/** on every
# write — safe to auto-resolve conflicts in these by keeping our side and
# rebuilding, unlike real content where we cannot guess which side to keep.
_GENERATED_FILES = {'tree.json', 'search.json'}


def sync_before_push(data_dir, remote='origin', branch='main'):
    """Fetch + merge remote into local before pushing, so push never needs
    --force. Returns True if a merge happened (caller should rebuild
    tree.json/search.json and commit), False if already up to date.

    Conflicts limited to tree.json/search.json are auto-resolved (keep
    ours, caller rebuilds after). Any conflict touching real content aborts
    the merge and raises — this repo has two independent write paths
    (this VM, and index.html's direct-to-GitHub path), so a conflict there
    means both sides have real, different edits and picking one
    automatically would silently discard someone's work.
    """
    _run(data_dir, ['fetch', remote, branch], timeout=60)
    ahead = _run(data_dir, ['rev-list', '--count', f'HEAD..{remote}/{branch}']).strip()
    if ahead == '0':
        return False
    result = subprocess.run(
        ['git', '-C', data_dir, 'merge', f'{remote}/{branch}', '--no-edit'],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode == 0:
        return True
    status = _run(data_dir, ['diff', '--name-only', '--diff-filter=U'], check=False)
    conflicted = [l for l in status.splitlines() if l.strip()]
    other = [f for f in conflicted if f not in _GENERATED_FILES]
    if other:
        _run(data_dir, ['merge', '--abort'], check=False)
        raise GitError(f'merge conflict outside generated files: {", ".join(other)} — needs manual resolution')
    for f in conflicted:
        _run(data_dir, ['checkout', '--ours', '--', f])
        _run(data_dir, ['add', '--', f])
    _run(data_dir, ['commit', '--no-edit'])
    return True
