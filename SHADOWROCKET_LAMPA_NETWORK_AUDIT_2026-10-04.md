# Apple TV / Lampa MX / KinoPub / Infuse: сетевой аудит

Проверка: 04.10.2026, UTC; местное время пользователя UTC+5. Репозиторий `aomikh/shadowrocket-configs`. Рабочий профиль `ru_direct_runetfreedom_improved_final_autoupdate.conf`.

## Результат

Добавлены только два точных правила: `DOMAIN,api.themoviedb.org,PROXY` и `DOMAIN,image.tmdb.org,PROXY`, после полного Apple/UFC-блока, перед Advertising. Это закрепление маршрута TMDB при отключённом дополнительном прокси Lampa. Ранее без доступного адресного совпадения эти имена доходили до `GEOIP,RU,DIRECT` либо `FINAL,PROXY`: отдельная политика не была гарантирована. Изменение устраняет эту зависимость, но **не доказывает**, что именно она вызвала ошибки пользователя или что текущий адрес TMDB определяется устройством как российский.

Доказанной сетевой причины обрыва Infuse, ошибки размера файла или рекламного экрана нет. Новых DIRECT-исключений для видео нет: фактический видеохост текущего Infuse, его ответы и прямой доступ из домашней сети неизвестны. Правила служебного KinoPub уже PROXY; нет основания менять их. `kinopub.fastcdn.pics` не блокируется отдельным диагностическим правилом, убирать такой REJECT не требуется.

Сохранены побайтно: [General], [Host], адрес обновления, локальные правила, весь Apple-блок с 75 правилами, UFC с 15 правилами и весь текст начиная с REJECT-блока. Сохранены российские суффиксы ru/su/xn--p1ai, поздний GEOIP,RU, пять внешних списков, FINAL,PROXY. Новых узлов, групп, широких CDN-исключений, переопределений HTTPS и корневых сертификатов нет. Плагин и соседний репозиторий не изменялись.

## Исходная версия и публикация

- Исходная локальная ветка: `codex/ufc-proxy-dedup-20260927`, HEAD `7489cd666d30a30ab996f4da17ae26ee39b95189`, чистая рабочая директория.
- Актуальный main после fetch: `fac9dc3ad6e139ff073663400a18a64df272b82a`; его дерево `7d03815721cc4eac243cb2673aa05d84afb9fd90` совпало с локальным. UFC уже объединён пользователем. Старый HANDOFF корректен как история, но его прежний статус «не опубликовано» устарел.
- [Действующий update-url](https://raw.githubusercontent.com/aomikh/shadowrocket-configs/main/ru_direct_runetfreedom_improved_final_autoupdate.conf) проверен 09:40:31 UTC: HTTP 200, text/plain, 10609 байт, SHA256 `824e0e0bb769a415428046f99d926aed94db88fb9d40f76a3f61d92c6460da30`; совпал с main и локальной копией. Проверены секции и FINAL, исключены HTML и пустой ответ.
- Рабочая ветка аудита: `codex/lampa-network-audit-20261004` от актуального main. AGENTS.md, README, CI и обязательного процесса PR нет. API сообщает `protected=false`, применимые правила ветки пусты; подключение имеет push. Текущая задача разрешает публикацию в main после проверки без force push.
- До записи main повторно сверяется с исходной ревизией. Окончательный статус публикации фиксируется в HANDOFF после чтения GitHub и update-url. Наличие файла в GitHub не означает загрузку профиля на Apple TV.

## Источники и воспроизводимость

Все источники проверены 04.10.2026. Метаданные, время загрузки, SHA256 и Git blob внешних списков: `audit/lampa-network-evidence-20261004.json`. Снимки проверяются по хэшу; списки не копируются в репозиторий. Полные медиассылки, пользовательские токены, подписки и необезличенные журналы не сохраняются.

| Источник | Версия | Подтверждённый факт и граница |
|---|---|---|
| [TMDB: изображения](https://developer.themoviedb.org/docs/image-basics), [изображения эпизодов](https://developer.themoviedb.org/reference/tv-episode-images) | Текущие страницы 04.10.2026 | image.tmdb.org доставляет изображения; api.themoviedb.org возвращает данные эпизодов. Метод возвращает существующие изображения и применяет языковые фильтры; не гарантирует кадр для каждого эпизода. |
| [Lampa TMDB](https://github.com/yumata/lampa-source/blob/b4a13b6af7fe2f3bbbcb91f4eb434ab3378f8d5d/src/core/tmdb/tmdb.js) | b4a13b6, 03.10.2026 | При выключенном proxy_tmdb стандартные адреса идут непосредственно на эти два хоста. В конкретной установленной оболочке и её настройках это нужно проверить. |
| [KinoPub API](https://kinoapi.com/api_video.html) | Документация v1.3 | Служебные методы media-links и media-video-link на api.service-kp.com. Файловые ссылки и субтитры возвращаются динамически. Нет основания подменять имя сервера, параметры региона или подпись вручную. |
| [Код плагина](https://github.com/aomikh/lampa_kinopub/blob/011fdf5b3a90078ed6d6981cc1240765e7f3186d/docs/kp.js) | 1.0.73-mx.4 | API_HOST, KP_PROXY_URL; прямой файловый путь Infuse, отдельные health/voice-sync и ограничение manifest-proxy сценариями Tizen. Код не показывает фактический домен подписанного файла пользователя. |
| [HANDOFF плагина](https://github.com/aomikh/lampa_kinopub/blob/011fdf5b3a90078ed6d6981cc1240765e7f3186d/HANDOFF_LAMPA_MX_KINOPUB.md), [установка](https://github.com/aomikh/lampa_kinopub/blob/011fdf5b3a90078ed6d6981cc1240765e7f3186d/INSTALL_LAMPA_MX.md) | 011fdf5, 04.10.2026 | После mx.3 пользователь сообщил об обрыве после начала видео. mx.4 сокращает подготовку файловой ссылки и добавляет ручную диагностику. Устранение обрыва на устройстве не подтверждено. |
| [Firecore: сторонние приложения](https://support.firecore.com/hc/en-us/articles/215090997-API-for-Third-Party-Apps-Services) | 12.06.2026, Infuse 8.4.7+ | Внешняя передача url/sub и временного плейлиста. Успешная передача ссылки не доказывает успешное воспроизведение. |
| [Справка Shadowrocket](https://github.com/LOWERTOP/Shadowrocket/blob/3537f928451038ba74258eccbb6d9bd7865628dd/README.md), lazy.conf той же ревизии | 3537f928, 26.09.2026 | Справка именно Shadowrocket, но общественный неофициальный проект. Основание для ограниченной статической модели; не исходный код приложения и не гарантия поведения конкретной версии tvOS. |

Ссылка плагина: `https://aomikh.github.io/lampa_kinopub/kp.js`. Ответ 09:41:36 UTC: HTTP 200, application/javascript, 224473 байта, SHA256 `2cabdbf27cc1d4ea8ebf637ab5f18e236aed8a5f3d684c5e154774d5dbb5574c`, совпадает с docs/kp.js ревизии 011fdf5. Документация рекомендует тот же файл с `?v=1.0.73-mx.4` для обновления кэша; параметр не закрепляет старую версию. Последняя известная пользовательская ссылка была mx.3. Факт установки mx.4 неизвестен. Зеркало не переключалось.

jsDelivr не найден как загрузчик в текущем опубликованном kp.js или установочной инструкции. Его контрольный hostname проверен только как кандидат; отдельное правило не добавлено. Для aomikh.github.io и raw.githubusercontent.com также нет доказанного конфликта, поэтому маршруты сохранены. Доменные исключения, если понадобятся, затронут все ресурсы данного хоста, а не один файл; широкие github.io/githubusercontent.com/jsdelivr.net не добавлялись.

## KinoPub и реальный видеопоток

`kino.pub` и `www.kino.pub` сначала совпадают с Runet Freedom DOMAIN-SET, строки списка 538679 и 1304082, политика PROXY. Сохраняется локальная страховка DOMAIN-SUFFIX,kino.pub,PROXY (строка 279 нового профиля), работающая независимо от этих записей. `api.service-kp.com` первым совпадает с точным PROXY, строка 281.

`kinopub.fastcdn.pics`: строки кода 66, 1091, 1154, 1802 и 5002 подтверждают проверку /health, синхронизацию выбора озвучек и manifest-proxy. `useManifestProxy` ограничен Tizen и определёнными плеерами; `preferredFormat('infuse')` возвращает http. Infuse получает свежую ссылку на файл через API, а не этот преобразователь. Фоновая служебная активность Lampa на fastcdn всё ещё возможна. Это не обязательно для MicroIPTV и не доказательство передачи основного объёма видео через fastcdn. Ни REJECT, ни DIRECT, ни новое PROXY для него не добавлены: подтверждённого текущего сбоя его маршрута нет.

cdn2cdn.com, cdn2site.com, digital-cdn.net, cdntogo.net остаются на прежних правилах. Их роль кандидатов поддерживается исходниками proxy-server и историческими материалами, но заголовок whitelist в server.js устарел относительно реализации. Выборка `logs/1.0.27_hls4.txt` соседнего репозитория содержит cdn2cdn.com/cdn2site.com/digital-cdn.net и маркеры Tizen/AVPlay, без Infuse/AppleTV. Это чужой исторический сценарий, не измерение пользователя. Актуального видеоподдомена Infuse/MicroIPTV и доменов перенаправлений нет. Одно лишь открытие корня CDN ничего не говорит о подписанном ресурсе.

Не доказаны привязка ссылки к адресу выхода или её отсутствие, скорость, устойчивость, перемотка, доступность субтитров и следующих серий. Действующая общая логика уже может давать DIRECT российскому IP; новый массовый DIRECT не вводится. В таблице условный результат означает именно неизвестность IP и геобазы, а не проведённый сетевой тест.

## TMDB и причины симптомов

Два новых правила закрепляют PROXY до Advertising, широких адресных и географических правил. Они действуют для любого приложения, обращающегося к двум точным хостам, включая Infuse и другие устройства с этим профилем. Не охватывают весь themoviedb.org/tmdb.org, их посторонние поддомены или общие CDN. Приоритет локальных/Apple-исключений сохранён.

В снимках списков нет доменного совпадения Advertising для проверенных служебных хостов. Полные подписанные пути и IP устройства отсутствуют, поэтому нельзя заявить проверку любого URL-REGEX или будущего адресного совпадения. Добавление точных TMDB-правил также ставит подтверждённые хосты выше таких общих правил. Отключение всей рекламы не требовалось.

По `audit/vosmidyesyatye-tmdb.json` соседней задачи, 04.10.2026 07:14 UTC у первого сезона «Восьмидесятых» (TMDB 50666) 21/21 эпизод без still_path. Это сохранённый результат запроса из среды аудита, не новая проверка Apple TV. Исправление сети не создаёт такие кадры. Другая ситуация: корректный URL изображения есть, но запрос ошибочен; тогда нужны статус и маршрут именно image.tmdb.org. Потеря thumbnail или ошибочное построение URL относятся к плагину.

`Server didn't report the size of the file` не определяет причину. Ранее соседняя задача проверила публичный тестовый MP4 Firecore: HEAD 200 с размером, Range GET 206 с Content-Range. Публичный тестовый manifest-proxy ответил манифестом без Content-Length и не выполнил Range. Это различие ресурсов, **не ответ фактического файла пользователя** и не доказательство причины его ошибки. Завершённые тесты повторно не выполнялись. Свежей разрешённой медиассылки пользователя нет, фильм не скачивался. mx.4 содержит ручной HEAD/Range диагностический экран; ограничения CORS нужно учитывать отдельно от ошибок Infuse.

«Реклама» может формироваться кодом Lampa: в изученной ревизии есть отдельный `src/interaction/advert/preroll.js`. Сетевое блокирование рекламного запроса и корректное завершение ожидания в приложении различны. Нет журнала, доказывающего зависший REJECT в данном запуске; сетевое «исправление рекламы» не заявляется. Подписки/учётные записи/CUB не менялись.

## DNS, локальная сеть и роутер

Все восемь перечисленных пользователем параметров совпали с исходным файлом: dns-server=system, fallback-dns-server=system, dns-fallback-system=false, dns-direct-system=false, dns-direct-fallback-proxy=false, ipv6=false, prefer-ipv6=false, udp-policy-not-supported-behaviour=REJECT. Сохранены также bypass-system и private-ip-answer. Дефекта DNS по доступным данным не обнаружено.

По общественной справке Shadowrocket DIRECT использует настроенное разрешение имён; здесь выбран system. dns-direct-system=false не превращает system в другой DNS и не означает запрет системных запросов. PROXY-домены могут разрешаться удалённо выбранным узлом; IP/GEOIP-правила могут потребовать локального разрешения до выбора маршрута. Поэтому PROXY у соединения не доказывает, что любой предшествующий DNS-запрос шёл через прокси. Точный путь зависит от типа узла и состояния клиента, которые в этом файле не заданы.

fallback-dns-server=system не создаёт независимого резерва при основном system. Справка описывает fallback после ошибки/задержки; точное взаимодействие скрытого dns-fallback-system=false с данной сборкой не подтверждено. dns-direct-fallback-proxy=false отключает переход к прокси при неудачном разрешении DIRECT, а не переключает весь DNS на DIRECT. При отказе разрешения нельзя обещать успешное восстановление. Адреса системных DNS Apple TV/роутера неизвестны. Новых шифрованных DNS, [Host]-подмен или параметров fake-IP не вводилось; внутреннее использование fake-IP клиентом по отсутствию параметра не определяется.

no-resolve не инициирует DNS для сопоставления адресного правила. Основная модель пропускает такие правила для доменного запроса согласно справке; отдельно проверен вариант уже известного адреса как анализ чувствительности. Это не утверждение о внутреннем кэше Shadowrocket. Обычный системный DNS среды Codex вернул temporary failure для всех проб, включая доступный по HTTP GitHub; это ограничение среды, не доказательство сбоя DNS пользователя. Домашняя DNS-проверка не подменяется запросами Codex.

skip-proxy содержит частные сети, localhost и *.local. Его нельзя приравнивать к обходу VPN: по справке он выбирает TUN вместо системного прокси-интерфейса. Прямую локальную обработку обеспечивают сохранённые [Rule] и tun-excluded-routes. Последний исключает частные сети и 224.0.0.0/4, включая mDNS 224.0.0.251 и SSDP 239.255.255.250. Имена .local имеют DOMAIN-SUFFIX DIRECT, [Host] содержит только localhost=127.0.0.1. Новые широкие IPv6-исключения не вводились, существующие Apple IPv6 сохранены. Bonjour/HomeKit/AirPlay между сегментами, IPv6/Thread/Matter и фактическое обнаружение требуют устройства.

Из доступного контекста известно о Keenetic с AmneziaWG, но актуальной политики для Apple TV и свежего self-test в этой рабочей среде нет. Нельзя утверждать, что Apple TV принудительно направлен в VPN роутера или исключён из него. DIRECT Shadowrocket отменить вышестоящий VPN не может. Для пробы сравнить привязку Apple TV к политике подключений в Keenetic, не подставлять адрес Samsung/Tizen.

## Проверки и ограничения

Существующий `audit_ufc_20260927.py` выполнен на исходном профиле: 77 трасс, 44 сценария. Его исторические ожидания количества правил и изменений не переписывались. Текущая проверка: `python audit_lampa_network_20261004.py --cache /tmp/sr-lampa --write-results`. Результат: 189 правил, 79 трасс, 68 сценариев TMDB/UFC с заданными RU/non-RU адресами и двумя вариантами no-resolve. JSON: `audit/lampa-network-results-20261004.json`.

Проверены структура секций, поля и политики, доменные границы, строгие IPv4/IPv6-префиксы, no-resolve, URL списков, окончания строк, точные дубли, безопасная избыточность локальных правил, сохранение порядка и побайтная неизменность остальных блоков. Точных дубликатов и доказанно лишних поздних локальных правил нет. Намеренные ранние узкие Apple-префиксы, KEYWORD и локальные страховки внешних списков сохранены. `git diff --check` пройден. У всех 77 не-TMDB контрольных назначений прежний семантический результат; номера поздних строк увеличились на 5.

Все пять внешних списков доступны. Advertising: 781 активная запись, новая ревизия заголовка; остальные четыре списка совпали с предыдущими снимками. Runet DOMAIN-SET: 1534624 записи; YouTube: 190; Discord: 29; Runet IP: 88586. Внутренних политик в списках нет, политика берётся из строки подключения. Известная строка Runet 269745 `dokumentam24.ru,` остаётся внешней аномалией; обработка ошибки нативным импортёром неизвестна. Unicode-имена не объявлялись ошибочными и весь внешний список не рефакторился.

Это ограниченная статическая модель: не выполняет импорт Shadowrocket, реальные DNS/GeoIP/CNAME/fake-IP, нормализацию международных имён, URL/USER-AGENT без входных данных и выбор режима в приложении. Apple/UFC проверены как сохранённые маршруты, а не новый полный инвентарный аудит. Реальное устройство и подписанное видео не проверены. FINAL,PROXY означает последний маршрут при работающих правилах, а не автоматически выбранный пользователем глобальный режим «весь трафик через прокси».

## Проверка только на Apple TV

1. Обновить именно действующий профиль по сохранённому update-url. Проверить наличие двух новых DOMAIN TMDB и активность этого профиля, затем режим применения правил конфигурации Shadowrocket.
2. Для сравнения DIRECT выяснить политику Apple TV в Keenetic. Закрыть Lampa MX, Infuse и MicroIPTV; переоткрыть соединения после обновления правил. Старые сокеты не доказывают действие новых правил.
3. Проверить установленный KinoPub: единственная актуальная копия с редакцией mx.4. В Lampa, если сборка позволяет: «Включить прокси автоматически» = Нет; «Проксировать TMDB» = Нет; пользовательские API и Image пустые. Эти настройки удалённо не изменялись.
4. Проверить каталог, поиск, авторизацию, данные TMDB и отдельную загрузку заведомо существующей картинки. Отсутствующий still_path не считать отказом image.tmdb.org.
5. Тот же материал KinoPub, фиксированные качество и сервер: минимум три запуска, затем 1080p и тяжёлый 4K; фиксировать время подготовки в Lampa отдельно от старта Infuse, перемотку, следующую серию, звук, субтитры, минуту обрыва/буферизации. HDR/Dolby Vision проверять только при поддержке всей цепочкой.
6. По журналу Shadowrocket найти соединение с основным объёмом передачи, его hostname, первое правило/внешний список и политику. Отдельно отметить дополнительные хосты субтитров/редиректов. Не приравнивать маленький запрос манифеста к большому потоку.
7. После сбоя вернуться в ту же работающую сессию Lampa: Настройки → KinoPub → Диагностика Infuse. Сопоставить безопасные HEAD/Range статусы и конечный hostname с журналом. Недоступный через CORS заголовок не означает отсутствие заголовка у Infuse. HTTP 401/403, тайм-аут, HTML вместо видео и ошибка формата требуют разных проверок; не подменять диагноз.
8. Проверить MicroIPTV → KinoPub, App Store/Apple Account, HomePod/AirPlay и UFC/Fight Pass. Требуемые сведения: домен, правило, политика, ошибка, объём, время старта/перемотки; без паролей, токенов и полных медиассылок.

Минимальная DIRECT-проба только после определения реального видеохоста: временно вставить **одну** строку `DOMAIN,<фактический_видеохост>,DIRECT` после Apple/UFC и до Advertising; угловые скобки заменить именем из журнала, не копировать пример как готовое правило. API оставить PROXY, получить свежую ссылку штатно. На одинаковом материале/качестве/сервере сравнить несколько запусков и перемоток, проверить авторизацию и редиректы. При отказе убрать только эту строку и переоткрыть приложения. В основной опубликованный профиль пробное правило не включено, второй постоянный профиль не создан. Положительный результат требуется отдельно для Infuse и MicroIPTV; затем можно обсуждать постоянное узкое исключение.

Откат текущей сетевой правки: удалить только два DOMAIN TMDB и два поясняющих комментария из diff ниже, сохранить файл и обновить профиль; либо отменить только конфигурационный коммит этого запуска через git revert после проверки последующих изменений. Не откатывать прежние коммиты Apple/UFC. Исходный конфиг доступен в fac9dc3. Изменение профиля само по себе не меняет плагин mx.4.

## Полная разница конфигурации текущего запуска

```diff
@@ -153,6 +153,11 @@ DOMAIN,static.diceplatform.com,PROXY
 DOMAIN,content-images.onvesper.com,PROXY
 DOMAIN,vod-images.onvesper.com,PROXY
 
+# TMDB metadata and images: keep routing independent of GEOIP fallback.
+# Exact hosts used by Lampa without its optional in-app TMDB proxy.
+DOMAIN,api.themoviedb.org,PROXY
+DOMAIN,image.tmdb.org,PROXY
+
 # -------------------------------
 # REJECT block
 # -------------------------------
```

Итоговый SHA256 конфигурации: `c7d1df4f17977406a71debbfb411d7d3fbaaa365e46fc0587ce7fbcca2d9ad45`. Кроме конфигурации изменён только HANDOFF, добавлены этот отчёт, относящийся к задаче статический скрипт и два JSON с результатами/источниками.

## Все статические трассировки

В таблице «RU»/«не RU» обозначают сценарии базы GeoIP, не фактические IP пользователя. Адресные no-resolve и неизвестные URL/UA имеют ограничения выше. Списки сокращены до имени файла; их полные URLs и хэши находятся в JSON. Точные записи внешнего совпадения указаны в последнем столбце. Номера относятся к конфигурационному файлу, номера entry к внешнему списку.

| Назначение | Первое правило до | Первое правило после | Политика после | Изменение; основание |
|---|---|---|---|---|
| apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| appleid.apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| setup.icloud.com | 39: DOMAIN-SUFFIX,icloud.com,DIRECT | 39: DOMAIN-SUFFIX,icloud.com,DIRECT | DIRECT | нет; Domain |
| guzzoni.apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| gateway.push.apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| api.push.apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| apps.apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| music.apple.com | 37: DOMAIN-SUFFIX,apple.com,DIRECT | 37: DOMAIN-SUFFIX,apple.com,DIRECT | DIRECT | нет; Domain |
| apple-relay.cloudflare.com | 81: DOMAIN,apple-relay.cloudflare.com,DIRECT | 81: DOMAIN,apple-relay.cloudflare.com,DIRECT | DIRECT | нет; Domain |
| apple-relay.fastly-edge.com | 82: DOMAIN,apple-relay.fastly-edge.com,DIRECT | 82: DOMAIN,apple-relay.fastly-edge.com,DIRECT | DIRECT | нет; Domain |
| cp4.cloudflare.com | 93: DOMAIN,cp4.cloudflare.com,DIRECT | 93: DOMAIN,cp4.cloudflare.com,DIRECT | DIRECT | нет; Domain |
| 17.57.146.140 | 101: IP-CIDR,17.0.0.0/8,DIRECT,no-resolve | 101: IP-CIDR,17.0.0.0/8,DIRECT,no-resolve | DIRECT | нет; Literal address |
| 17.57.146.141 | 101: IP-CIDR,17.0.0.0/8,DIRECT,no-resolve | 101: IP-CIDR,17.0.0.0/8,DIRECT,no-resolve | DIRECT | нет; Literal address |
| 17.57.146.135 | 101: IP-CIDR,17.0.0.0/8,DIRECT,no-resolve | 101: IP-CIDR,17.0.0.0/8,DIRECT,no-resolve | DIRECT | нет; Literal address |
| ufc.com | 137: DOMAIN-SUFFIX,ufc.com,PROXY | 137: DOMAIN-SUFFIX,ufc.com,PROXY | PROXY | нет; Domain |
| ufcfightpass.com | 138: DOMAIN-SUFFIX,ufcfightpass.com,PROXY | 138: DOMAIN-SUFFIX,ufcfightpass.com,PROXY | PROXY | нет; Domain |
| ufc.ru | 141: DOMAIN-SUFFIX,ufc.ru,PROXY | 141: DOMAIN-SUFFIX,ufc.ru,PROXY | PROXY | нет; Domain |
| ufc.com.br | 142: DOMAIN-SUFFIX,ufc.com.br,PROXY | 142: DOMAIN-SUFFIX,ufc.com.br,PROXY | PROXY | нет; Domain |
| ufcespanol.com | 143: DOMAIN-SUFFIX,ufcespanol.com,PROXY | 143: DOMAIN-SUFFIX,ufcespanol.com,PROXY | PROXY | нет; Domain |
| ufc.cn | 144: DOMAIN-SUFFIX,ufc.cn,PROXY | 144: DOMAIN-SUFFIX,ufc.cn,PROXY | PROXY | нет; Domain |
| ufc.tv | 140: DOMAIN-SUFFIX,ufc.tv,PROXY | 140: DOMAIN-SUFFIX,ufc.tv,PROXY | PROXY | нет; Domain |
| fightpass.com | 139: DOMAIN-SUFFIX,fightpass.com,PROXY | 139: DOMAIN-SUFFIX,fightpass.com,PROXY | PROXY | нет; Domain |
| dce-frontoffice.imggaming.com | 148: DOMAIN,dce-frontoffice.imggaming.com,PROXY | 148: DOMAIN,dce-frontoffice.imggaming.com,PROXY | PROXY | нет; Domain |
| ufc.api.onvesper.com | 149: DOMAIN,ufc.api.onvesper.com,PROXY | 149: DOMAIN,ufc.api.onvesper.com,PROXY | PROXY | нет; Domain |
| search.dce-prod.dicelaboratory.com | 150: DOMAIN,search.dce-prod.dicelaboratory.com,PROXY | 150: DOMAIN,search.dce-prod.dicelaboratory.com,PROXY | PROXY | нет; Domain |
| guide.imggaming.com | 151: DOMAIN,guide.imggaming.com,PROXY | 151: DOMAIN,guide.imggaming.com,PROXY | PROXY | нет; Domain |
| static.diceplatform.com | 152: DOMAIN,static.diceplatform.com,PROXY | 152: DOMAIN,static.diceplatform.com,PROXY | PROXY | нет; Domain |
| content-images.onvesper.com | 153: DOMAIN,content-images.onvesper.com,PROXY | 153: DOMAIN,content-images.onvesper.com,PROXY | PROXY | нет; Domain |
| vod-images.onvesper.com | 154: DOMAIN,vod-images.onvesper.com,PROXY | 154: DOMAIN,vod-images.onvesper.com,PROXY | PROXY | нет; Domain |
| api.themoviedb.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | 158: DOMAIN,api.themoviedb.org,PROXY | PROXY | да; Domain |
| image.tmdb.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | 159: DOMAIN,image.tmdb.org,PROXY | PROXY | да; Domain |
| kino.pub | 238: DOMAIN-SET,antifilter-download.txt,PROXY | 243: DOMAIN-SET,antifilter-download.txt,PROXY | PROXY | нет; entry 538679: kino.pub |
| www.kino.pub | 238: DOMAIN-SET,antifilter-download.txt,PROXY | 243: DOMAIN-SET,antifilter-download.txt,PROXY | PROXY | нет; entry 1304082: www.kino.pub |
| api.service-kp.com | 276: DOMAIN,api.service-kp.com,PROXY | 281: DOMAIN,api.service-kp.com,PROXY | PROXY | нет; Domain |
| kinopub.fastcdn.pics | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| cdn2cdn.com | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| cdn2site.com | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| digital-cdn.net | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| cdntogo.net | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| aomikh.github.io | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| raw.githubusercontent.com | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| cdn.jsdelivr.net | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| lampa.mx | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| s.fastcdn.pics | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| yandex.ru | 172: DOMAIN-SUFFIX,yandex.ru,DIRECT | 177: DOMAIN-SUFFIX,yandex.ru,DIRECT | DIRECT | нет; Domain |
| mail.ru | 165: DOMAIN-SUFFIX,mail.ru,DIRECT | 170: DOMAIN-SUFFIX,mail.ru,DIRECT | DIRECT | нет; Domain |
| vk.com | 167: DOMAIN-SUFFIX,vk.com,DIRECT | 172: DOMAIN-SUFFIX,vk.com,DIRECT | DIRECT | нет; Domain |
| 2gis.ru | 183: DOMAIN-SUFFIX,2gis.ru,DIRECT | 188: DOMAIN-SUFFIX,2gis.ru,DIRECT | DIRECT | нет; Domain |
| aviasales.ru | 188: DOMAIN-SUFFIX,aviasales.ru,DIRECT | 193: DOMAIN-SUFFIX,aviasales.ru,DIRECT | DIRECT | нет; Domain |
| telegram.org | 207: DOMAIN-SUFFIX,telegram.org,PROXY | 212: DOMAIN-SUFFIX,telegram.org,PROXY | PROXY | нет; Domain |
| whatsapp.com | 220: DOMAIN-SUFFIX,whatsapp.com,PROXY | 225: DOMAIN-SUFFIX,whatsapp.com,PROXY | PROXY | нет; Domain |
| chatgpt.com | 244: DOMAIN-SUFFIX,chatgpt.com,PROXY | 249: DOMAIN-SUFFIX,chatgpt.com,PROXY | PROXY | нет; Domain |
| openai.com | 245: DOMAIN-SUFFIX,openai.com,PROXY | 250: DOMAIN-SUFFIX,openai.com,PROXY | PROXY | нет; Domain |
| claude.ai | 248: DOMAIN-SUFFIX,claude.ai,PROXY | 253: DOMAIN-SUFFIX,claude.ai,PROXY | PROXY | нет; Domain |
| gemini.google.com | 250: DOMAIN,gemini.google.com,PROXY | 255: DOMAIN,gemini.google.com,PROXY | PROXY | нет; Domain |
| grok.com | 253: DOMAIN-SUFFIX,grok.com,PROXY | 258: DOMAIN-SUFFIX,grok.com,PROXY | PROXY | нет; Domain |
| perplexity.ai | 258: DOMAIN-SUFFIX,perplexity.ai,PROXY | 263: DOMAIN-SUFFIX,perplexity.ai,PROXY | PROXY | нет; Domain |
| youtube.com | 239: RULE-SET,YouTube.list,PROXY | 244: RULE-SET,YouTube.list,PROXY | PROXY | нет; entry 57: DOMAIN-SUFFIX,youtube.com |
| discord.com | 240: RULE-SET,Discord.list,PROXY | 245: RULE-SET,Discord.list,PROXY | PROXY | нет; entry 14: DOMAIN-SUFFIX,discord.com |
| ebay.com | 264: DOMAIN-SUFFIX,ebay.com,PROXY | 269: DOMAIN-SUFFIX,ebay.com,PROXY | PROXY | нет; Domain |
| paypal.com | 267: DOMAIN-SUFFIX,paypal.com,PROXY | 272: DOMAIN-SUFFIX,paypal.com,PROXY | PROXY | нет; Domain |
| bybit.com | 269: DOMAIN-SUFFIX,bybit.com,PROXY | 274: DOMAIN-SUFFIX,bybit.com,PROXY | PROXY | нет; Domain |
| redotpay.com | 195: DOMAIN-SUFFIX,redotpay.com,PROXY | 200: DOMAIN-SUFFIX,redotpay.com,PROXY | PROXY | нет; Domain |
| ads.doubleclick.net | 159: RULE-SET,Advertising.list,REJECT | 164: RULE-SET,Advertising.list,REJECT | REJECT | нет; entry 54: DOMAIN-KEYWORD,doubleclick. |
| cloudflare.com | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| other.fastcdn.pics | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| example.akamaized.net | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| example.cloudfront.net | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| example.fastly.net | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| api.themoviedb.org.example.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| other.api.themoviedb.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| other.image.tmdb.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| image.tmdb.org.example.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| ufc.com.example.org | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| unknown-lampa-audit.example | RU: 285: GEOIP,RU,DIRECT; non-RU: 293: FINAL,PROXY | RU: 290: GEOIP,RU,DIRECT; non-RU: 298: FINAL,PROXY | RU: DIRECT; non-RU: PROXY | нет; IP/GeoIP устройства неизвестны |
| 192.168.1.1 | 26: IP-CIDR,192.168.0.0/16,DIRECT,no-resolve | 26: IP-CIDR,192.168.0.0/16,DIRECT,no-resolve | DIRECT | нет; Literal address |
| 10.1.30.1 | 27: IP-CIDR,10.0.0.0/8,DIRECT,no-resolve | 27: IP-CIDR,10.0.0.0/8,DIRECT,no-resolve | DIRECT | нет; Literal address |
| 172.16.1.1 | 28: IP-CIDR,172.16.0.0/12,DIRECT,no-resolve | 28: IP-CIDR,172.16.0.0/12,DIRECT,no-resolve | DIRECT | нет; Literal address |
| audit.local | 30: DOMAIN-SUFFIX,local,DIRECT | 30: DOMAIN-SUFFIX,local,DIRECT | DIRECT | нет; Domain |
| 224.0.0.251; 239.255.255.250 | 7: tun-excluded-routes 224/4 | 7: tun-excluded-routes 224/4 | обход туннеля | нет; механизм [General] |
