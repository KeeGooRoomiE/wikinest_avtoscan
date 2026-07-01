# Контроль доступа — Wikinest Автоскан

Этот файл описывает все нестандартные условия по правам и видимости страниц.
Хранится только в репозитории, **не публикуется в документации**.

---

## Роли (roles.json)

| Роль (slug)    | Название               | Редактирование | Скрытые разделы |
|----------------|------------------------|:--------------:|-----------------|
| `owner`        | Владелец               | ✅             | —               |
| `admin`        | Администратор          | ❌             | —               |
| `director`     | Директор               | ❌             | —               |
| `head`         | Руководитель отдела    | ❌             | —               |
| `support`      | Техническая поддержка  | ❌             | —               |
| `sales`        | Менеджер продаж        | ❌             | `tp/devices`    |
| `accounting`   | Бухгалтерия            | ❌             | `tp/devices`, `tp/reglamentation`, `tp/software`, `tp/examples` |
| `office-manager` | Офис-менеджер        | ❌             | `products`, `tp/reglamentation`, `incidents`, `tp/software`, `tp/examples`, `glossary` |
| `warehouse`    | Кладовщик              | ❌             | `company`, `products`, `tp/reglamentation`, `incidents`, `tp/software`, `tp/examples`, `glossary` |
| `logistics`    | Логист                 | ❌             | `company`, `products`, `tp/reglamentation`, `incidents`, `tp/software`, `tp/examples`, `glossary` |
| `installer`    | Установщик             | ❌             | `company`, `products`, `tp/reglamentation`, `incidents`, `tp/software`, `tp/examples`, `glossary` |

---

## Привилегированные роли (FULL_ACCESS_ROLES)

Роли `owner`, `admin`, `director`, `head` имеют **полный доступ** ко всем разделам
и игнорируют поле `hidden_sections`. Реализовано в `index.html`:

```js
const FULL_ACCESS_ROLES = ['owner','admin','director','head'];
```

Эти роли видят все разделы дерева документов, даже если `hidden_sections` в roles.json заполнен.

---

## Право редактирования

Только роль `owner` имеет `can_edit: true`. Это дает доступ к:
- Кнопке редактирования страницы (иконка карандаша)
- Кнопке тестирования (`Тестирование`) в шапке
- Черновикам страниц (`#draft-banner`)

Дополнительно: для конкретной страницы может быть задан список `editors[]` в tree.json.
Функция `canEditPage(page)` разрешает редактирование если роль в `editors[]` ИЛИ `can_edit===true`.

---

## Ограничения на уровне страниц (tree.json)

Поля `roles[]` и `editors[]` в записях tree.json позволяют задавать доступ на уровне
отдельных документов:

- **`roles[]`** — список ролей, которым разрешён просмотр страницы (если пусто — всем)
- **`editors[]`** — список ролей, которым разрешено редактирование страницы

На данный момент ни у одной страницы не заданы `roles[]` или `editors[]` —
доступ определяется только через `hidden_sections` в roles.json.

---

## Видимость разделов в дереве навигации

Разделы скрываются если `path` страницы начинается с одного из значений в `hidden_sections`.

Пример: роль `sales` скрывает раздел `tp/devices` — все страницы с путём вида
`tp/devices/...` не отображаются в дереве и не открываются.

---

## Хранение паролей

Пароли хранятся как SHA-256 хеши в roles.json. Plaintext-пароли **никогда** не коммитятся в git.
Файл с паролями в открытом виде (CREDENTIALS.md) должен быть в .gitignore и не пушится.
