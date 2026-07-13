# Руководство по созданию контента WikiNest Автоскан

Памятка для ИИ-ассистента: как создавать файлы и папки, чтобы они корректно отображались в дереве базы знаний.

---

## Общий принцип

Всё содержимое базы знаний лежит в папке `docs/`. Каждый **раздел** соответствует папке первого уровня (`docs/company/`, `docs/devices/` и т.д.). Дерево навигации (`tree.json`) пересобирается автоматически при каждом пуше в `docs/**`.

---

## Структура файлов

### Документ (страница)

Файл `docs/<раздел>/<подпапка>/<slug>.md`.

**Обязательный frontmatter:**

```markdown
---
title: Название документа
isCounting: true
---
# Название документа
```

**Необязательные поля frontmatter:**

```markdown
---
title: Название документа
isCounting: true
roles: [sales, support]     # ограничить доступ конкретными ролями (по умолчанию — всем)
author: Иванов И.И.
tags: [тахограф, НРД]
---
```

> `isCounting: true` — страница попадает в счётчик раздела в сайдбаре. Для заглушек/служебных файлов можно поставить `false` или убрать поле.

---

### Папка (подраздел)

Чтобы папка **появилась в дереве**, в ней должен быть файл `_meta.json`.

**Минимальный `_meta.json`:**
```json
{"title": "Название папки"}
```

**С указанием порядка страниц:**
```json
{"title": "Название папки", "pages": ["slug1", "slug2", "slug3"]}
```

> Поле `pages` — массив slug-ов (имён файлов без `.md`). Задаёт порядок страниц внутри папки. Если не указано, страницы идут в алфавитном порядке.

**С явным порядком подпапок (для папки первого уровня):**
```json
{"title": "Регламенты", "order": 3, "pages": ["sales", "service", "support", "accounting"]}
```

> `order` — позиция при сортировке подпапок внутри раздела (редко нужен вручную, бот управляет по `pages[]`).

---

## Правила именования

| Что | Правило | Пример |
|-----|---------|--------|
| Папки | строчные латиница, цифры, дефис | `fuel-control`, `service-ops` |
| Файлы .md | строчные латиница, цифры, дефис | `drive-base.md`, `kv-manufacturing.md` |
| `_meta.json` | точно такое имя | `_meta.json` |
| `title` в `_meta.json` | любой текст, на русском | `"Техническая поддержка"` |
| `title` во frontmatter | любой текст, на русском | `Drive Base` |

---

## Разделы верхнего уровня

Определены в `SECTIONS` в `index.html` и `docs.html`. Папки должны **точно совпадать** с `folder` в SECTIONS.

| Раздел в интерфейсе | Папка `docs/` | slug |
|---------------------|---------------|------|
| Компания | `company/` | `company` |
| Продукты | `products/` | `products` |
| Оборудование | `devices/` | `devices` |
| Процессы | `processes/` | `processes` |
| Регламенты | `reglamentation/` | `reglamentation` |
| Инциденты и решения | `incidents/` | `incidents` |
| Сервисы и инструменты | `software/` | `software` |
| Шаблоны и памятки | `reference/` + `examples/` | `reference` |
| Глоссарий | `glossary/` | `glossary` |

> Разделы "Шаблоны и памятки" объединяет две папки: `reference/` (основная) и `examples/`. Новый контент памяток и шаблонов класть в `reference/`.

---

## Глубина вложенности в сайдбаре

Сайдбар отображает **два уровня**: раздел → подпапка → страницы.

```
Раздел (devices)
└── Тахографы  ← подпапка первого уровня (devices/tachographs/)
    ├── Drive Base  ← страница (devices/tachographs/drive/drive-base.md)
    └── ...
```

Страницы на глубине 3+ (`devices/tachographs/drive/drive-base.md`) группируются под ближайшей первой подпапкой (`tachographs`). Отдельного уровня для `drive/` в сайдбаре нет — страница просто отображается внутри "Тахографы".

---

## Типичные задачи

### Создать новый документ

```
docs/processes/service/new-doc.md
```

```markdown
---
title: Название нового документа
isCounting: true
---
# Название нового документа
```

### Создать новую подпапку с документами

```
docs/reglamentation/accounting/_meta.json  → {"title": "Бухгалтерия"}
docs/reglamentation/accounting/doc1.md
docs/reglamentation/accounting/doc2.md
```

### Создать пустую папку (без документов)

Достаточно только `_meta.json`:
```
docs/products/radios/_meta.json  → {"title": "Рации"}
```

Пустые папки отображаются в дереве как folder-маркеры без страниц внутри.

### Задать порядок подпапок

В `_meta.json` родительской папки:
```json
{"title": "Регламенты", "pages": ["sales", "support", "service", "accounting"]}
```

Порядок в `pages[]` = порядок в сайдбаре.

---

## Контроль доступа

**Скрыть страницу от ролей** — через `roles[]` во frontmatter:
```markdown
---
title: Секретный документ
isCounting: true
roles: [owner, admin, director, head]
---
```

**Скрыть целую папку/раздел от роли** — через `hidden_sections` в `roles.json`. Значение — slug папки:

| Папка | hidden_sections slug |
|-------|---------------------|
| `products/` | `products` |
| `devices/` | `devices` |
| `reglamentation/` | `reglamentation` |
| `software/` | `software` |
| `examples/` | `examples` |
| `incidents/` | `incidents` |
| `glossary/` | `glossary` |
| `company/` | `company` |

Роли `owner`, `admin`, `director`, `head` игнорируют `hidden_sections` — видят всё.

---

## После создания файлов

**GitHub Pages путь (`index.html`):** бот (`build-tree.yml`) пересобирает `tree.json` автоматически при пуше. Если бот переписал `tree.json` с конфликтом:
```bash
git fetch origin
git merge origin/main --strategy-option=ours -m "merge: sync with bot"
git push
```

**VM путь (`docs.html`):** бэкенд пересобирает `tree.json` синхронно при каждой записи через API — ничего дополнительно делать не нужно.

---

## Чего НЕ делать

- Не создавать папки без `_meta.json` — они не появятся в дереве.
- Не писать русские символы в именах файлов/папок.
- Не редактировать `tree.json` вручную при работе через GitHub (бот перепишет).
- Не коммитить `CREDENTIALS.md` и plaintext-пароли.
- Не менять `roles.json` через `put_file` — только через `/api/roles/visibility`.
