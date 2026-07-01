# CLAUDE.md — Wikinest Автоскан

Инструкции для Claude Code при работе в этом репозитории.

---

## Проект

Внутренняя база знаний компании **Автоскан** на движке WikiNest.
Репозиторий: `KeeGooRoomiE/wikinest_avtoscan` · GitHub Pages · ветка `main`.
Стек: `index.html` (весь JS внутри) + `style.css` + `docs/*.md` + `tree.json`.

Архитектура: [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)
Контроль доступа: [ACCESS_CONTROL.md](ACCESS_CONTROL.md)

---

## Правила работы с tree.json

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

---

## UI и стили

- **Тёмная тема удалена** целиком. Не добавлять обратно: ни `@media (prefers-color-scheme: dark)`, ни `[data-theme="dark"]`.
- **Поле поиска** — `autocomplete="new-password" name="search_q"` обязательно (иначе браузер предлагает сохранить пароль).
- **Динамические списки** (поиск, избранное, недавние) — строить через `document.createElement` + `div.onclick = () => {...}`, не через `innerHTML` с `onclick=""`.

---

## Структура ролей

Файл `roles.json`. Роли и их доступ:

| Роль | can_edit | hidden_sections |
|------|:--------:|-----------------|
| `owner` | ✅ | — |
| `admin`, `director`, `head` | ❌ | — (видят всё) |
| `support` | ❌ | — |
| `sales` | ❌ | `tp/devices` |
| `accounting` | ❌ | `tp/devices`, `tp/reglamentation`, `tp/software`, `tp/examples` |
| `office-manager` | ❌ | `products`, `tp/reglamentation`, `incidents`, `tp/software`, `tp/examples`, `glossary` |
| `warehouse`, `logistics`, `installer` | ❌ | `company`, `products`, `tp/reglamentation`, `incidents`, `tp/software`, `tp/examples`, `glossary` |

`FULL_ACCESS_ROLES = ['owner','admin','director','head']` — обходят все `hidden_sections`.

---

## Структура навигации (tree.json разделы)

| Раздел в UI | folder_titles ключ | Путь docs/ |
|-------------|-------------------|------------|
| Компания | `company: "Company"` | `docs/company/` |
| Памятки | `reference: "Памятки"` | `docs/reference/` |
| Документация для ТП | `tp: "Документация для ТП"` | `docs/tp/` |
| — Терминалы | `devices: "Терминалы"` | `docs/tp/devices/` |
| — Регламенты | `reglamentation: "Регламенты"` | `docs/tp/reglamentation/` |
| — Шаблоны (ТП) | `examples: "Шаблоны"` | `docs/tp/examples/` |
| — Сервисы | `software: "Сервисы"` | `docs/tp/software/` |
| Шаблоны | `templates: "Шаблоны"` | `docs/templates/` |
| Глоссарий | `glossary: "Glossary"` | `docs/glossary/` |
| Инциденты | `incidents: "Incidents"` | `docs/incidents/` |
| Процессы | `processes: "Processes"` | `docs/processes/` |

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
