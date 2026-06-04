# nmap-ai-analyzer
    Примечание: Для других дистрибутивов используйте соответствующий менеджер пакетов (pacman, dnf, brew). Скрипт также работает с pip install requests colorama, но на Ubuntu 24.04+ рекомендуется использовать системные пакеты.

🚀 Использование
Базовое сканирование (без AI)
bash

python3 nmap_ai_helper.py scanme.nmap.org --no-ai

Полный анализ с AI
bash

export DEEPSEEK_API_KEY="ваш_ключ"
python3 nmap_ai_helper.py scanme.nmap.org

С дополнительными аргументами nmap
bash

python3 nmap_ai_helper.py 192.168.1.1 --nmap-args "-sS -p 1-1000"

Использование готового XML-файла
bash

python3 nmap_ai_helper.py --xml-file result.xml

Сохранение результата в JSON
bash

python3 nmap_ai_helper.py scanme.nmap.org --json report.json

Отключение кэша
bash

python3 nmap_ai_helper.py scanme.nmap.org --no-cache

📊 Пример вывода
text

🔍 Запуск nmap: nmap -sV -T4 -oX - scanme.nmap.org
🔄 Парсинг XML...

📋 Результаты сканирования:
  Хост: 45.33.32.156  (ОС: Не определена)
  Открыто портов: 4
    tcp/22  ssh OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13
    tcp/80  http Apache httpd 2.4.7
    tcp/9929  nping-echo Nping echo None
    tcp/31337  tcpwrapped None None

🤖 Запрос к DeepSeek...

💡 Анализ и рекомендации DeepSeek:
============================================================
Краткий вывод: Целевая система (45.33.32.156) имеет несколько открытых портов, включая потенциально опасные нестандартные сервисы...
[подробный анализ]
============================================================

🖼️ Скриншоты

    Здесь вы можете добавить скриншоты работы скрипта.
    Например: терминал с результатами сканирования и AI-анализом.

🛠️ Аргументы командной строки
Аргумент	Описание
target	Цель сканирования (IP, хост, сеть)
--nmap-args	Дополнительные аргументы для nmap (в кавычках)
--xml-file	Путь к готовому XML-файлу nmap (вместо сканирования)
--no-ai	Пропустить AI-анализ (только вывод nmap)
--json [FILE]	Сохранить результат в JSON (если без FILE – в stdout)
--no-cache	Отключить кэширование
--cache-ttl	Время жизни кэша в секундах (по умолчанию 86400)
📦 Кэширование

Скрипт сохраняет результаты сканирования в ~/.cache/nmap_ai_helper/. При повторном запуске с теми же аргументами используется кэш (24 часа). Это ускоряет работу при отладке промптов.
🤝 Как внести вклад

    Форкните репозиторий.

    Создайте ветку для вашего изменения (git checkout -b feature/amazing-feature).

    Закоммитьте изменения (git commit -m 'Add amazing feature').

    Запушьте в ветку (git push origin feature/amazing-feature).

    Откройте Pull Request.

📄 Лицензия

Распространяется под лицензией MIT. Подробности в файле LICENSE.
👤 Автор

tipok-ml – GitHub
🙏 Благодарности

    nmap – за мощный сканер безопасности.

    DeepSeek – за доступ к API и анализ уязвимостей.

⭐️ Если вам помог этот проект, поставьте звезду на GitHub!
