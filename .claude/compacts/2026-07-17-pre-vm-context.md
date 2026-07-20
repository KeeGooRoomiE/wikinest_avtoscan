# Архив CONTEXT.md на 2026-06-19 (до появления VM/docs.html-архитектуры)

Актуально было до того, как появился VM-путь (`docs.html` + `backend/`). Сохранено для истории — эти детали (SSH-пуш через `keegooroomie-github.com`, паттерн `git stash && git pull --rebase && git stash pop && git push`, полные raw.githubusercontent.com URL для картинок) всё ещё применимы к GitHub Pages / `index.html`-пути, но не были актуализированы вместе с остальным контекстом.

## Что было сделано (на 2026-06-19)

- Регламенты: `docs/tp/reglamentation/add-car-reglament.md`, `add-object-axenta.md`
- Главная страница (`docs/home.md`) переписана
- UI: кнопка `+` в сайдбаре рядом с кнопкой переименования папки
- Изображения: полные URL `https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/...`

## Ключевые решения (для index.html/GitHub Pages пути)

- SPA резолвит относительные img-пути от URL страницы, не от .md файла → нужны полные raw.githubusercontent.com URL
- SSH для пуша: remote `git@keegooroomie-github.com:...`, host alias в `~/.ssh/config` → `id_ed25519_wikinest`
- Пуш-паттерн: `.claude/settings.local.json` всегда нестейджед; `git stash && git pull --rebase && git stash pop && git push`
- `.github/workflows/deploy.yml` триггерится на `index.html`, `style.css`, `config.json`, `i18n/**`

## Открытые вопросы на тот момент

- Wialon объекты — документация только частичная
- `tp/reglamentation/index.md` существовал, но пустой
- `tp/examples/index.md` — возможно требует наполнения
