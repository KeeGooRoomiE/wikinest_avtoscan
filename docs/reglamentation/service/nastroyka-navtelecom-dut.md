---
title: Настройка терминалов Навтелеком — ДУТ BLE и проводной
isCounting: true
---
# Настройка терминалов Навтелеком — ДУТ BLE и проводной

1.  Запустите программу NTC Configurator:

> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-3.png" style="max-width:500px;height:auto">

2.  Подключите устройство к конфигуратору, подождите пока устройство
    свяжется с конфигуратором. Когда это произойдет, Вы увидите
    информацию об устройстве.

> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-4.png" style="max-width:500px;height:auto">

3.  Настройте конфигурацию, нажав на кнопку "Чтение конфигурации
    устройства". Программа загрузит настройки из подключенного
    устройства.

> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-5.png" style="max-width:500px;height:auto">

4.  На вкладке Передача данных в полях APN, Логин и Пароль укажите
    настройки для подключения к Internet. В примере использованы
    настройки доступа в Internet для SIM-карт MTS:\
    APN = interet.mts.ru\
    Логин = mts\
    Пароль = mts

<img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-6.png" style="max-width:500px;height:auto">

5.  На вкладке "Передача данных" укажите IP/DNS и Порт сервера
    мониторинга.

> Для линейки устройств Navtelecom 24хх в системе Wialon необходимо
> использовать IP-адрес 185.213.0.24 и порт 21626.
>
> Значения Порта обычно индивидуальны для каждого типа оборудования.
> Значения этих параметров Вы можете узнать в службе технической
> поддержки или на сайте
> Gurtam.<img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-7.png" style="max-width:500px;height:auto">

Пример для сервера Wialon:

<table style="width:48%;">
<colgroup>
<col style="width: 19%" />
<col style="width: 5%" />
<col style="width: 13%" />
<col style="width: 9%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>Модель устройства</strong></th>
<th style="text-align: center;"><strong>Порт</strong></th>
<th style="text-align: center;"><strong>IP-адрес</strong></th>
<th style="text-align: center;"><strong>DNS-имя</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;">START S-20xx</td>
<td style="text-align: center;">22347</td>
<td rowspan="4" style="text-align: center;">185.213.0.24</td>
<td rowspan="4" style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: center;">SMART S-24xx</td>
<td style="text-align: center;">21626</td>
</tr>
<tr>
<td style="text-align: center;">SIGNAL S-26xx</td>
<td style="text-align: center;">21889</td>
</tr>
<tr>
<td style="text-align: center;">SIGNAL S-46xx</td>
<td style="text-align: center;">22102</td>
</tr>
</tbody>
</table>

> Остальные настройки следует оставить как есть.

7.  Теперь можно перейти к проверке подключения

- откройте окно логов

<img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-8.png" style="max-width:500px;height:auto">

- выберите **пользовательский** лог GSM и нажмите кнопку запуска лога

<img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-9.png" style="max-width:500px;height:auto">

- когда устройство попытается установить связь с сервером Вы увидите

Подключение к серверу № 1: TCP 185.213.0.24:21626, протокол FLEX 1.0

- когда процедура авторизации будет успешно завершена Вы увидите

Соединение с сервером № 1 установлено

> Подключение ДУТ BLE
>
> **Настройка ДУТ**
>
> При подключении нескольких датчиков, их адреса не должны совпадать
>
> **Устройство**
>
> **Настройка Bluetooth**
>
> Ставим галочку «использовать Bluetooth модуль», выбираем устройство
> «датчики»
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-10.jpg" style="max-width:500px;height:auto">
>
> Выбираем тип датчика «ДУТ» , прописываем MAC адрес датчика, тип дут и
> адрес в качестве которого передавать. Имя датчика не обязательно.
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-11.jpg" style="max-width:500px;height:auto">
>
> **Настройка интерфейса**
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-12.png" style="max-width:500px;height:auto">
>
> **Проверка**
>
> **Телеметрия**
>
> Для проверки через
> окно ["Телеметрия"](https://wiki.navtelecom.ru/ru/home/ntc_configurator/help/telemetry) необходимо
> подключиться к устройству по USB или удаленно.
>
> После подключения конфигуратором к устройству, необходимо открыть окно
> "Телеметрия"
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-13.png" style="max-width:500px;height:auto">
>
> Далее нужно включить автоматическое обновление параметров и посмотреть
> показания
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-14.png" style="max-width:500px;height:auto">
>
> Подключение ДУТ (проводной)
>
> **Подключение**
>
> Ниже приведены примеры схем подключения
>
> **Устройства СИГНАЛ**
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-15.png" style="max-width:500px;height:auto">
>
> **Устройства СМАРТ**
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-16.png" style="max-width:500px;height:auto">
>
> **Настройка**
>
> **ДУТ**
>
> При настройке датчиков следует соблюдать несколько обязательных
> правил:

1.  **Выдача данных** должна производится **по запросу** от Устройства

2.  Необходимо **узнать адрес** датчика.

> При подключении нескольких датчиков, их адреса не должны совпадать

3.  Необходимо **узнать скорость** работы интерфейса.

> Обычно используется скорость 19200 бит/с.
>
> **Устройство**
>
> **Настройка интерфейса**
>
> Настройки скорости интерфейса и адреса в устройствах должны совпадать
> с настройками в датчиках
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-17.png" style="max-width:500px;height:auto">
>
> **Настройка интерфейса**
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-12.png" style="max-width:500px;height:auto">
>
> Если выбран протокол передачи данных FLEX 1.0, то на сервер передается
> только **Уровень**.\
> Если выбран протокол FLEX 2.0 и выше, то на сервер
> передается **Уровень** и **Температура**.
>
> **Проверка**
>
> **Телеметрия**
>
> Для проверки через
> окно ["Телеметрия"](https://wiki.navtelecom.ru/ru/home/ntc_configurator/help/telemetry) необходимо
> подключиться к устройству по USB или удаленно.
>
> После подключения конфигуратором к устройству, необходимо открыть окно
> "Телеметрия"
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-13.png" style="max-width:500px;height:auto">
>
> Далее нужно включить автоматическое обновление параметров и посмотреть
> показания
>
> <img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-14.png" style="max-width:500px;height:auto">
>
> Ниже представлены рекомендации по выбору уровня фильтрации в
> зависимости от типа транспортного средства (на примере датчиков фирмы
> «Эскорт»):

1.  Стационарные объекты или емкости

<!-- -->

4.  Транспорт, передвигающийся по ровным асфальтированным дорогам

<!-- -->

7.  Сельскохозяйственная техника

> 8-10 Тяжелая карьерная техника
>
> Это общие рекомендации:
>
> \- Чем короче датчик тем выше следует устанавливать степень
> фильтрации;
>
> \- Чем ближе датчик к одной из стенок бака, тем выше должна быть
> степень фильтрации;
>
> \- Чем более неровная дорога, тем выше должна быть степень фильтрации;
>
> Фильтрации уменьшают колебания уровня топлива, которые вызываются
> плесканием топлива во время движения.
>
> **Важно!!! При установке навигационного терминала необходимо
> устанавливать пароль, состоящий из 4 цифр, который будет определяться
> исходя из времени установки терминала, например:**
>
> терминал был установлен в 9 часов 30 минут, значит пароль будет: 0930
>
> После того как был установлен пароль его **ОБЯЗАТЕЛЬНО** нужно
> записать в заказ-наряд в указанном месте:

<img src="/docs/assets/reglamentation/service/navtelecom-dut-setup-18.jpg" style="max-width:500px;height:auto">
