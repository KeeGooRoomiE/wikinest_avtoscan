# CLAUDE.md — Wikinest Автоскан

Инструкции для Claude Code при работе в этом репозитории.

Для других агентных инструментов (OpenAI Codex CLI и аналоги, читающие `AGENTS.md`) есть [AGENTS.md](AGENTS.md) — короткий шлюз с самыми критичными правилами, отсылающий сюда за подробностями. При правке критичных правил в этом файле проверяйте, не устарел ли `AGENTS.md`.

---

## Проект

Внутренняя база знаний компании **Автоскан** на движке WikiNest.
Репозиторий: `KeeGooRoomiE/wikinest_avtoscan` · ветка `main`.
Стек: `index.html` (весь JS внутри) + `style.css` + `docs/*.md` + `tree.json`.

**Два параллельных пути хостинга — см. «Два пути» ниже.** GitHub Pages (`index.html`) остаётся аварийным фолбэком; основной путь ежедневной работы — VM (`docs.html` + `backend/`).

Архитектура (GitHub/GitLab CI, `index.html`): [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)
Архитектура бэкенда (VM, `docs.html`): [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)
Деплой на VM: [DEPLOYMENT.md](DEPLOYMENT.md)
Контроль доступа: [ACCESS_CONTROL.md](ACCESS_CONTROL.md)

---

## Два пути — index.html и docs.html

`docs.html` — копия `index.html` с другим API-слоем (same-origin вызовы к `backend/` вместо GitHub/GitLab Actions). Рендеринг, роли, поиск, редактор, модалки — идентичны в обоих файлах.

**Правило:** любое изменение в общей логике (не в API-слое — в рендеринге дерева, ролях, поиске, редакторе, модалках) нужно вносить в **оба** файла. Изменения непосредственно в способе чтения/записи (fetch к GitHub API vs fetch к `/api/*`) — только в соответствующий файл, во втором ничего не трогать.

**Осознанное исключение из этого правила:** drag-and-drop реордер дерева (тумблер «Редактировать структуру» у «РАЗДЕЛЫ») существует только в `docs.html`. Причина не в лени, а в стоимости записи на git-пути — см. [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md#удаление-переименование-реордер-папок-2026-07). Кнопки переименования/удаления папки в этом тумблере — обычная общая логика, есть в обоих файлах как всегда.

Что именно отличается между файлами и почему — таблица в [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md#два-независимых-пути).

---

## Правила работы с tree.json

Это всё — про GitHub/GitLab CI путь (`index.html`). На VM-пути (`docs.html`) `tree.json` пересобирает сам бэкенд синхронно при записи (`backend/tree_builder.py`), никакого бота и конфликтов при мерже нет — см. [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md).

**Бот (GitHub Actions `build-tree.yml`) автоматически перегенерирует `tree.json` на каждый пуш в `docs/**`.** Это создаёт конфликт. Паттерн разрешения:

```bash
git fetch origin
git merge origin/main --strategy-option=ours -m "merge: sync with bot"
git push
```

`--strategy-option=ours` — при конфликте побеждает **наша** версия `tree.json`.

### Что бот делает неправильно
- Ставит `folder_titles` на английском (`"templates": "Templates"`)
- Может взять неверный заголовок если в `.md` файле есть `# H1` в примере кода (вне code block)
- Добавляет ghost-записи при перемещении файлов — нужно чистить вручную

### Правила tree.json вручную
- Русские `folder_titles` всегда проставлять вручную после бота
- При перемещении файла — удалять старую запись из tree.json, добавлять новую
- `excerpt` брать из первой значимой строки `.md` файла

---

## Безопасность

- **Пароли** — только SHA-256 хеши в `roles.json`. Plaintext **никогда** не коммитить.
- **CREDENTIALS.md** — в `.gitignore`, не пушить ни при каких обстоятельствах.
- **PAT GitHub** — хранится в memory (session). В repo не хранить.
- **Inline onclick с JSON.stringify** — критически опасный паттерн, ломает клики если строка содержит `"`. Всегда использовать DOM event listeners для динамических списков.
- **`index.html` шлёт `roles.json` целиком (с `password_hash`) в браузер** — так и должно быть на этом пути (сравнение пароля клиентское, единственный путь к записи — GitHub-токен за GitHub-аутентификацией). На VM-пути (`docs.html`) это закрыто иначе: пароль сверяется на сервере, `GET /api/roles` хеши не отдаёт вообще. Не переносить обратно в `docs.html` паттерн с полным roles.json — там эндпоинты публичные.

---

## UI и стили

- **Тёмная тема удалена** целиком. Не добавлять обратно: ни `@media (prefers-color-scheme: dark)`, ни `[data-theme="dark"]`.
- **Поле поиска** — `autocomplete="new-password" name="search_q"` обязательно (иначе браузер предлагает сохранить пароль).
- **Динамические списки** (поиск, избранное, недавние) — строить через `document.createElement` + `div.onclick = () => {...}`, не через `innerHTML` с `onclick=""`.

---

## Структура ролей

Файл `roles.json`, 9 ролей (модель с 2026-07-21): `owner`, `admin` (оба `can_edit: true`, полный доступ), `director`, `head`, `support`, `sales`, `accounting`, `office-manager`, `service`.

Ключевые правила (детали — [ACCESS_CONTROL.md](ACCESS_CONTROL.md)):
- `FULL_ACCESS_ROLES = ['owner','admin']` — только эти двое обходят все `roles[]`-ограничения. `owner` не показывается ни в одном чеклисте; `admin` показывается всегда с несъёмной галочкой (`FORCED_ROLE`).
- Остальные роли — обычные, ограничиваемые: видимость и редактирование задаются per-страница (`roles[]`/`editors[]` в tree.json) и per-папка (`roles[]` в `_meta.json`, каскадно на содержимое).
- Роль из `editors[]` видит страницу автоматически и может управлять её видимостью/редакторами.
- `hidden_sections` — legacy, очищен у всех ролей, новые ограничения через него не делать.
- Пароль каждой роли уникален — логин определяет роль по хешу, дубликат пароля делает роль недостижимой.

---

## Структура навигации (tree.json разделы)

Разделы = массив `SECTIONS` в docs.html/index.html (порядок и названия — оттуда):

| Раздел в UI | slug/folder | Путь docs/ |
|-------------|-------------|------------|
| Компания | `company` | `docs/company/` |
| Продукты | `products` | `docs/products/` |
| Оборудование | `devices` | `docs/devices/` |
| Процессы | `processes` | `docs/processes/` |
| Регламенты | `reglamentation` | `docs/reglamentation/` |
| Инциденты и решения | `incidents` (direct → `incidents/index`) | `docs/incidents/` |
| Сервисы и инструменты | `software` | `docs/software/` |
| Шаблоны и памятки | `reference` (+extraFolder `examples`) | `docs/reference/`, `docs/examples/` |
| Глоссарий | `glossary` (direct → `glossary/index`) | `docs/glossary/` |

---

## Важные функции index.html

| Функция | Назначение |
|---------|-----------|
| `openFavoritesView()` | Попап избранного — DOM listeners, не inline onclick |
| `openRecentView()` | Попап недавних — аналогично |
| `runSearch(q)` | Поиск — DOM listeners, `window._searchHighlight = q` для подсветки |
| `highlightInView(q)` | Подсвечивает текст в открытой странице тегами `<mark>` |
| `injectBirthdayBanner(el)` | Парсит 🎂 колонку таблицы контактов, показывает ближайшие ДР |
| `openPage(page)` | После рендера: если `window._searchHighlight` — подсвечивает и скроллит |
| `FULL_ACCESS_ROLES` | `['owner','admin','director','head']` — полный доступ, игнор hidden_sections |
| `canEdit()` | `currentRole?.can_edit === true` |
| `canEditPage(page)` | Проверяет `editors[]` страницы ИЛИ `can_edit` |
| `toggleEditTreeMode()` | Тумблер у «РАЗДЕЛЫ»: 1-й клик — режим редактирования дерева, 2-й — применяет накопленные перестановки одним `apiReorder` (только `docs.html`; в `index.html` тот же тумблер только показывает/прячет кнопки папок, без применения) |
| `addFolderActions(hdrEl, path, title)` | Вешает кнопки «Переименовать»/«Удалить» на заголовок папки — видны только при `editTreeMode` |
| `openRenameFolder(path, title)` / `doRenameFolder(path)` | Модалка переименования — меняет только `_meta.json.title`, путь папки не трогается |
| `deleteFolderConfirm(path, title)` / `doDeleteFolder(path)` | Модалка + рекурсивное удаление папки. На `docs.html` — один вызов `apiDeleteFolder`; на `index.html` — последовательные `apiDeleteFile` по всем найденным в `tree` записям под этим путём |
| `makeSortable(container, onDrop)` | Нативный HTML5 drag-and-drop без библиотек — только `docs.html`, см. «Два пути» выше |

---

## Файл контактов

`docs/contacts.md` и `docs/company/contacts.md` — идентичны.
Колонки: `| 📞 | ФИО | Должность | Рабочий | Личный | Почта | 🎂 |`
Лидеры секций — строки полностью жирные (кроме 🎂).
Офисные телефоны — вне таблиц, над каждой секцией.

---

## Пуш паттерн

При конфликте (бот пушит tree.json):
```bash
git fetch origin
git merge origin/main --strategy-option=ours -m "merge: sync with bot"
git push
```

При чистом пуше:
```bash
git add <files>
git commit -m "..."
git push
```
