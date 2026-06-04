# nmap-ai-analyzer

```markdown
# 🔍 nmap-ai-analyzer

[Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[GitHub stars](https://img.shields.io/github/stars/tipok-ml/nmap-ai-analyzer?style=social)](https://github.com/tipok-ml/nmap-ai-analyzer/stargazers)

**Автоматизированный анализ безопасности сетей с помощью nmap и DeepSeek AI**

`nmap-ai-analyzer` — это мощный инструмент командной строки, который запускает сканирование `nmap`, извлекает из его XML‑вывода всю ключевую информацию (открытые порты, сервисы, версии, ОС, результаты NSE‑скриптов) и отправляет эти данные в **DeepSeek API** для интеллектуального анализа уязвимостей и получения чётких, структурированных рекомендаций по повышению безопасности.

> 🚀 **Идеальный помощник для пентестеров, администраторов безопасности и всех, кто хочет быстро оценить уязвимости своей сети.**

---

## 📦 Возможности

- ✅ **Полная интеграция с nmap** – поддерживает любые аргументы `nmap` (`-sS`, `-p`, `--script`, и т.д.).
- ✅ **Умный парсинг** – извлекает IP, хост, ОС, открытые порты (TCP/UDP), версии сервисов, а также вывод NSE‑скриптов.
- ✅ **Обнаружение CVE** – автоматически находит упоминания CVE в выводах скриптов (например, `vuln`).
- ✅ **Кэширование** – сохраняет результаты сканирования в `~/.cache/nmap_ai_helper/` и при повторном запуске использует кэш (по умолчанию 24 часа). Ускоряет отладку и повторные анализы.
- ✅ **Гибкий вывод** – цветной консольный вывод, поддержка экспорта в JSON (флаг `--json`).
- ✅ **Проверка API‑ключа** – перед сканированием проверяет валидность ключа DeepSeek, чтобы не тратить время зря.
- ✅ **Работа с готовыми XML‑файлами** – если у вас уже есть вывод `nmap -oX`, можно передать его напрямую.

---

## 📋 Требования

- **Python** 3.8 или выше
- **nmap** (установлен в системе)
- **API‑ключ DeepSeek** – получить бесплатно на [platform.deepseek.com](https://platform.deepseek.com/)

---

## 🚀 Установка и запуск

### 1️⃣ Клонируйте репозиторий
```bash
git clone https://github.com/tipok-ml/nmap-ai-analyzer.git
cd nmap-ai-analyzer
```

### 2️⃣ Установите зависимости (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install nmap python3-requests python3-colorama -y
```

> Для других дистрибутивов используйте соответствующий менеджер пакетов (`pacman`, `dnf`, `brew`). Либо установите `requests` и `colorama` через `pip install --user requests colorama`.

### 3️⃣ Запустите первое сканирование (без AI)
```bash
python3 nmap_ai_helper.py scanme.nmap.org --no-ai
```
Вы увидите таблицу с открытыми портами и сервисами.

### 4️⃣ Полный анализ с AI
```bash
export DEEPSEEK_API_KEY="ваш_ключ"
python3 nmap_ai_helper.py scanme.nmap.org
```

---

## 🛠️ Примеры использования

| Команда | Описание |
|--------|----------|
| `python3 nmap_ai_helper.py 192.168.1.1 --nmap-args "-sS -p 1-1000"` | Сканирование с дополнительными аргументами `nmap`. |
| `python3 nmap_ai_helper.py --xml-file result.xml` | Анализ готового XML‑файла без повторного сканирования. |
| `python3 nmap_ai_helper.py scanme.nmap.org --json report.json` | Сохранить результат (включая AI‑анализ) в JSON. |
| `python3 nmap_ai_helper.py scanme.nmap.org --no-cache` | Отключить кэширование (принудительное сканирование). |

---

## 📊 Пример вывода

```text
🔍 Запуск nmap: nmap -sV -T4 -oX - scanme.nmap.org
🔄 Парсинг XML...

📋 Результаты сканирования:
  Хост: 45.33.32.156  (ОС: Не определена)
  Открыто портов: 4
    tcp/22   ssh    OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13
    tcp/80   http   Apache httpd 2.4.7
    tcp/9929 nping-echo Nping echo None
    tcp/31337 tcpwrapped None None

🤖 Запрос к DeepSeek...
💡 Анализ и рекомендации DeepSeek:
============================================================
Краткий вывод: Целевая система имеет устаревшие версии OpenSSH и Apache, а также два нестандартных сервиса. Наиболее критично – OpenSSH 6.6.1p1, содержащий известные CVE (CVE-2016-6210, CVE-2015-5600). ...
```

> ℹ️ Полный вывод AI‑анализа занимает несколько экранов и содержит детальные рекомендации по каждому сервису.

---

## 🖼️ Скриншоты

Пример без AI <img width="1854" height="1048" alt="Снимок экрана от 2026-06-04 16-00-56" src="https://github.com/user-attachments/assets/4145d0d8-f580-4670-806a-78844cda7ff3" />


Пример с AI <img width="1854" height="1048" alt="Снимок экрана от 2026-06-04 15-18-46" src="https://github.com/user-attachments/assets/184bf9e8-36cd-49b0-bd65-e3f32c29080e" />
<img width="1854" height="1048" alt="Снимок экрана от 2026-06-04 15-18-52" src="https://github.com/user-attachments/assets/76857cfe-dd1b-484c-a34e-44adf02107ea" />
<img width="1854" height="1048" alt="Снимок экрана от 2026-06-04 15-18-58" src="https://github.com/user-attachments/assets/96fb47ae-e63d-4049-8d06-0c83f2bc6631" />
<img width="1854" height="1048" alt="Снимок экрана от 2026-06-04 15-19-02" src="https://github.com/user-attachments/assets/a52c749b-ac70-4f15-88ff-f602baa1cef7" />
```


 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности – в файле [LICENSE](LICENSE).


 👤 Автор

tipok-ml  
[GitHub](https://github.com/tipok-ml)

Если вам понравился проект, поставьте ⭐️ – это очень поможет в развитии!
