"""Rebuilds tree.json + search.json from docs/.

In-process port of the tree/search rebuild step that used to run as a
GitHub Actions / GitLab CI job (see .github/workflows/build-tree.yml and
the build-tree stage in .gitlab-ci.yml). Same algorithm, two differences:

- updated_at comes from filesystem mtime instead of `git log -1` per file
  (no subprocess per file — the backend is the only writer, so mtime is
  accurate the moment a write lands).
- roles[] / editors[] / isCounting are carried forward from the previous
  tree.json instead of being dropped. The CI script rebuilt tree.json from
  scratch on every docs/ change, which silently wiped any values set only
  through the visibility/editors modals (those fields don't exist in
  frontmatter, so a from-scratch rebuild had nothing to derive them from).
"""
import json
import os
import re
from datetime import datetime, timezone


def _parse_frontmatter(text):
    meta = {}
    body = text
    m = re.match(r'^---\r?\n([\s\S]*?)\r?\n---\r?\n?', text)
    if m:
        body = text[len(m.group(0)):]
        for line in m.group(1).splitlines():
            kv = re.match(r'^(\w[\w-]*):\s*(.*)$', line)
            if not kv:
                continue
            k, v = kv.group(1), kv.group(2).strip()
            if v.startswith('['):
                try:
                    meta[k] = json.loads(v.replace("'", '"'))
                except Exception:
                    meta[k] = [s.strip() for s in v[1:-1].split(',') if s.strip()]
            else:
                meta[k] = v.strip('"\'')
        if isinstance(meta.get('tags'), str):
            meta['tags'] = [s.strip() for s in meta['tags'].split(',') if s.strip()]
    return meta, body


def _titlecase(s):
    return s.replace('-', ' ').replace('_', ' ').capitalize()


def rebuild(data_dir):
    """Walks {data_dir}/docs, writes tree.json + search.json into data_dir.

    Returns (page_count, search_count).
    """
    docs_dir = os.path.join(data_dir, 'docs')
    tree_path = os.path.join(data_dir, 'tree.json')

    # Carry forward UI-only fields (roles/editors/isCounting) keyed by path.
    prev_by_path = {}
    if os.path.exists(tree_path):
        try:
            with open(tree_path, encoding='utf-8') as fh:
                for entry in json.load(fh):
                    if not entry.get('_folder'):
                        prev_by_path[entry['path']] = entry
        except Exception:
            pass

    tree = []
    search = {}
    folder_meta = {}

    for root, dirs, files in os.walk(docs_dir):
        dirs.sort()
        if '_meta.json' in files:
            meta_path = os.path.join(root, '_meta.json')
            with open(meta_path, encoding='utf-8') as fh:
                try:
                    meta = json.load(fh)
                    rel_dir = os.path.relpath(root, docs_dir).replace('\\', '/')
                    folder_meta[rel_dir] = meta
                except Exception:
                    pass

        for f in sorted(files):
            if not f.endswith('.md') or f.startswith('_'):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, docs_dir).replace('\\', '/')
            path = rel[:-3]
            parts = path.split('/')

            with open(full, encoding='utf-8') as fh:
                raw_content = fh.read()

            fm_meta, body = _parse_frontmatter(raw_content)
            tags = fm_meta.get('tags', [])
            author = fm_meta.get('author', '')
            is_counting = fm_meta.get('isCounting', 'false').lower() not in ('false', '0', 'no', '') \
                if isinstance(fm_meta.get('isCounting'), str) \
                else bool(fm_meta.get('isCounting', False))

            title = _titlecase(parts[-1])
            excerpt = ''
            in_code_block = False
            for line in body.splitlines():
                stripped = line.strip()
                if stripped.startswith('```') or stripped.startswith('~~~'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
                if stripped.startswith('# '):
                    title = stripped[2:].strip()
                    break
                elif stripped and not stripped.startswith('#') and not excerpt:
                    excerpt = stripped[:140]

            folder_titles = {}
            for i in range(len(parts) - 1):
                folder_path = '/'.join(parts[:i + 1])
                meta = folder_meta.get(folder_path, {})
                folder_titles[parts[i]] = meta.get('title', _titlecase(parts[i]))

            mtime = os.path.getmtime(full)
            updated_at = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

            prev = prev_by_path.get(path, {})
            entry = {
                'path': path, 'title': title, 'excerpt': excerpt,
                'parts': parts, 'folder_titles': folder_titles,
                'updated_at': updated_at, 'tags': tags, 'author': author,
                'isCounting': fm_meta.get('isCounting') is not None and is_counting or prev.get('isCounting', is_counting),
            }
            if prev.get('roles'):
                entry['roles'] = prev['roles']
            if prev.get('editors'):
                entry['editors'] = prev['editors']

            if 'glossary' in parts:
                entry['termCount'] = len(re.findall(r'^\|\s*\*\*', body, re.MULTILINE))
            if 'incidents' in parts and parts[-1] == 'index':
                count = 0
                expect = None  # 'header' then 'sep' then data rows
                for line in body.splitlines():
                    if re.match(r'^##\s', line):
                        expect = 'header'
                        continue
                    if not line.startswith('|'):
                        continue
                    if expect == 'header':
                        expect = 'sep'
                        continue
                    if expect == 'sep':
                        expect = None
                        continue
                    count += 1
                entry['incidentCount'] = count
            tree.append(entry)

            search[path] = raw_content

    def page_sort_key(entry):
        parts = entry['parts']
        key = []
        for depth in range(len(parts)):
            parent = '/'.join(parts[:depth]) if depth > 0 else '.'
            part = parts[depth]
            meta = folder_meta.get(parent, {})
            pages_order = meta.get('pages', [])
            if part in pages_order:
                key.append((0, pages_order.index(part), part))
            else:
                key.append((1, 0, part))
        return key

    tree.sort(key=page_sort_key)

    # Add _folder marker entries — same logic as build-tree.yml bot:
    # add marker if folder is empty (no pages) OR explicitly listed in parent's pages[].
    # Sort by pages[] order so sidebar respects _meta.json ordering even for empty folders.
    def folder_marker_key(item):
        rd = item[0]
        parts = rd.split('/')
        key = []
        for i in range(len(parts)):
            parent = '/'.join(parts[:i]) if i > 0 else '.'
            part = parts[i]
            m = folder_meta.get(parent, {})
            pages_ord = m.get('pages', [])
            if part in pages_ord:
                key.append((0, pages_ord.index(part), part))
            else:
                key.append((1, 0, part))
        return key

    page_paths = {e['path'] for e in tree}
    for rel_dir, meta in sorted(folder_meta.items(), key=folder_marker_key):
        if rel_dir == '.':
            continue
        parts = rel_dir.split('/')
        has_child = any(p == rel_dir or p.startswith(rel_dir + '/') for p in page_paths)
        parent_dir = '/'.join(parts[:-1]) if len(parts) > 1 else '.'
        in_parent_pages = parts[-1] in folder_meta.get(parent_dir, {}).get('pages', [])
        if not has_child or in_parent_pages:
            ft = {}
            for i in range(len(parts) - 1):
                parent = '/'.join(parts[:i + 1])
                m = folder_meta.get(parent, {})
                ft[parts[i]] = m.get('title', _titlecase(parts[i]))
            tree.append({
                '_folder': True,
                'path': rel_dir,
                'title': meta.get('title', _titlecase(parts[-1])),
                'parts': parts,
                'folder_titles': ft,
            })

    with open(tree_path, 'w', encoding='utf-8') as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, 'search.json'), 'w', encoding='utf-8') as f:
        json.dump(search, f, ensure_ascii=False)

    return len(tree), len(search)
