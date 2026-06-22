# LLM Context — wikinest_avtoscan

## Текущее состояние проекта

WikiNest-based internal documentation wiki для компании АвтоСкан, задеплоенная на GitHub Pages.
Репозиторий: `KeeGooRoomiE/wikinest_avtoscan`, ветка `main`.

### Что уже сделано (актуально на 2026-06-19)

- **Регламенты:**
  - `docs/tp/reglamentation/add-car-reglament.md` — создание УЗ клиента в AXENTA / Глонасс Soft / Wialon + финальный шаг через account.avtoscan42.ru
  - `docs/tp/reglamentation/add-object-axenta.md` — создание объекта в AXENTA, датчики, детектор поездок

- **Главная страница** (`docs/home.md`) переписана: таблицы регламентов, сервисов, терминалов, быстрые ссылки

- **UI: кнопка `+` в сайдбаре** — рядом с кнопкой переименования папки, появляется при наведении, открывает модальное окно создания страницы с выбором папки

- **Изображения:** все используют полные URL `https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/...`

## Ключевые технические решения

### Изображения в SPA
WikiNest — SPA, браузер разрешает относительные пути от URL страницы (`/wikinest_avtoscan/`), а не от `.md` файла. Поэтому все `<img src>` должны использовать полный `raw.githubusercontent.com` URL.

### SSH для пуша
Remote: `git@keegooroomie-github.com:KeeGooRoomiE/wikinest_avtoscan.git`  
SSH host: `keegooroomie-github.com` → `~/.ssh/config` → `id_ed25519_wikinest`

### Пуш-паттерн
`.claude/settings.local.json` всегда нестейджед. При пуше:
```
git stash && git pull --rebase && git stash pop && git push
```

### tree.json
Индексный файл — обновлять при добавлении новых `.md` страниц (path, title, excerpt, parts, folder_titles).

### Deploy workflow
`.github/workflows/deploy.yml` триггерится на изменения `index.html`, `style.css`, `config.json`, `i18n/**`. Деплоит весь репозиторий (`path: '.'`).

## Открытые вопросы / возможные следующие шаги

- Документация пока покрывает не все сервисы (Wialon объекты — только частично через регламент УЗ)
- `tp/reglamentation/index.md` существует но пустой (excerpt пустой в tree.json)
- `tp/examples/index.md` — шаблоны, возможно требует наполнения
