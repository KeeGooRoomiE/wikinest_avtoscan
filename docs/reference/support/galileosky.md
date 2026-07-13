---
isCounting: true
---
# GalileoSky 5

## Основные команды

| Команда | Описание |
|---|---|
| `addphone 1234` | Авторизация номера телефона |
| `REMOTECONFIG 1` | Включить удалённое конфигурирование |
| `COLDSTART` | Перезагрузка GPS модуля |
| `Reset` | Перезагрузка устройства (ответ: `Reset of device. Please wait 15 seconds…`) |
| `upgrade 0` | Обновление прошивки |
| `EraseTrack` | Удаление из памяти всех треков |
| `ChangePass 1234` | Смена пароля (ответ: `current password 1234`) |

## Смена сервера

```
Serverip 95.163.12.22,20359
Serverip2 hw.axenta.cloud,22481
```

Примеры запрос/ответ:

```
Serverip m.7gis.ru,60521      → SERVERIP=m.7gis.ru:60521
Serverip2 m.7gis.ru,60521     → Serverip2= m.7gis.ru: 60521
ServersCfg 120                → включить передачу на второй сервер
```

## PIN / пароль

```
PIN 1234         → PIN:1234;
```
> На новых прошивках команда называется `ACCESSPIN`. PIN — это одновременно код SIM-карты и пароль для доступа через Конфигуратор. По умолчанию `0`.

## Выгрузка архива с SD

```
EFS <begin>,<end>
```

| Параметр | Формат |
|---|---|
| `begin` | `ДДММГГ[ЧЧ[ММ]]` — начало периода (по умолчанию 00:00) |
| `end` | `ДДММГГ[ЧЧ[ММ]]` — конец периода (по умолчанию 23:59) |

```
EFS 010119,010119   → EFS: Uploading of archive has been scheduled
```

## Синхронизация

```
*!SYNC 1    → синхронизация с сервером 1
```

## Доступ инженеру поддержки

https://base.galileosky.com/articles/#!docs-publication/inviting-support-engineers
