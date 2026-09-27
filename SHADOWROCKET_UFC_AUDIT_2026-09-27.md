# UFC PROXY и проверка повторов, 2026-09-27

Изменён существующий профиль: добавлено 15 приоритетных UFC PROXY-правил, удалены 3 доказанно избыточных правила. Всего 175 → 187 правил. Все 75 Apple DIRECT-правил, локальные исключения, [General], [Host], update-url, внешние подписки и FINAL,PROXY сохранены. Новый общий аудит Apple не проводился.

Рабочая ветка: `codex/ufc-proxy-dedup-20260927`. База: `780a5d0f29326fc1242f66288ecbd3a75bf52fe1`. Точный путь конфигурации: `ru_direct_runetfreedom_improved_final_autoupdate.conf` в `aomikh/shadowrocket-configs`. Локальный путь: `/workspace/scratch/d1450cdb9b27/shadowrocket-configs/ru_direct_runetfreedom_improved_final_autoupdate.conf`.

## Исходное состояние

Рабочая директория была чистая, исходная ветка `codex/apple-kinopub-audit-20260924`, HEAD `a115a1e0f547e758443b5a8b48516ea591e85ace`. После fetch проверен main `780a5d0…`: предыдущая работа уже объединена через rebase, полное дерево файлов совпадает с прежней веткой. Незавершённых локальных отличий не было; слепая замена содержимым raw URL не выполнялась. Инструкций AGENTS.md и CI не найдено. Прочитаны конфигурация, HANDOFF и прежняя проверка.

[Действующий update-url](https://raw.githubusercontent.com/aomikh/shadowrocket-configs/main/ru_direct_runetfreedom_improved_final_autoupdate.conf) проверен 2026-09-27T02:58:53Z: HTTP 200, text/plain, 9902 байта; присутствуют секции и FINAL,PROXY, это не HTML или пустой ответ. SHA256 опубликованного файла, локальной копии и базы одинаков: `0fc24453eb6d2fb11537067c554f90aa55c0c9fb8b95511e6728006ad9ce106d`.

## Удалённые повторы

Это случаи Б: поздние правила полностью покрыты более ранним суффиксом той же политики, без дополнительных параметров. Точных дубликатов типа А в исходном [Rule] не было.

| Удалено | Исходная строка | Сохраняемое правило | Его строка до → после | Доказательство |
|---|---:|---|---:|---|
| `DOMAIN-SUFFIX,market.yandex.ru,DIRECT` | 160 | `DOMAIN-SUFFIX,yandex.ru,DIRECT` | 149 → 172 | Суффикс полностью покрывает имя/подсуффикс; политика и параметры совпадают; более раннее совпадение уже завершало обработку. |
| `DOMAIN,api.market.yandex.ru,DIRECT` | 161 | `DOMAIN-SUFFIX,yandex.ru,DIRECT` | 149 → 172 | Суффикс полностью покрывает имя/подсуффикс; политика и параметры совпадают; более раннее совпадение уже завершало обработку. |
| `DOMAIN,helpcenter.redotpay.com,PROXY` | 177 | `DOMAIN-SUFFIX,redotpay.com,PROXY` | 176 → 195 | Суффикс полностью покрывает имя/подсуффикс; политика и параметры совпадают; более раннее совпадение уже завершало обработку. |

Удалён также опустевший заголовок Yandex Market. Порядок остальных строк не изменён. Проверен весь [Rule], до и после Apple: в итоговом файле нет точных дубликатов или поздних DOMAIN/DOMAIN-SUFFIX/IP-CIDR, полностью покрытых ранним локальным правилом той же политики и с теми же параметрами. Проверены также односторонние включения локальных KEYWORD; они не признаны эквивалентом SUFFIX.

Намеренно сохранены:

- `198.183.17.0/24` перед `198.183.16.0/20` и `2a01:b740::/32` перед `2a01:b740::/29`: раннее узкое правило не покрывает позднюю широкую сеть, а подтверждённые Apple-правила сохраняются по условию задачи.
- `DOMAIN-KEYWORD,redotpay,PROXY` и аналогичное WhatsApp: охватывают также имена вне соответствующих суффиксов. Ранний суффикс и более поздний keyword не имеют одинаковой области.
- Локальные страховки KinoPub, GoogleVideo/YouTube, Discord/AI и прочие совпадения с изменяемыми внешними списками. Доступность и содержимое подписок не должны становиться условием удаления пользовательского правила.
- Совпадения приватных сетей между skip-proxy, tun-excluded-routes и [Rule]: разные механизмы. Правила IPv6 сохранены при текущем ipv6=false.

## Полный UFC-блок

Apple имеет приоритет. UFC расположен после Apple и локальных правил, перед Advertising, российскими DIRECT, всеми внешними списками и GEOIP. Новых групп, узлов или выбора страны выхода нет. Использована существующая политика PROXY.

```ini
# UFC / UFC Fight Pass — PROXY
# Official sites, regional editions and the active legacy redirect.
# -------------------------------
DOMAIN-SUFFIX,ufc.com,PROXY
DOMAIN-SUFFIX,ufcfightpass.com,PROXY
DOMAIN-SUFFIX,fightpass.com,PROXY
DOMAIN-SUFFIX,ufc.tv,PROXY
DOMAIN-SUFFIX,ufc.ru,PROXY
DOMAIN-SUFFIX,ufc.com.br,PROXY
DOMAIN-SUFFIX,ufcespanol.com,PROXY
DOMAIN-SUFFIX,ufc.cn,PROXY

# Exact shared-platform hosts used by the public Fight Pass web application.
# These rules also affect other services using the same hostnames.
DOMAIN,dce-frontoffice.imggaming.com,PROXY
DOMAIN,ufc.api.onvesper.com,PROXY
DOMAIN,search.dce-prod.dicelaboratory.com,PROXY
DOMAIN,guide.imggaming.com,PROXY
DOMAIN,static.diceplatform.com,PROXY
DOMAIN,content-images.onvesper.com,PROXY
DOMAIN,vod-images.onvesper.com,PROXY
```

## Основания для новых правил

Проверка источников: 2026-09-27. Использованы первичные публичные страницы и код официального веб-приложения, сборка `6.60.0.21db1d8`. Это подтверждает назначение инфраструктуры, но не успешность входа/воспроизведения в домашней сети. Метаданные загрузки, SHA256, URLs и решения для каждого правила сохранены в `audit/ufc-evidence-20260927.json`. API-ключи, токены, cookies и полные подписанные видеоссылки не сохранялись в репозитории.

| Правило/назначение | Первичный источник | Что подтверждено | Ограничение |
|---|---|---|---|
| `DOMAIN-SUFFIX,ufc.com,PROXY` | [ufc](https://www.ufc.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Официальный сайт / региональная ссылка в текущем меню UFC; UFC-пространство имён. | Поддомены покрыты суффиксом; фактическое приложение на устройстве не запускалось. |
| `DOMAIN-SUFFIX,ufcfightpass.com,PROXY` | [ufc](https://www.ufc.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Официальный сайт / региональная ссылка в текущем меню UFC; UFC-пространство имён. | Поддомены покрыты суффиксом; фактическое приложение на устройстве не запускалось. |
| `DOMAIN-SUFFIX,ufc.ru,PROXY` | [ufc](https://www.ufc.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Официальный сайт / региональная ссылка в текущем меню UFC; UFC-пространство имён. | ufc.ru связан официальным меню и текущим realm, HTTP 502 из среды аудита; это не проверка из домашней сети. |
| `DOMAIN-SUFFIX,ufc.com.br,PROXY` | [ufc](https://www.ufc.com/); [ufc-br](https://www.ufc.com.br/) | Официальный сайт / региональная ссылка в текущем меню UFC; UFC-пространство имён. | Поддомены покрыты суффиксом; фактическое приложение на устройстве не запускалось. |
| `DOMAIN-SUFFIX,ufcespanol.com,PROXY` | [ufc](https://www.ufc.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Официальный сайт / региональная ссылка в текущем меню UFC; UFC-пространство имён. | Поддомены покрыты суффиксом; фактическое приложение на устройстве не запускалось. |
| `DOMAIN-SUFFIX,ufc.cn,PROXY` | [ufc](https://www.ufc.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Официальный сайт / региональная ссылка в текущем меню UFC; UFC-пространство имён. | Поддомены покрыты суффиксом; фактическое приложение на устройстве не запускалось. |
| `DOMAIN-SUFFIX,ufc.tv,PROXY` | [ufc-tv](https://ufc.tv/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | HTTP-запрос перенаправлен на https://ufcfightpass.com/, возвращена действующая оболочка. | Проверен публичный redirect из среды аудита. |
| `DOMAIN-SUFFIX,fightpass.com,PROXY` | [fightpass-com](https://fightpass.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | HTTP-запрос перенаправлен на https://ufcfightpass.com/, возвращена действующая оболочка. | Проверен публичный redirect из среды аудита. |
| `DOMAIN,dce-frontoffice.imggaming.com,PROXY` | [fightpass](https://ufcfightpass.com/); [fightpass-js-8](https://ufcfightpass.com/code/js/app.2aca647041a2d49ab5e3.js); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Базовый HTTP API v2/v4: realm, login, session, catalogue и запрос playback details. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |
| `DOMAIN,ufc.api.onvesper.com,PROXY` | [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com); [ufc-api-realm](https://ufc.api.onvesper.com/api/v2/realm-settings/domain/ufcfightpass.com) | FRONTOFFICE_URL в iosSettings/androidSettings UFC; тот же realm отвечает на выделенном API. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |
| `DOMAIN,search.dce-prod.dicelaboratory.com,PROXY` | [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com); [fightpass-js-8](https://ufcfightpass.com/code/js/app.2aca647041a2d49ab5e3.js); [player-78955](https://ufcfightpass.com/code/js/chunks/78955.3d2a5fe65cf3b6257d1c.js) | Для dce.ufc выбран contentSearchEngine=VESPER; prod vespersearchapi и функция построения поиска указывают этот hostname. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |
| `DOMAIN,guide.imggaming.com,PROXY` | [fightpass-js-8](https://ufcfightpass.com/code/js/app.2aca647041a2d49ab5e3.js); [player-79092](https://ufcfightpass.com/code/js/chunks/79092.64ad2a0033a51e82c7a9.js) | beaconapi для сессии воспроизведения; проигрыватель запускает beacon и при определённых обрабатываемых ошибках вызывает clear()/сообщение об ошибке. Это не только необязательные изображения. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |
| `DOMAIN,static.diceplatform.com,PROXY` | [fightpass](https://ufcfightpass.com/); [realm-settings](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) | Ресурсы UFC, включая APPLETV_* иллюстрации, web login background, логотипы и шрифты. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |
| `DOMAIN,content-images.onvesper.com,PROXY` | [fightpass](https://ufcfightpass.com/); [fightpass-js-3](https://ufcfightpass.com/code/js/93627.74e4ef94ac859437144e.js) | Предзагрузка DNS и код преобразования static.diceplatform.com в адрес изображений. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |
| `DOMAIN,vod-images.onvesper.com,PROXY` | [fightpass](https://ufcfightpass.com/); [fightpass-js-3](https://ufcfightpass.com/code/js/93627.74e4ef94ac859437144e.js) | Предзагрузка DNS и код преобразования видеопостеров в адрес изображений; это не доказательство доставки видео. | Точное правило действует для любого приложения, обращающегося к этому hostname. Использование конкретной версией tvOS-приложения не проверено. |

[Официальная карточка UFC в App Store](https://apps.apple.com/us/app/ufc/id534568162) связывает приложение с UFC Fight Pass. Принадлежность App Store/StoreKit/APNs остаётся Apple: связанные соединения обрабатываются прежним DIRECT, а не процессным UFC PROXY.

В [публичном realm UFC](https://dce-frontoffice.imggaming.com/api/v2/realm-settings/domain/ufcfightpass.com) прямо заданы `realm=dce.ufc`, `realmFullName=UFC Fightpass`, `preferredDomain=ufcfightpass.com`, `contentSearchEngine=VESPER`, `videoEndpoint=V4`, `liveEndpoint=V4`. `iosSettings.FRONTOFFICE_URL=https://ufc.api.onvesper.com`; отдельный FRONTOFFICE_URL для tvOS в полученном документе не задан. Поэтому нельзя выдавать iOS-настройку за наблюдение сетевого журнала конкретного Apple TV.

Узлы static/content-images/vod-images используются для иллюстраций и ресурсов. Название `vod-images` не означает передачу видеосегментов. Общие узлы imggaming/onvesper/diceplatform/dicelaboratory закреплены только точным DOMAIN; тот же hostname будет PROXY и при обращении другого приложения. Доменная маршрутизация не может отделить `/dce.ufc/` от другого пути на одном hostname.

Код плеера, полученный по ленивым зависимостям официального video-модуля, читает `playerUrlCallback`, HLS/DASH, субтитры и `drm.licenseServerUrl` из ответа для материала. Подтверждены механизмы получения потоков и DRM, но сами итоговые CDN/лицензионные hostname без авторизованного ответа не установлены. Новые фиксированные CDN/IP по догадке не добавлены. Вход в аккаунт, сессия пользователя, запрос лицензии и запуск платного материала не выполнялись.

Не добавлены: `ufcfightpass.ru` и `ufcpromocodes.ru` (есть среди разрешённых realm-имён, но HTTP 502, текущая необходимость не подтверждена); stage/UAT/test/development и старые технические aliases; общие платформы целиком; маркетинговые трекеры; магазины, спортзалы и внешние медиапартнёры как предполагаемые зависимости запуска. Для неизвестного CDN остаются действующие правила/GEOIP/FINAL, это не обещание полного UFC PROXY без журналов.

## Внешние списки и семантика

Все пять действующих подключений получены успешно. SHA256 закреплены, вычисленные Git blob SHA сверены с GitHub Contents API. Политика и URLs в конфигурации не изменены. Каждый внешний список расположен после всего Apple/UFC. Проверялись формат и релевантные совпадения, новый ручной аудит миллионов посторонних доменов не проводился.

| Список | Строка конфигурации | Политика | Записей / формат | Ревизия содержимого (Git blob) |
|---|---:|---|---|---|
| [Advertising.list](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Advertising/Advertising.list) | 159 | REJECT | 781; DOMAIN-KEYWORD 278, URL-REGEX 14, IP-CIDR 489 | `043734ca1421ca2cf463ef9616403c4a3c882e9d` |
| [antifilter-download.txt](https://raw.githubusercontent.com/runetfreedom/russia-blocked-geosite/release/antifilter-download.txt) | 238 | PROXY | 1534624; DOMAIN-SET 1534624 | `5bdbbe3e8a368351e4fe4fe9031b174d8afaf36e` |
| [YouTube.list](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/YouTube/YouTube.list) | 239 | PROXY | 190; DOMAIN-SUFFIX 179, DOMAIN-KEYWORD 1, USER-AGENT 7, IP-CIDR 3 | `6eba0595290b3f991d156a580e08508d0c544495` |
| [Discord.list](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Discord/Discord.list) | 240 | PROXY | 29; DOMAIN-SUFFIX 29 | `2dadab08cacb13029da275269ac13a2c423ca09a` |
| [ru-blocked.txt](https://raw.githubusercontent.com/runetfreedom/russia-blocked-geoip/release/surge/ru-blocked.txt) | 241 | PROXY | 88586; IP-CIDR 88586 | `7c6589363f4d26f5d8fa2af2d41cfc83016aabdb` |

В реально полученных RULE-SET записи имеют тип/значение и иногда `no-resolve`, но не собственные DIRECT/PROXY/REJECT. Следовательно, в этой конфигурации нет неоднозначности между встроенной политикой и политикой подключения. DOMAIN-SET Runet содержит доменные значения, а не строки правил. Подключение и выбор политики сверены со [справкой именно Shadowrocket](https://github.com/LOWERTOP/Shadowrocket/blob/6336a2e010660b5ef70cb2a0d77e5f5988dc1501/README.md). Это сторонняя справка, не документация Surge/Clash и не проверка закрытого парсера клиента. Поведение при произвольной встроенной политике в другом RULE-SET из этого аудита не выводится.

Содержимое Runet/YouTube/Discord совпало с полученным 24 сентября. SHA Advertising изменился только из-за его метаданных заголовка; набор активных правил сверяется отдельно. Advertising.list содержит 781 активную строку, большой TOTAL в заголовке относится также к отдельному файлу доменов, который здесь не подключён.

Сохраняется прежняя upstream-аномалия Runet DOMAIN-SET: строка 269745 `dokumentam24.ru,`. Внешний файл не редактировался. Модель пропускает эту строку с предупреждением; реальное поведение импорта Shadowrocket при этой записи не проверено. URL-REGEX/USER-AGENT без URL/заголовков и фактическая GeoIP-база приложения в модель не входят.

## Структура, регрессии и трассировки

Пройдены: структура [General]/[Rule]/[Host], формат и число полей всех 187 правил, доменные значения/границы, IPv4/IPv6 CIDR, no-resolve, HTTPS URLs, единственный последний FINAL,PROXY, LF/завершающий перевод строки, уникальность правил, порядок Apple/UFC/внешних списков, сохранение порядка всех оставшихся старых правил. `git diff --check` и компиляция Python без исполнения прошли.

Исходный `audit_shadowrocket.py` успешно выполнен до изменения профиля, на его историческом ожидаемом состоянии 175 правил. Он содержит жёсткие ожидания этапа 24 сентября и не является текущим универсальным CI. Для этого ограниченного продолжения:

```bash
python audit_ufc_20260927.py --cache /tmp/sr-ufc-audit --write-results
```

Новая статическая проверка прошла: 77 трасс, включая 13 обязательных Apple DIRECT, 22 UFC PROXY, остальные сервисы/границы/локальные случаи; отдельно 44 сценария известных имён UFC с заданным российским или зарубежным IP. Это не встроенный движок Shadowrocket. Переданные IP и страны являются входными условиями теста; DNS и GeoIP из домашней сети не подставлялись. Вариант с известным IP проверяется дополнительно; no-resolve сам не запускает DNS.

Во всех 44 сценариях первым совпало локальное UFC PROXY до GEOIP. `ufc.com.example.org` и `notufc.com` не совпадают с SUFFIX ufc.com; для них сохранено обычное поведение. Без исходного имени общий IP CDN не может быть надёжно отнесён к UFC.

Для таблицы: R1=Advertising, R2=Runet DOMAIN-SET, R3=YouTube, R4=Discord, R5=Runet IP. Их полные URL и политики приведены выше. «RU?» означает, что без базы устройства первое GEOIP-совпадение неизвестно; обе ветви отражены. Базовая трассировка имён не выдумывает DNS-адрес. В столбце «Изменение» сравниваются правило/политика, а не просто сдвиг номера строки.

| Назначение | Первая строка итогового файла | Первое правило / совпадение списка | Политика | Изменение против базы |
|---|---:|---|---|---|
| `apple.com` | 37 | `DOMAIN-SUFFIX,apple.com,DIRECT` | DIRECT | нет |
| `setup.icloud.com` | 39 | `DOMAIN-SUFFIX,icloud.com,DIRECT` | DIRECT | нет |
| `guzzoni.apple.com` | 37 | `DOMAIN-SUFFIX,apple.com,DIRECT` | DIRECT | нет |
| `api.push.apple.com` | 37 | `DOMAIN-SUFFIX,apple.com,DIRECT` | DIRECT | нет |
| `appleid.apple.com` | 37 | `DOMAIN-SUFFIX,apple.com,DIRECT` | DIRECT | нет |
| `music.apple.com` | 37 | `DOMAIN-SUFFIX,apple.com,DIRECT` | DIRECT | нет |
| `apps.apple.com` | 37 | `DOMAIN-SUFFIX,apple.com,DIRECT` | DIRECT | нет |
| `apple-relay.cloudflare.com` | 81 | `DOMAIN,apple-relay.cloudflare.com,DIRECT` | DIRECT | нет |
| `apple-relay.fastly-edge.com` | 82 | `DOMAIN,apple-relay.fastly-edge.com,DIRECT` | DIRECT | нет |
| `cp4.cloudflare.com` | 93 | `DOMAIN,cp4.cloudflare.com,DIRECT` | DIRECT | нет |
| `17.57.146.140` | 101 | `IP-CIDR,17.0.0.0/8,DIRECT,no-resolve` | DIRECT | нет |
| `17.57.146.141` | 101 | `IP-CIDR,17.0.0.0/8,DIRECT,no-resolve` | DIRECT | нет |
| `17.57.146.135` | 101 | `IP-CIDR,17.0.0.0/8,DIRECT,no-resolve` | DIRECT | нет |
| `ufc.com` | 137 | `DOMAIN-SUFFIX,ufc.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `ufcfightpass.com` | 138 | `DOMAIN-SUFFIX,ufcfightpass.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `ufc.ru` | 141 | `DOMAIN-SUFFIX,ufc.ru,PROXY` | PROXY | раньше DIRECT; теперь явный UFC |
| `ufc.com.br` | 142 | `DOMAIN-SUFFIX,ufc.com.br,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `ufcespanol.com` | 143 | `DOMAIN-SUFFIX,ufcespanol.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `ufc.cn` | 144 | `DOMAIN-SUFFIX,ufc.cn,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `ufc.tv` | 140 | `DOMAIN-SUFFIX,ufc.tv,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `fightpass.com` | 139 | `DOMAIN-SUFFIX,fightpass.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `dce-frontoffice.imggaming.com` | 148 | `DOMAIN,dce-frontoffice.imggaming.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `ufc.api.onvesper.com` | 149 | `DOMAIN,ufc.api.onvesper.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `search.dce-prod.dicelaboratory.com` | 150 | `DOMAIN,search.dce-prod.dicelaboratory.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `guide.imggaming.com` | 151 | `DOMAIN,guide.imggaming.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `static.diceplatform.com` | 152 | `DOMAIN,static.diceplatform.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `content-images.onvesper.com` | 153 | `DOMAIN,content-images.onvesper.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `vod-images.onvesper.com` | 154 | `DOMAIN,vod-images.onvesper.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `www.ufc.com` | 137 | `DOMAIN-SUFFIX,ufc.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `jp.ufc.com` | 137 | `DOMAIN-SUFFIX,ufc.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `kr.ufc.com` | 137 | `DOMAIN-SUFFIX,ufc.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `www.ufcfightpass.com` | 138 | `DOMAIN-SUFFIX,ufcfightpass.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `app.ufcfightpass.com` | 138 | `DOMAIN-SUFFIX,ufcfightpass.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `app.ufc.tv` | 140 | `DOMAIN-SUFFIX,ufc.tv,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `us.ufcespanol.com` | 143 | `DOMAIN-SUFFIX,ufcespanol.com,PROXY` | PROXY | раньше DIRECT if RU; otherwise PROXY; теперь явный UFC |
| `yandex.ru` | 172 | `DOMAIN-SUFFIX,yandex.ru,DIRECT` | DIRECT | нет |
| `market.yandex.ru` | 172 | `DOMAIN-SUFFIX,yandex.ru,DIRECT` | DIRECT | нет |
| `api.market.yandex.ru` | 172 | `DOMAIN-SUFFIX,yandex.ru,DIRECT` | DIRECT | нет |
| `mail.ru` | 165 | `DOMAIN-SUFFIX,mail.ru,DIRECT` | DIRECT | нет |
| `vk.com` | 167 | `DOMAIN-SUFFIX,vk.com,DIRECT` | DIRECT | нет |
| `2gis.ru` | 183 | `DOMAIN-SUFFIX,2gis.ru,DIRECT` | DIRECT | нет |
| `2gis.com` | 184 | `DOMAIN-SUFFIX,2gis.com,DIRECT` | DIRECT | нет |
| `aviasales.ru` | 188 | `DOMAIN-SUFFIX,aviasales.ru,DIRECT` | DIRECT | нет |
| `aviasales.com` | 189 | `DOMAIN-SUFFIX,aviasales.com,DIRECT` | DIRECT | нет |
| `t.me` | 203 | `DOMAIN-SUFFIX,t.me,PROXY` | PROXY | нет |
| `telegram.org` | 207 | `DOMAIN-SUFFIX,telegram.org,PROXY` | PROXY | нет |
| `whatsapp.com` | 220 | `DOMAIN-SUFFIX,whatsapp.com,PROXY` | PROXY | нет |
| `graph.facebook.com` | 218 | `DOMAIN,graph.facebook.com,PROXY` | PROXY | нет |
| `openai.com` | 245 | `DOMAIN-SUFFIX,openai.com,PROXY` | PROXY | нет |
| `chatgpt.com` | 244 | `DOMAIN-SUFFIX,chatgpt.com,PROXY` | PROXY | нет |
| `claude.ai` | 248 | `DOMAIN-SUFFIX,claude.ai,PROXY` | PROXY | нет |
| `gemini.google.com` | 250 | `DOMAIN,gemini.google.com,PROXY` | PROXY | нет |
| `grok.com` | 253 | `DOMAIN-SUFFIX,grok.com,PROXY` | PROXY | нет |
| `perplexity.ai` | 258 | `DOMAIN-SUFFIX,perplexity.ai,PROXY` | PROXY | нет |
| `youtube.com` | 239 | `RULE-SET,R3,PROXY`; entry 57: DOMAIN-SUFFIX,youtube.com | PROXY | нет |
| `discord.com` | 240 | `RULE-SET,R4,PROXY`; entry 14: DOMAIN-SUFFIX,discord.com | PROXY | нет |
| `ebay.com` | 264 | `DOMAIN-SUFFIX,ebay.com,PROXY` | PROXY | нет |
| `paypal.com` | 267 | `DOMAIN-SUFFIX,paypal.com,PROXY` | PROXY | нет |
| `bybit.com` | 269 | `DOMAIN-SUFFIX,bybit.com,PROXY` | PROXY | нет |
| `redotpay.com` | 195 | `DOMAIN-SUFFIX,redotpay.com,PROXY` | PROXY | нет |
| `helpcenter.redotpay.com` | 195 | `DOMAIN-SUFFIX,redotpay.com,PROXY` | PROXY | нет |
| `kino.pub` | 238 | `DOMAIN-SET,R2,PROXY`; entry 538679: kino.pub | PROXY | нет |
| `api.service-kp.com` | 276 | `DOMAIN,api.service-kp.com,PROXY` | PROXY | нет |
| `192.168.1.1` | 26 | `IP-CIDR,192.168.0.0/16,DIRECT,no-resolve` | DIRECT | нет |
| `10.1.30.1` | 27 | `IP-CIDR,10.0.0.0/8,DIRECT,no-resolve` | DIRECT | нет |
| `172.16.1.1` | 28 | `IP-CIDR,172.16.0.0/12,DIRECT,no-resolve` | DIRECT | нет |
| `audit.local` | 30 | `DOMAIN-SUFFIX,local,DIRECT` | DIRECT | нет |
| `ufc.com.example.org` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `notufc.com` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `other.imggaming.com` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `other.onvesper.com` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `cloudflare.com` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `example.akamaized.net` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `example.cloudfront.net` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `example.fastly.net` | 285 | `GEOIP,RU,DIRECT [if RU]; FINAL,PROXY [otherwise]` | DIRECT if RU; otherwise PROXY | нет |
| `unknown-ufc-audit.example [GeoIP non-RU]` | 293 | `FINAL,PROXY` | PROXY | нет |
| `224.0.0.251` | 7 | `tun-excluded-routes = …224.0.0.0/4…` | Excluded from tunnel | нет |

Фактическое изменение политики особенно существенно для `ufc.ru`: раньше DIRECT как при GEOIP RU, так и при попадании в `.ru` после GEOIP; теперь PROXY. Остальные подтверждённые имена UFC раньше зависели от GEOIP/FINAL, теперь имеют явный приоритет. Это устраняет зависимость от российского адреса CDN, но не меняет регион учётной записи, подписки или лицензионные права.

## DNS, локальная сеть и Apple

[General] и [Host] побайтно совпали с базой. Сохранены system DNS, все пять DNS-параметров, ipv6/prefer-ipv6, bypass-system, private-ip-answer, UDP REJECT и остальные настройки. Доказанного нового дефекта DNS/транспорта нет; глобальная схема не менялась. IPv6-правила не удалены. При непредусмотренном разрешении/ошибке DNS нужно смотреть журнал устройства.

Для 192.168.1.1, 10.1.30.1 и 172.16.1.1 проверены принадлежность tun-excluded-routes и прежние DIRECT-правила, а также сохранность skip-proxy с приватными сетями, localhost и *.local. Для audit.local проверено суффиксное DIRECT; для 224.0.0.251 проверено исключение 224.0.0.0/4 на уровне туннеля. Эти механизмы не объединялись и не удалялись как дубликаты. Реальные Bonjour/AirPlay/межсетевые VLAN-пути и IPv6 на tvOS не испытывались. DIRECT внутри приложения не отменяет VPN-политику роутера.

## Полный diff конфигурации текущего запуска

```diff
diff --git a/ru_direct_runetfreedom_improved_final_autoupdate.conf b/ru_direct_runetfreedom_improved_final_autoupdate.conf
index cd4f7b2..22a7fd1 100644
--- a/ru_direct_runetfreedom_improved_final_autoupdate.conf
+++ b/ru_direct_runetfreedom_improved_final_autoupdate.conf
@@ -132,0 +133,23 @@ IP-CIDR,2a01:b740::/29,DIRECT,no-resolve
+# -------------------------------
+# UFC / UFC Fight Pass — PROXY
+# Official sites, regional editions and the active legacy redirect.
+# -------------------------------
+DOMAIN-SUFFIX,ufc.com,PROXY
+DOMAIN-SUFFIX,ufcfightpass.com,PROXY
+DOMAIN-SUFFIX,fightpass.com,PROXY
+DOMAIN-SUFFIX,ufc.tv,PROXY
+DOMAIN-SUFFIX,ufc.ru,PROXY
+DOMAIN-SUFFIX,ufc.com.br,PROXY
+DOMAIN-SUFFIX,ufcespanol.com,PROXY
+DOMAIN-SUFFIX,ufc.cn,PROXY
+
+# Exact shared-platform hosts used by the public Fight Pass web application.
+# These rules also affect other services using the same hostnames.
+DOMAIN,dce-frontoffice.imggaming.com,PROXY
+DOMAIN,ufc.api.onvesper.com,PROXY
+DOMAIN,search.dce-prod.dicelaboratory.com,PROXY
+DOMAIN,guide.imggaming.com,PROXY
+DOMAIN,static.diceplatform.com,PROXY
+DOMAIN,content-images.onvesper.com,PROXY
+DOMAIN,vod-images.onvesper.com,PROXY
+
@@ -159,4 +181,0 @@ DOMAIN-SUFFIX,yandexcloud.net,DIRECT
-# Yandex Market
-DOMAIN-SUFFIX,market.yandex.ru,DIRECT
-DOMAIN,api.market.yandex.ru,DIRECT
-
@@ -177 +195,0 @@ DOMAIN-SUFFIX,redotpay.com,PROXY
-DOMAIN,helpcenter.redotpay.com,PROXY
```

## Файлы, публикация и проверка на Apple TV

Изменены только профиль и HANDOFF; добавлены этот отчёт, `audit_ufc_20260927.py`, `audit/ufc-evidence-20260927.json`, `audit/ufc-results-20260927.json`. Сырые HTML/JS/realm с техническими ключами и большие внешние списки остаются вне репозитория. Чужих изменений в исходной рабочей директории не было.

Проверка сохранения 2026-09-27T03:55:12.618646+00:00: операция создания рабочей ветки через подключение GitHub была прервана. Последующий git ls-remote подтвердил, что remote-ветка codex/ufc-proxy-dedup-20260927 не создана, main остаётся 780a5d0f29326fc1242f66288ecbd3a75bf52fe1. Повторно прочитан действующий update-url: HTTP 200, 9902 байта, прежний SHA256 0fc24453eb6d2fb11537067c554f90aa55c0c9fb8b95511e6728006ad9ce106d, UFC-блока нет. Изменения сохранены только в локальной рабочей ветке, отправки нет. Создание remote-ветки после прерывания не повторялось. Main/история/Apple TV не изменены. Идентификатор локального коммита доступен через git log -1 этой ветки; это не подтверждение публикации.

Для проверки до слияния импортируй изменённый файл как временную копию и явно выбери её; не нажимай в ней обновление по прежнему update-url, иначе загрузится версия main. Убедись, что используется режим конфигурационных правил. Сам update-url в файле остаётся неизменным по условию задачи. После разрешённого слияния можно обновить основной профиль и удалить временную копию.

1. Переоткрой соединения: останови/запусти Shadowrocket и перезапусти UFC. Проверь вход, каталог и поиск.
2. Запусти доступную по подписке запись, затем доступную прямую трансляцию; проверь старт, перемотку, звук и субтитры. Несколько раз повтори один материал с тем же качеством и сервером.
3. В журнале UFC-имена должны показывать новые DOMAIN/DOMAIN-SUFFIX и PROXY. Соединение с основным объёмом данных определяет фактический CDN; отдельно проверь узлы после перенаправлений и ошибки лицензии. Для неизвестных имён политика может остаться GEOIP/DIRECT/FINAL, пока узел не подтверждён.
4. Проверь Apple Account/App Store и локальный AirPlay/HomePod: Apple DIRECT сохранён. Проверь KinoPub/MicroIPTV и российские сервисы как короткую функциональную регрессию.
5. Для разбора нужны только домен, первое правило/список, политика, ошибка, объём и время старта. Не передавай пароль, cookies, ключ, токен, полный URL манифеста/лицензии или подписанную ссылку.

Откат только текущих изменений: выбери прежний рабочий профиль либо удали добавленный UFC-блок и восстанови три строки из diff; до слияния main уже содержит прежнюю версию. После будущего слияния используй revert соответствующего конфигурационного коммита, без reset/force push и без отката предыдущего Apple-аудита.

Импорт и фактическое воспроизведение в Shadowrocket/tvOS не проверены. Не подтверждены все динамические CDN/DRM-host, нативные tvOS-отличия API, домашний DNS/GeoIP, исходный домен при IP-only соединении и активность дополнительных российских aliases. Маршрутизация не гарантирует доступ к контенту и не добавляет кодеки/HDR/Dolby Vision.
