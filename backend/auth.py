"""Password verification, role permission checks, and login rate limiting.

roles.json (with password_hash) is loaded server-side only and never sent to
the browser — see /api/roles in app.py, which strips password_hash before
returning. That's the one behavioral change from index.html's model: today
the browser fetches the full roles.json (hashes included) and compares
client-side. Fine when the only way to reach GitHub's write API is a
workflow-dispatch token that lives behind GitHub's own auth; not fine once
the write endpoints are a bare public URL — anyone who loads the page today
can already read every role's hash and crack it offline. Moving the compare
server-side and never shipping the hashes closes that off.
"""
import hashlib
import json
import os
import threading
import time

FULL_ACCESS_ROLES = {'owner', 'admin', 'director', 'head'}
APPEND_ALLOWED_PATHS = {'glossary/index', 'incidents/index'}


def load_roles(data_dir):
    with open(os.path.join(data_dir, 'roles.json'), encoding='utf-8') as fh:
        return json.load(fh)


def sanitize_roles(roles):
    return [{k: v for k, v in r.items() if k != 'password_hash'} for r in roles]


def verify_password(roles, password):
    h = hashlib.sha256(password.encode('utf-8')).hexdigest()
    for role in roles:
        if role.get('password_hash') == h:
            return role
    return None


def find_role(roles, slug):
    return next((r for r in roles if r['slug'] == slug), None)


def can_edit(role):
    return bool(role) and role.get('can_edit') is True


def can_edit_page(role, page):
    """page is a tree.json entry (dict) or None for new/non-page paths."""
    if can_edit(role):
        return True
    if not role or not page:
        return False
    return role['slug'] in (page.get('editors') or [])


def can_append(role):
    return bool(role) and role['slug'] in FULL_ACCESS_ROLES


class LoginRateLimiter:
    """Per-IP sliding-window lockout for /api/login. In-memory — fine for a
    single-process, single-worker deployment (see gunicorn --workers 1 in
    the Dockerfile); a multi-worker setup would need this in shared storage.
    """

    def __init__(self, max_attempts=10, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts = {}  # ip -> [timestamps]
        self._lock = threading.Lock()

    def check(self, ip):
        now = time.time()
        with self._lock:
            attempts = [t for t in self._attempts.get(ip, []) if now - t < self.window_seconds]
            self._attempts[ip] = attempts
            return len(attempts) < self.max_attempts

    def record_failure(self, ip):
        with self._lock:
            self._attempts.setdefault(ip, []).append(time.time())

    def record_success(self, ip):
        with self._lock:
            self._attempts.pop(ip, None)
