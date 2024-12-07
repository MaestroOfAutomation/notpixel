Скрипт из видео про автоматизацию работы с Notpixel при помощи Playwright и centrifugal WS SDK.

Открывается страница в браузере с нотпикселем, запускается webapp'a, достается токен для подключения по WS и открывается WS соединение, которое контролируется скриптом.

В данный момент скрипт перерисовывает пиксель https://t.me/notpixel/app?startapp=x811_y86 если он закрашен черным цветом.

SDK: https://centrifugal.dev/docs/transports/client_sdk

Установка зависимости SDK:
```
pip install centrifuge-python
pip install playwright
playwright install
```
