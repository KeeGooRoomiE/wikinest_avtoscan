"""Wikinest VM backend — replaces the GitHub/GitLab Actions write path with
direct, synchronous writes against a local git checkout.

See ../BACKEND_ARCHITECTURE.md for the full design. Summary: this process is
the single writer for docs/, tree.json, search.json and roles.json. Every
write is: validate → apply to disk → rebuild tree/search if docs/ changed →
git commit locally → return. Pushing to the GitHub remote happens on its own
timer (see push_loop) and is a backup, not part of the request path.
"""
import base64
import glob
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time

from flask import Flask, jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

import auth
import git_ops
import tree_builder

DATA_DIR = os.environ.get('DATA_DIR', '/data')
DOCS_DIR = os.path.join(DATA_DIR, 'docs')
SECRET_KEY = os.environ['SECRET_KEY']  # fail fast — no safe default for a session-signing key
COMMIT_NAME = os.environ.get('COMMIT_NAME', 'wikinest-backend')
COMMIT_EMAIL = os.environ.get('COMMIT_EMAIL', 'wikinest-backend@localhost')
GIT_REMOTE = os.environ.get('GIT_REMOTE', 'origin')
GIT_BRANCH = os.environ.get('GIT_BRANCH', 'main')
GIT_PUSH_TOKEN = os.environ.get('GIT_PUSH_TOKEN', '')
GIT_PUSH_REPO = os.environ.get('GIT_PUSH_REPO', '')  # "owner/repo", required if GIT_PUSH_TOKEN set
PUSH_INTERVAL_SECONDS = int(os.environ.get('PUSH_INTERVAL_SECONDS', str(24 * 3600)))
COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '1') != '0'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_SECURE=COOKIE_SECURE,
    # Stay under GitHub's hard 100MB per-file push limit — better to reject an
    # oversized upload here, immediately, than have it commit fine locally and
    # only surface as a broken nightly backup push days later.
    MAX_CONTENT_LENGTH=95 * 1024 * 1024,
)
# Caddy sits in front — trust its X-Forwarded-* so rate limiting and any
# logging see the real client IP, not Caddy's container IP.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

write_lock = threading.Lock()
login_limiter = auth.LoginRateLimiter()
sync_state = {'last_push_at': None, 'last_push_error': None}

_PATH_RE = re.compile(r'^[a-zA-Z0-9_\-][a-zA-Z0-9_\-./]*$')


class ApiError(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status


@app.errorhandler(ApiError)
def _handle_api_error(e):
    return jsonify({'error': e.message}), e.status


def _safe_full_path(rel_path):
    if not rel_path or not _PATH_RE.match(rel_path):
        raise ApiError('invalid path')
    full = os.path.normpath(os.path.join(DATA_DIR, rel_path))
    if not (full == os.path.normpath(DATA_DIR) or full.startswith(os.path.normpath(DATA_DIR) + os.sep)):
        raise ApiError('invalid path')
    return full


def _current_role():
    slug = session.get('role_slug')
    if not slug:
        return None
    return auth.find_role(auth.load_roles(DATA_DIR), slug)


def _require_role():
    role = _current_role()
    if not role:
        raise ApiError('not authenticated', 401)
    return role


def _require_can_edit():
    role = _require_role()
    if not auth.can_edit(role):
        raise ApiError('forbidden', 403)
    return role


def _load_tree():
    import json
    tree_path = os.path.join(DATA_DIR, 'tree.json')
    if not os.path.exists(tree_path):
        return []
    with open(tree_path, encoding='utf-8') as fh:
        return json.load(fh)


def _find_page(tree, rel_path):
    """rel_path like 'docs/foo/bar.md' -> tree entry with path 'foo/bar', or None."""
    if not (rel_path.startswith('docs/') and rel_path.endswith('.md')):
        return None
    page_path = rel_path[len('docs/'):-3]
    return next((p for p in tree if not p.get('_folder') and p['path'] == page_path), None)


# ── Auth ──────────────────────────────────────────────────────────────────

@app.post('/api/login')
def login():
    ip = request.remote_addr or 'unknown'
    if not login_limiter.check(ip):
        raise ApiError('too many attempts, try again later', 429)
    body = request.get_json(silent=True) or {}
    password = body.get('password', '')
    roles = auth.load_roles(DATA_DIR)
    role = auth.verify_password(roles, password)
    if not role:
        login_limiter.record_failure(ip)
        raise ApiError('invalid password', 401)
    login_limiter.record_success(ip)
    session.clear()
    session['role_slug'] = role['slug']
    session.permanent = True
    return jsonify({'role': {k: v for k, v in role.items() if k != 'password_hash'}})


@app.post('/api/logout')
def logout():
    session.clear()
    return jsonify({'ok': True})


@app.get('/api/me')
def me():
    role = _current_role()
    return jsonify({'role': ({k: v for k, v in role.items() if k != 'password_hash'} if role else None)})


@app.get('/api/roles')
def list_roles():
    _require_role()
    return jsonify(auth.sanitize_roles(auth.load_roles(DATA_DIR)))


@app.post('/api/roles/visibility')
def roles_visibility():
    """Toggles hidden_sections for a folder across a set of roles, without
    ever round-tripping the full roles.json (and its password hashes)
    through the client. Body: {folder_key, roles: {slug: visible_bool}}.
    """
    _require_can_edit()
    body = request.get_json(silent=True) or {}
    folder_key = body.get('folder_key')
    changes = body.get('roles') or {}
    if not folder_key or not isinstance(changes, dict):
        raise ApiError('folder_key and roles are required')

    roles = auth.load_roles(DATA_DIR)
    for slug, visible in changes.items():
        role = auth.find_role(roles, slug)
        if not role:
            continue
        hs = role.get('hidden_sections', [])
        if visible:
            role['hidden_sections'] = [s for s in hs if s != folder_key]
        elif folder_key not in hs:
            role['hidden_sections'] = [*hs, folder_key]

    import json
    with write_lock:
        with open(os.path.join(DATA_DIR, 'roles.json'), 'w', encoding='utf-8') as fh:
            json.dump(roles, fh, ensure_ascii=False, indent=2)
        git_ops.commit_paths(DATA_DIR, ['roles.json'], 'chore: update section visibility')

    return jsonify(auth.sanitize_roles(roles))


# ── Writes ────────────────────────────────────────────────────────────────

@app.post('/api/write/put_file')
def put_file():
    role = _require_role()
    body = request.get_json(silent=True) or {}
    rel_path = body.get('path', '')
    message = body.get('message', 'docs: update')
    content = body.get('content', '')
    encoding = body.get('encoding', 'text')

    if rel_path in ('roles.json',):
        raise ApiError('roles.json must be edited via /api/roles/visibility', 403)

    tree = _load_tree()
    page = _find_page(tree, rel_path)
    if page is not None:
        if not auth.can_edit_page(role, page):
            raise ApiError('forbidden', 403)
    else:
        if not auth.can_edit(role):
            raise ApiError('forbidden', 403)

    full = _safe_full_path(rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)

    with write_lock:
        if encoding == 'base64':
            with open(full, 'wb') as fh:
                fh.write(base64.b64decode(content))
        else:
            with open(full, 'w', encoding='utf-8') as fh:
                fh.write(content)

        commit_paths = [rel_path]
        if rel_path.startswith('docs/'):
            tree_builder.rebuild(DATA_DIR)
            commit_paths += ['tree.json', 'search.json']
        git_ops.commit_paths(DATA_DIR, commit_paths, message)

    return jsonify({'ok': True})


@app.post('/api/write/delete_file')
def delete_file():
    role = _require_can_edit()
    body = request.get_json(silent=True) or {}
    rel_path = body.get('path', '')
    message = body.get('message', 'docs: delete')

    full = _safe_full_path(rel_path)

    with write_lock:
        if os.path.exists(full):
            os.remove(full)

        commit_paths = [rel_path]
        if rel_path.startswith('docs/'):
            tree_builder.rebuild(DATA_DIR)
            commit_paths += ['tree.json', 'search.json']
        git_ops.commit_paths(DATA_DIR, commit_paths, message)

    return jsonify({'ok': True})


@app.post('/api/write/upload')
def upload_file():
    """Binary uploads (images, video) — multipart, not base64-in-JSON like
    put_file. Werkzeug spools the incoming file to a temp file during
    multipart parsing and FileStorage.save() streams it to its final path, so
    this never holds the whole upload in memory as a Python string the way
    base64-encoding it for put_file would. Images or short clips for docs —
    not a page's tree.json rebuild concern, so no tree_builder.rebuild() here.
    """
    _require_can_edit()
    rel_path = request.form.get('path', '')
    message = request.form.get('message', 'docs: upload file')
    if 'file' not in request.files:
        raise ApiError('no file provided')

    full = _safe_full_path(rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)

    with write_lock:
        request.files['file'].save(full)
        git_ops.commit_paths(DATA_DIR, [rel_path], message)

    return jsonify({'ok': True})


@app.post('/api/write/convert_docx')
def convert_docx():
    """Convert an uploaded .docx to GFM markdown via pandoc.
    Extracts embedded images to docs/assets/ and rewrites their paths in the
    returned markdown.  The markdown is NOT written to docs/ — the client
    opens it in the editor for review, then saves via put_file.
    """
    _require_can_edit()
    if 'file' not in request.files:
        raise ApiError('no file provided')
    f = request.files['file']
    if not (f.filename or '').lower().endswith('.docx'):
        raise ApiError('only .docx files are supported')

    tmpdir = tempfile.mkdtemp()
    try:
        input_path = os.path.join(tmpdir, 'input.docx')
        output_path = os.path.join(tmpdir, 'output.md')
        f.save(input_path)

        result = subprocess.run(
            ['pandoc', '--from=docx', '--to=gfm',
             f'--extract-media={tmpdir}',
             '-o', output_path, input_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise ApiError(f'pandoc: {result.stderr[:500]}')

        with open(output_path, encoding='utf-8') as fh:
            md = fh.read()

        images = []
        media_dir = os.path.join(tmpdir, 'media')
        if os.path.exists(media_dir):
            assets_dir = os.path.join(DOCS_DIR, 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            ts = int(time.time())
            git_paths = []
            for idx, img in enumerate(
                sorted(glob.glob(os.path.join(media_dir, '**', '*'), recursive=True)), start=1
            ):
                if not os.path.isfile(img):
                    continue
                orig_name = os.path.basename(img)
                dest_name = f'{ts}-{idx}-{orig_name}'
                shutil.copy2(img, os.path.join(assets_dir, dest_name))
                # pandoc writes refs relative to tmpdir (e.g. "media/image1.png")
                old_ref = os.path.relpath(img, tmpdir).replace(os.sep, '/')
                new_ref = f'/docs/assets/{dest_name}'
                md = md.replace(f']({old_ref})', f']({new_ref})')
                md = md.replace(f'src="{old_ref}"', f'src="{new_ref}"')
                rel_asset = f'docs/assets/{dest_name}'
                images.append(rel_asset)
                git_paths.append(rel_asset)

            if git_paths:
                with write_lock:
                    git_ops.commit_paths(DATA_DIR, git_paths, 'docs: upload docx images')

        return jsonify({'markdown': md, 'images': images})
    except ApiError:
        raise
    except Exception as e:
        raise ApiError(f'conversion failed: {str(e)[:300]}')
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.post('/api/write/append_row')
def append_row():
    role = _require_role()
    if not auth.can_append(role):
        raise ApiError('forbidden', 403)
    body = request.get_json(silent=True) or {}
    rel_path = body.get('path', '')
    message = body.get('message', 'docs: append row')
    section_name = body.get('section_name', '')
    new_row = body.get('new_row', '')

    page_path = rel_path[len('docs/'):-3] if rel_path.startswith('docs/') and rel_path.endswith('.md') else ''
    if page_path not in auth.APPEND_ALLOWED_PATHS:
        raise ApiError('forbidden', 403)

    full = _safe_full_path(rel_path)

    with write_lock:
        with open(full, encoding='utf-8') as fh:
            md = fh.read()

        lines = md.split('\n')
        sec_idx = -1
        for i, line in enumerate(lines):
            m = re.match(r'^##\s+(.+)', line)
            if m and m.group(1).strip() == section_name:
                sec_idx = i
                break
        if sec_idx < 0:
            raise ApiError(f'section not found: {section_name!r}')

        last_table = -1
        for i in range(sec_idx + 1, len(lines)):
            if re.match(r'^##\s', lines[i]):
                break
            if lines[i].startswith('|'):
                last_table = i
        insert_at = last_table + 1 if last_table >= 0 else sec_idx + 1
        lines.insert(insert_at, new_row)

        with open(full, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines))

        tree_builder.rebuild(DATA_DIR)
        git_ops.commit_paths(DATA_DIR, [rel_path, 'tree.json', 'search.json'], message)

    return jsonify({'ok': True})


# ── History ───────────────────────────────────────────────────────────────

@app.get('/api/history')
def history():
    _require_can_edit()
    rel_path = request.args.get('path', '')
    _safe_full_path(rel_path)  # validates, raises on traversal
    return jsonify(git_ops.log_for_path(DATA_DIR, rel_path))


@app.get('/api/history/content')
def history_content():
    _require_can_edit()
    rel_path = request.args.get('path', '')
    sha = request.args.get('sha', '')
    _safe_full_path(rel_path)
    if not re.match(r'^[0-9a-f]{7,40}$', sha):
        raise ApiError('invalid sha')
    try:
        content = git_ops.show_at(DATA_DIR, rel_path, sha)
    except git_ops.GitError as e:
        raise ApiError(str(e), 404)
    return jsonify({'content': content})


# ── Sync status / manual push ────────────────────────────────────────────

@app.get('/api/sync/status')
def sync_status():
    _require_can_edit()
    return jsonify(sync_state)


@app.post('/api/sync/push')
def sync_push():
    _require_can_edit()
    ok, err = _do_push()
    if not ok:
        raise ApiError(err or 'push failed', 502)
    return jsonify(sync_state)


@app.get('/healthz')
def healthz():
    return jsonify({'ok': True})


# ── Background push loop ─────────────────────────────────────────────────

def _do_push():
    try:
        git_ops.push(DATA_DIR, GIT_REMOTE, GIT_BRANCH)
        sync_state['last_push_at'] = time.time()
        sync_state['last_push_error'] = None
        return True, None
    except git_ops.GitError as e:
        sync_state['last_push_error'] = str(e)
        app.logger.error('git push failed: %s', e)
        return False, str(e)


def _push_loop():
    while True:
        time.sleep(PUSH_INTERVAL_SECONDS)
        with write_lock:
            _do_push()


def _configure_git_remote():
    if not GIT_PUSH_TOKEN:
        app.logger.warning('GIT_PUSH_TOKEN not set — backup push to GitHub is disabled')
        return False
    if not GIT_PUSH_REPO:
        raise RuntimeError('GIT_PUSH_REPO ("owner/repo") is required when GIT_PUSH_TOKEN is set')
    url = f'https://x-access-token:{GIT_PUSH_TOKEN}@github.com/{GIT_PUSH_REPO}.git'
    import subprocess
    subprocess.run(['git', '-C', DATA_DIR, 'remote', 'set-url', GIT_REMOTE, url], check=True)
    return True


def _startup():
    logging.basicConfig(level=logging.INFO)
    git_ops.ensure_identity(DATA_DIR, COMMIT_NAME, COMMIT_EMAIL)
    if _configure_git_remote():
        threading.Thread(target=_push_loop, daemon=True).start()


_startup()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
