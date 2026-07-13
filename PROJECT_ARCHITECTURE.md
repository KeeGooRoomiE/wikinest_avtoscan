# Архитектура проекта — Wikinest Автоскан

> Актуально на: 2026-07-01

**Этот файл описывает путь GitHub/GitLab CI (`index.html`).** С 2026-07-03 это аварийный фолбэк — основной путь ежедневной работы переехал на VM (`docs.html` + `backend/`), см. [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) и [DEPLOYMENT.md](DEPLOYMENT.md). Сам движок (роли, рендеринг, поиск, редактор) общий для обоих путей — здесь описанное про UI/роли/паттерны верно для обоих, различается только транспорт чтения/записи.

---

## Стек

| Компонент | Реализация |
|-----------|-----------|
| SPA | `index.html` — весь JavaScript inline, без bundler/build step |
| Стили | `style.css` — CSS без препроцессора, Flexbox/Grid |
| Рендеринг Markdown | `marked.js` v9 (CDN, SRI хеш) |
| Хостинг | GitHub Pages, ветка `main`, папка root |
| CI/CD | GitHub Actions (`.github/workflows/`) |
| Контент | `docs/*.md` — Markdown файлы |
| Индекс | `tree.json` — авто-генерируется ботом, корректируется вручную |
| Поиск | `search.json` — path → raw markdown, lazy-load |
| Роли | `roles.json` — SHA-256 хеши паролей + права + hidden_sections |
| Конфиг | `config.json` — owner, repo, site_name, lang, edit_password_hash |

---

## Структура файлов

```
wikinest_avtoscan/
├── index.html                 # SPA entry point, весь JS внутри (~1870 строк)
├── style.css                  # Все стили (~1600 строк)
├── config.json                # Публичный конфиг (owner, repo, lang)
├── roles.json                 # Роли, SHA-256 хеши, права доступа
├── tree.json                  # Индекс страниц (auto-generated + manual fixes)
├── search.json                # Полнотекстовый индекс (auto-generated)
├── CLAUDE.md                  # Инструкции для Claude Code
├── PROJECT_ARCHITECTURE.md    # Этот файл
├── ACCESS_CONTROL.md          # Документ по правам и видимости
├── i18n/
│   ├── ru.json
│   └── en.json
├── docs/
│   ├── home.md
│   ├── contacts.md            # Дубль — основной
│   ├── company/
│   │   └── contacts.md        # Дубль — в разделе Компания
│   ├── glossary/index.md
│   ├── incidents/index.md
│   ├── processes/
│   │   ├── 1c/index.md
│   │   └── bitrix/index.md
│   ├── reference/
│   │   ├── links.md
│   │   └── markdown.md
│   ├── templates/
│   │   └── markdown-reference.md   # Справочник по оформлению
│   └── tp/
│       ├── main.md
│       ├── devices/           # adm, arnavi, at-links, galileosky, ...
│       ├── examples/index.md  # Шаблоны для ТС
│       ├── reglamentation/    # Регламенты + должностные функции
│       └── software/axenta.md
├── docs/assets/
│   └── brand/
│       ├── autoskan-logo-transparent.png
│       └── autoskan-favicon-32x32.ico
└── .github/workflows/
    ├── build-tree.yml         # Авто-генерация tree.json при push в docs/**
    └── deploy.yml             # Деплой на GitHub Pages
```

---

## Поток данных

### Чтение

```
Пользователь открывает GitHub Pages URL
    ↓
index.html загружается
    ↓
JS: fetch config.json → fetch roles.json → показ модала входа
    ↓
Пользователь вводит пароль → SHA-256 → сравнение с roles.json
    ↓
currentRole сохраняется в sessionStorage
    ↓
fetch tree.json (raw.githubusercontent.com, no-cache)
    ↓
renderTree() → строит навигацию, фильтруя по hidden_sections роли
    ↓
openPage(page) → fetch docs/{path}.md → marked.parse() → #view
```

### Поиск

```
Пользователь открывает поиск (⌘K)
    ↓
ensureSearchIndex() → lazy fetch search.json (один раз за сессию)
    ↓
runSearch(q):
  1. Фильтр tree[] по title/excerpt (быстрый)
  2. Фильтр searchIndex по полному контенту
  3. Дедупликация, лимит 12 результатов
    ↓
DOM listeners на каждый результат:
  div.onclick = () => { closeSearch(); window._searchHighlight = q; openPage(p); }
    ↓
После рендера страницы: highlightInView(q) → скролл к первому <mark>
```

### Ролевой доступ

```
roles.json → currentRole (sessionStorage)
    ↓
FULL_ACCESS_ROLES = ['owner','admin','director','head']
    ↓
isHiddenPage(page):
  если роль в FULL_ACCESS_ROLES → false (видит всё)
  иначе → проверить hidden_sections[]
    ↓
canEdit():
  currentRole?.can_edit === true (только owner)
    ↓
canEditPage(page):
  canEdit() ИЛИ page.editors?.includes(currentRole.slug)
```

---

## GitHub Actions

### `build-tree.yml`

Триггер: push в `main` затрагивает `docs/**`.

1. Checkout с `fetch-depth: 0` (нужен `git log` для `updated_at`)
2. `git pull origin main`
3. Python скрипт:
   - Обходит `docs/`, извлекает первый `# H1` как title, первую строку как excerpt
   - `git log -1 --format=%cI` для `updated_at`
   - Генерирует `tree.json` + `search.json`
4. `git commit && git push` если файлы изменились

**Проблема:** Бот всегда ставит `folder_titles` на английском (берёт имя папки) и может взять неверный `title` если в файле есть незакавыченный `# H1` в примерах. Решение — merge с `--strategy-option=ours`.

### `deploy.yml`

Триггер: каждый push в `main`.
Деплоит весь репозиторий на GitHub Pages через `actions/deploy-pages`.

---

## Ролевая система

### roles.json

```json
{
  "slug": "owner",
  "name": "Владелец",
  "password_hash": "SHA-256 hex",
  "can_edit": true,
  "hidden_sections": []
}
```

Вход: пароль → `sha256()` → сравнение → `currentRole` в sessionStorage.

### Видимость разделов

`hidden_sections` — массив префиксов путей. Страница скрывается если её `path` начинается с любого из префиксов.

`FULL_ACCESS_ROLES` (`owner`, `admin`, `director`, `head`) — полностью игнорируют `hidden_sections`.

### Редактирование

Только `owner` (`can_edit: true`). Остальные видят страницы, но не могут редактировать.
На уровне страницы — поле `editors[]` в tree.json (сейчас не используется).

---

## Безопасность

| Аспект | Реализация |
|--------|-----------|
| XSS | `escHtml()` для всего user-controlled контента в innerHTML |
| Динамические onclick | DOM API (`div.onclick = fn`), не `innerHTML` с атрибутами |
| Пути | Валидация `/^[a-zA-Z0-9_\-][a-zA-Z0-9_\-\/]*$/` перед API вызовами |
| PAT токен | XOR-обфускация с паролем → `localStorage.wn_enc_token` |
| Пароли | SHA-256 хеши в roles.json, plaintext никогда не в репо |
| SRI | marked.js загружается с `integrity="sha512-..."` |
| marked.js | Парсит markdown → innerHTML без DOMPurify (приемлемо для internal wiki) |

---

## Ключевые паттерны

### Inline onclick — ЗАПРЕЩЁН для динамических списков

```js
// НЕПРАВИЛЬНО — ломается если строка содержит "
div.innerHTML = `<div onclick="openPage(${JSON.stringify(p)})">...</div>`;

// ПРАВИЛЬНО
const div = document.createElement('div');
div.innerHTML = `<span>${escHtml(p.title)}</span>`;
div.onclick = () => openPage(p);
container.appendChild(div);
```

### Подсветка поиска

```js
// При клике на результат поиска:
div.onclick = () => {
  closeSearch();
  window._searchHighlight = q;  // передаём запрос
  openPage(p);
};

// В renderView() после рендера:
if (window._searchHighlight) {
  const _q = window._searchHighlight;
  window._searchHighlight = null;
  highlightInView(_q);
  const firstMark = $('view').querySelector('mark');
  if (firstMark) setTimeout(() => firstMark.scrollIntoView({behavior:'smooth',block:'center'}), 80);
}
```

### Банер дней рождения

`injectBirthdayBanner(el)` — парсит 🎂 колонку из таблицы контактов, показывает карточки для ближайших 30 дней. Вызывается после рендера если `currentPath` содержит `contacts`.

---

## CDN кеширование

`raw.githubusercontent.com` кеширует ответы ~30–60 сек.
После push страница может быть устаревшей — дождаться завершения `deploy.yml`.

---

## Известные ограничения

- `docs/contacts.md` и `docs/company/contacts.md` — дубли, нужно поддерживать синхронизацию вручную
- `tree.json` — бот перезаписывает при каждом push в docs/, нужен merge (только на этом, GitHub/GitLab CI пути — на VM-пути бэкенд пересобирает `tree.json` сам, конфликтов нет)
- Темная тема удалена намеренно (была нерабочая)
- `tp/reglamentation/index.md` — существует но почти пустой
- Раздел «CDN кеширование» выше (задержка 30-60 сек после push) относится только к этому пути — на VM бэкенд пишет файл на диск и он сразу отдаётся тем же процессом, задержки нет
