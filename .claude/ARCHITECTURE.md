# Architecture — wikinest_avtoscan

## Стек

- **Frontend:** WikiNest SPA — `index.html` + `style.css` + vanilla JS
- **Рендеринг:** marked.js (markdown → HTML) в браузере
- **Хостинг:** GitHub Pages (ветка `main`, папка root)
- **CI/CD:** GitHub Actions `.github/workflows/deploy.yml`

## Структура файлов

```
wikinest_avtoscan/
├── index.html              # SPA entry point, весь JS внутри
├── style.css               # Стили
├── config.json             # Настройки WikiNest (название, цвета и т.д.)
├── tree.json               # Индекс всех страниц (обновлять вручную при добавлении)
├── i18n/
│   ├── ru.json             # Русская локализация
│   └── en.json             # Английская локализация
├── docs/
│   ├── home.md             # Главная страница (путь "home" в tree.json)
│   ├── contacts.md
│   ├── reference/
│   │   ├── links.md        # Ссылки на ресурсы
│   │   └── markdown.md     # Памятка по markdown
│   └── tp/
│       ├── main.md         # Основная информация для ТП
│       ├── devices/        # Терминалы (adm, arnavi, galileosky, ...)
│       ├── reglamentation/ # Регламенты
│       │   ├── add-car-reglament.md
│       │   ├── add-object-axenta.md
│       │   └── index.md    # (пустой)
│       ├── examples/
│       │   └── index.md    # Шаблоны
│       └── software/
│           └── axenta.md
└── docs/assets/images/
    ├── axenta/             # image1.JPG ... image31.JPG, image70.png
    ├── axenta-obj/         # ao-p1-*.png (11 шт.)
    ├── glonassoft/         # gs-p1-*.png (18 шт.)
    └── wialon/             # w-p1-*.png (23 шт.)
```

## Поток данных

1. Пользователь открывает `https://keegooroomie.github.io/wikinest_avtoscan/`
2. `index.html` загружается, JS читает `tree.json` → строит навигационное дерево
3. При переходе на страницу JS делает fetch к GitHub raw API → получает `.md` → рендерит через marked.js
4. `[[wiki link]]` синтаксис разрешается против `tree.json` по полю `title`
5. Изображения в `.md` должны иметь полный URL `raw.githubusercontent.com` (не относительные пути)

## Ключевые модификации index.html

- **`renderNode()`** — добавлена кнопка `+` рядом с кнопкой переименования папки
- **`openNewPage(presetFolder)`** — переписана: modal с select папки + input имени + live preview пути
- **`createPage()`** — читает `m-folder` + `m-name` вместо старого `m-path`
- **Inline `<style>` в `<head>`** — fallback для `.folder-add-btn` opacity rules (против кэша браузера)
