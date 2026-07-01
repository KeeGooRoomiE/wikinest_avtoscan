# Регламент создания и настройки учётной записи клиента

## Шаг 1 — Создание учётной записи в 1С

В 1С открыть карточку контрагента. Перейти в **Системы мониторинга** и нажать кнопку **«Создать»**.

Далее выбрать нужный сервер и действовать по соответствующему разделу ниже:

- [AXENTA](#axenta) — для клиентов филиалов г. Кемерово и г. Екатеринбург
- [Глонасс Soft](#глонасс-soft) — для клиентов на сервере ГЛОНАССофт
- [Wialon](#wialon) — для клиентов на сервере Wialon

---

## AXENTA

### 1. Создание учётной записи

1. Открывшаяся форма выглядит следующим образом:

   ![Создание учётной записи](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image1.JPG)

2. Выбрать сервер:
   - **г. Кемерово** → `AXENTA (Кем)`
   - **г. Екатеринбург** → `AXENTA (Екб)`

3. Шаблон имени заполнится автоматически — можно оставить или сократить. Префикс и постфикс добавляются автоматически.

   ![Шаблон имени](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image2.JPG)

4. Проставить галочки как на скриншоте (галочку **«Синхронизировать объекты»** поставим позже):

   ![Настройки галочек](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image3.JPG)

   Нажать **«Записать»**. Если имя уже занято в AXENTA — появится предупреждение; изменить шаблон имени и повторить.

   Спуститься вниз к таблице **«Пользователи»**:

   ![Таблица пользователей](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image70.png)

   Нажать **«Создать»**. Ввести тот же шаблон имени, что при создании административного пользователя. Галочку «Префикс/постфикс» оставить.

   Если все новые ТС должны добавляться в просмотр этому пользователю — установить галочку **«Назначать права на новые объекты»**.

   Нажать **«Записать и закрыть»** на карточке пользователя, затем **«Записать и закрыть»** на карточке учётной записи.

   Через несколько минут учётная запись, административный пользователь и пользователь клиента будут созданы в AXENTA.

5. В CMS перейти в раздел **«Пользователи»**:

   ![Раздел пользователей в CMS](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image5.JPG)

   Распределение ролей:
   - **Пользователь №1** (ЯкуповПГ) — передаётся клиенту
   - **Пользователь №2** — административный, работает специалист ТП

   ![Распределение ролей](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image6.JPG)

   Как различить пользователей:
   - ![Кнопка активности](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image7.JPG) В графе **«Активность»** у административного пользователя зелёная кнопка некликабельна и имеет более бледный оттенок
   - По графе **«Создатель (ФИО)»** — у пользователя №1 прописано `ЯкуповПГ_adm`

   > Для синхронизации с 1С необходимо выдать **«права администратора»** на административного пользователя.

   ![Права администратора — шаг 1](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image8.JPG)
   ![Права администратора — шаг 2](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image9.JPG)
   ![Права администратора — шаг 3](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image10.JPG)
   ![Права администратора — шаг 4](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image11.JPG)

6. После выдачи «административных прав» вернуться в 1С и поставить галочку **«Синхронизировать объекты»**, затем нажать **«Записать и закрыть»**.

   ![Синхронизировать объекты](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image12.JPG)

---

### 2. Настройка кабинета клиента

Открыть административного пользователя. ТС создаются и настраиваются под этим пользователем.

![Административный пользователь](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image13.JPG)

#### 2.1 Загрузка шаблонов отчётов

Раздел **«Отчёты»** (шаг 1) → вкладка **«Шаблоны»** (шаг 2) → **«Создать из файла»** (шаг 3). Выбрать отчёт:
- **«Общий по машине»** — если ТС одна
- **«Общий по группе»** — если ТС несколько

![Загрузка шаблонов](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image14.JPG)

Выбрать файл «Бланк отчётов», нажать **«Загрузить»**. В таблице «Что импортировать» выбрать нужные отчёты.

#### 2.2 Создание пользователя

![Создание пользователя](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image15.JPG)

В разделе **«Пользователи»** нажать **«+»** и создать пользователя.

#### 2.3 Выдача прав

В разделе **«Пользователи»** (шаг 1) нажать значок **«шестерёнки»** (шаг 2) напротив нужного пользователя.

![Выдача прав — шестерёнка](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image16.JPG)

Вкладка **«Доступ»** → раздел **«Общий доступ»** → проставить галочки как на скриншоте:

![Общий доступ](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image17.JPG)

Из списка объектов выбрать нужное ТС, выбрать **«Шаблон прав доступа»** и проставить галочки:

![Права на ТС](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image18.JPG)
![Права на ТС — детали](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image19.JPG)

Для шаблона отчётов — выделить нужный шаблон, поставить галочку **«Только чтение»**.

![Шаблон отчётов — только чтение](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image20.JPG)

Нажать большую зелёную кнопку **«Сохранить»**:

![Кнопка Сохранить](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image21.JPG)

#### 2.4 Настройки под пользователем клиента

Открыть пользователя без постфикса `_adm`:

![Пользователь клиента](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image22.JPG)
![Интерфейс клиента](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image23.JPG)

В левом нижнем углу: **«Настройки»** → **«Мои настройки»**:

![Мои настройки](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image24.JPG)

**Основные настройки** — изменить часовой пояс, при необходимости логин/ФИО/почту клиента.

![Основные настройки](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image25.JPG)

Вкладка **«Дополнительно»** — настроить отображение информационного окна ТС и вкладок клиента согласно скриншотам:

![Дополнительно — часть 1](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image26.JPG) ![Дополнительно — часть 2](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image27.JPG)

![Дополнительно — часть 3](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image28.JPG)

#### 2.5 Конечный результат

![Конечный результат](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image29.JPG)

Информационное окно объекта:

![Информационное окно объекта](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/axenta/image30.JPG)

---

---

## Глонасс Soft

### 1. Создание учётной записи и пользователя

1. Открывшаяся форма выглядит следующим образом:

   ![Форма создания в 1С](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p1-form-1c.png)

2. Выбрать сервер **«ГЛОНАСС Soft»**.

3. Проставить все галочки как на скриншоте.

4. Шаблон имени заполнится автоматически — можно оставить или изменить.

   ![Настройки и шаблон имени](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p1-checkboxes.png)

5. Нажать **«Записать»**, затем спуститься к таблице **«Пользователи»**:

   ![Таблица пользователей](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p2-users-table.png)

   Нажать **«Создать»**. Ввести тот же шаблон имени. Если все новые ТС должны добавляться в просмотр — установить галочку **«Назначать права на новые объекты»**.

   Нажать **«Записать и закрыть»** на карточке пользователя, затем **«Записать и закрыть»** на карточке учётной записи.

   Через несколько минут клиент и пользователь будут созданы в Глонасс Soft.

---

### 2. Настройка клиента и пользователя

1. После создания учётной записи перейти в созданного клиента → раздел **«Пользователи»**.

   ![Список пользователей клиента](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p2-rights-table.png)

2. Двойным нажатием на логин открыть настройки пользователя. Перейти на вкладку **«Права доступа»** → **«Системные роли»** → поставить галочку на **«Пользователь+»**:

   ![Системные роли — Пользователь+](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p3-system-roles.png)

   Роль **«Пользователь+»** включает:
   1. Доступ к просмотру объектов
   2. Доступ к просмотру созданных датчиков (Топливо, зажигание и т.д.)
   3. Изменение иконки
   4. Создание и редактирование произвольных полей
   5. Нормы для ТО
   6. Доступ к созданию, редактированию геообъектов
   7. Доступ к базовым отчётам, конструктору отчётов, отчёт «Трек»
   8. Создание, редактирование путевых листов
   9. Создание, редактирование уведомлений

3. Во вкладке **«Персональные данные»** установить пароль и прописать его в поле **«Описание»** или **«Должность»**.

   ![Персональные данные](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p3-personal-data.png)

4. Перейти в раздел **«Справочники»** → **«Группы»**. Создать группу с наименованием клиента, добавить все ТС и нажать **«Сохранить»**.

   ![Справочники — Группы](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p4-groups-menu.png)
   ![Диалог создания группы](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p4-groups-dialog.png)

5. В разделе **«Справочники»** → **«Модели объектов»** в **«Модель по умолчанию»** изменить иконку на **«Автомобиль Бизнес (Синий)»**.

   ![Модели объектов](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p4-models-menu.png)
   ![Выбор иконки](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p4-icons-selector.png)

---

### 3. Настройка учётной записи

1. Войти в мониторинг под логином и паролем созданной учётной записи, открыть **«Настройки»**.

   ![Интерфейс мониторинга](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p5-monitoring-view.png)

2. Вкладка **«Общее»** — отметить **«Сохранять выбор элементов при обновлении страницы»**.

   ![Настройки — Общее](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p5-settings-general.png)

3. Вкладка **«Объекты»** — **убрать** отметку «Группировка объектов» и **отметить** «Показывать след за объектом» с установкой цвета следа.

   ![Настройки — Объекты](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p6-settings-objects.png)

4. Вкладка **«Трек»** — отметить **«Чередовать цвета при построении отчётов»** и **«Показывать аннотации к треку»**.

   ![Настройки — Трек](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p6-settings-track.png)

5. Вкладка **«Отчёты»** — нажать **«Загрузить отчёт»**, загрузить отчёт **«Общий по машине»** и проставить все галочки в конструкторе отчёта.

   ![Отчёты](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p7-reports.png)

6. Проставить все галочки в конструкторе отчёта и сохранить настройки.

   ![Конструктор отчётов](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p7-report-builder.png)

---

---

---

## Wialon

### 1. Создание учётной записи

1. Открывшаяся форма выглядит следующим образом:

   ![Форма создания в 1С](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p1-form-1c.png)

2. Выбрать сервер:
   - **г. Кемерово** → `WialonHosting (Кем)`
   - **г. Екатеринбург** → `WialonHosting (Екб)`

3. Шаблон имени заполнится автоматически — можно оставить или сократить. Конечный результат имени административного пользователя виден в третьей строке.

   ![Шаблон имени](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p1-template-name.png)

4. Проставить галочки как на скриншоте — **Синхронизировать**, **Синхронизировать объекты**, **Управлять блокированием**:

   ![Настройки галочек](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p2-checkboxes.png)

   Нажать **«Записать»**. Если имя занято — появится предупреждение, изменить шаблон и повторить. Спуститься к таблице **«Пользователи»**:

   ![Таблица пользователей](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p2-users-table.png)

   Нажать **«Создать»**, ввести тот же шаблон имени. Если все новые ТС нужно добавлять в просмотр — установить галочку **«Назначать права на новые объекты»**.

   Нажать **«Записать и закрыть»** на карточке пользователя, затем на карточке учётной записи.

   Через несколько минут учётная запись, административный пользователь и пользователь клиента будут созданы в Wialon.

---

### 2. Настройка кабинета клиента

Открыть административного пользователя (постфикс `_adm`). ТС создаются и настраиваются под этим пользователем.

![Административный пользователь](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p3-admin-user.png)

#### 2.1 Загрузка шаблонов отчётов

В меню административного пользователя выбрать **Импорт/Экспорт** → **Импорт из WLP**:

![Меню импорта](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p4-import-menu.png)

Выбрать файл **«Бланк отчётов»**, нажать **«загрузить»**. В таблице «Что импортировать» выбрать:
- **«Общий по машине»** — если ТС одна
- **«Общий по машине»** и **«Общий по группе»** — если ТС несколько

В таблице **«Куда импортировать»** выбрать учётную запись клиента и нажать **«OK»**:

![Диалог импорта](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p4-import-dialog.png)

#### 2.2 Переключение под пользователя клиента

Переключиться на пользователя без постфикса `_adm`:

![Переключение пользователя](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p5-switch-user.png)

#### 2.3 Настройка главного меню

Оставить только **3 вкладки**: Мониторинг, Треки, Отчёты:

![Главное меню](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p5-main-menu.png)

#### 2.4 Настройка рабочей области

В первой колонке оставить: **Слежение за объектом**, **Состояние движения**, **Актуальность данных**, **Состояние соединения** (установить 10 минут), **Быстрый трек**, **Быстрый отчёт**:

![Рабочая область](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p6-workspace.png)

#### 2.5 Настройки пользователя

Открыть **Настройки пользователя**:

![Настройки пользователя](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p6-user-settings.png)

**6.1 Общие настройки.** Установить:
- Часовой пояс клиента
- Формат даты: `dd.MM.yyyy`
- Город клиента
- Включить: **Значения датчиков**, **Произвольные поля**, **Техобслуживание**, **Водители**
- Включить **Группировку перекрывающихся объектов**

![Общие настройки](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p7-settings-general.png)

Дополнительная информация (Подсказка, Список) — включить согласно скриншоту:

![Дополнительная информация](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p7-settings-extra-info.png)

![Таблица доп. информации](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p8-settings-extra-table.png)

Настройки отображения объектов на карте:

![Настройки объектов](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p8-settings-objects.png)

**6.2 Безопасность** — ничего не меняем.

**6.3 Карты.** Добавить все доступные карты. Если **Яндекс** в списке отсутствует — добавить через учётную запись клиента в `cms.wialon.com`:

![Настройки карт](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p8-maps-settings.png)

После добавления Яндекс появится в списке:

![Список карт](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p9-maps-list.png)

![Яндекс карта](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p9-yandex-map.png)

**6.4 Дроби в датчиках** — на всех пунктах установить **«Округлять»**:

![Дроби в датчиках](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p10-sensor-rounding.png)

#### 2.6 Конечный результат

![Конечный результат](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p10-final-result.png)

#### 2.7 Установка пароля пользователю клиента

Открыть административного пользователя → раздел **«Пользователи»** → открыть свойства пользователя → придумать пароль, ввести его дважды, нажать **«OK»**:

![Установка пароля](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p11-password-set.png)

---

## Финальный шаг — Отправка данных менеджеру

Перейти на [account.avtoscan42.ru](http://account.avtoscan42.ru). Ввести логин и пароль клиента, выбрать систему мониторинга и нажать **«Отправить менеджеру»**, выбрав менеджера из выпадающего списка.

- **АКСЕНТА** — для клиентов AXENTA
- **ГЛОНАСССОФТ** — для клиентов Глонасс Soft
- **WIALON LOCAL** — для клиентов Wialon

![Отправить менеджеру — Глонасссофт](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/glonassoft/gs-p8-account-site.png)

![Отправить менеджеру — Wialon](https://raw.githubusercontent.com/KeeGooRoomiE/wikinest_avtoscan/HEAD/docs/assets/images/wialon/w-p12-account-site.png)
