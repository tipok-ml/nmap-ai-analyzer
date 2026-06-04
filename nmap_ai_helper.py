#!/usr/bin/env python3
"""
nmap_ai_helper.py – запуск nmap, парсинг результатов и AI-анализ через DeepSeek API.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import requests
from colorama import Fore, Style, init

init(autoreset=True)

# ------------------------- Конфигурация -------------------------
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
CACHE_DIR = os.path.expanduser("~/.cache/nmap_ai_helper")
DEFAULT_CACHE_TTL = 86400  # 24 часа

# ------------------------- Вспомогательные функции -------------------------
def get_deepseek_api_key() -> Optional[str]:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key
    print(f"{Fore.YELLOW}⚠️ Переменная окружения DEEPSEEK_API_KEY не установлена.{Style.RESET_ALL}")
    print("Вы можете ввести ключ вручную (будет сохранён только для текущего сеанса):")
    return input("API-ключ: ").strip()

def validate_api_key(api_key: str) -> bool:
    try:
        resp = requests.get(
            f"{DEEPSEEK_API_BASE}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False

def get_cache_path(cache_key: str) -> str:
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, cache_key)

def load_cache(cache_key: str, ttl: int) -> Optional[str]:
    path = get_cache_path(cache_key)
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        if time.time() - mtime < ttl:
            with open(path, "r") as f:
                return f.read()
    return None

def save_cache(cache_key: str, data: str) -> None:
    path = get_cache_path(cache_key)
    with open(path, "w") as f:
        f.write(data)

def generate_cache_key(target: str, extra_args: str) -> str:
    raw = f"nmap -sV -T4 {extra_args} {target}"
    return hashlib.sha256(raw.encode()).hexdigest()

# ------------------------- Работа с nmap -------------------------
def run_nmap(target: str, extra_args: str, use_cache: bool, cache_ttl: int) -> str:
    cache_key = generate_cache_key(target, extra_args) if use_cache else None
    if use_cache:
        cached = load_cache(cache_key, cache_ttl)
        if cached:
            print(f"{Fore.YELLOW}📦 Использую кэшированный результат (до {cache_ttl//3600} ч).{Style.RESET_ALL}")
            return cached

    cmd = ["nmap", "-sV", "-T4", "-oX", "-"] + (extra_args.split() if extra_args else []) + [target]
    print(f"{Fore.GREEN}🔍 Запуск nmap:{Style.RESET_ALL} {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        sys.exit(f"{Fore.RED}❌ nmap не найден. Установите его (apt install nmap).{Style.RESET_ALL}")
    except subprocess.TimeoutExpired:
        sys.exit(f"{Fore.RED}❌ Превышено время ожидания (10 мин).{Style.RESET_ALL}")

    if result.returncode != 0:
        print(f"{Fore.RED}❌ Ошибка nmap (код {result.returncode}):{Style.RESET_ALL}")
        print(result.stderr)
        sys.exit(1)

    if use_cache:
        save_cache(cache_key, result.stdout)
    return result.stdout

def parse_nmap_xml(xml_content: str) -> Dict:
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return {"error": f"Ошибка парсинга XML: {e}"}

    host_el = root.find(".//host")
    if host_el is None:
        return {"error": "Хост не найден в XML"}

    addr_el = host_el.find(".//address[@addrtype='ipv4']")
    scan_info = {
        "target": addr_el.get("addr") if addr_el is not None else "unknown",
        "hostname": (host_el.find(".//hostnames/hostname") or {}).get("name", ""),
        "os": (host_el.find(".//os/osmatch") or {}).get("name", "Не определена"),
        "ports": [],
        "tcp_ports": [],
        "udp_ports": [],
        "scripts": [],
        "vulnerabilities": []
    }

    for port_el in root.findall(".//port"):
        port_id = port_el.get("portid")
        protocol = port_el.get("protocol")
        state_el = port_el.find("state")
        state = state_el.get("state") if state_el is not None else "unknown"
        service_el = port_el.find("service")
        service_name = service_el.get("name") if service_el is not None else "unknown"
        product = service_el.get("product") if service_el is not None else ""
        version = service_el.get("version") if service_el is not None else ""
        full_version = f"{product} {version}".strip()
        port_info = {
            "port": port_id,
            "protocol": protocol,
            "state": state,
            "service": service_name,
            "version": full_version
        }
        scan_info["ports"].append(port_info)
        if protocol == "tcp":
            scan_info["tcp_ports"].append(port_info)
        elif protocol == "udp":
            scan_info["udp_ports"].append(port_info)

    for script_el in root.findall(".//script"):
        script_id = script_el.get("id")
        output = script_el.get("output", "")
        scan_info["scripts"].append({"id": script_id, "output": output[:300]})
        cves = re.findall(r'CVE-\d{4}-\d{4,}', output)
        if cves:
            scan_info["vulnerabilities"].append({
                "script": script_id,
                "cves": cves,
                "summary": output[:300]
            })

    return scan_info

def build_prompt(scan_data: Dict) -> str:
    lines = []
    lines.append(f"Цель: {scan_data['target']}")
    if scan_data.get("hostname"):
        lines.append(f"Хост: {scan_data['hostname']}")
    lines.append(f"ОС: {scan_data['os']}")

    open_ports = [p for p in scan_data["ports"] if p["state"] == "open"]
    if open_ports:
        lines.append("\nОткрытые порты:")
        for p in open_ports:
            lines.append(f"  {p['protocol']}/{p['port']} : {p['service']} {p['version']}")
    else:
        lines.append("Открытых портов не обнаружено.")

    if scan_data.get("vulnerabilities"):
        lines.append("\nОбнаруженные CVE (через NSE-скрипты):")
        for vuln in scan_data["vulnerabilities"]:
            lines.append(f"  - {vuln['script']}: {', '.join(vuln['cves'])}")
            lines.append(f"    {vuln['summary'][:200]}")

    lines.append("\nПроанализируй результаты сканирования nmap. Укажи, какие сервисы потенциально уязвимы, какие настройки можно улучшить, и дай конкретные рекомендации по повышению безопасности. Ответь структурированно: краткий вывод, затем детали и рекомендации.")
    return "\n".join(lines)

def query_deepseek(prompt: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    try:
        resp = requests.post(
            f"{DEEPSEEK_API_BASE}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа")
    except requests.exceptions.RequestException as e:
        return f"Ошибка API: {e}"

# ------------------------- Главная функция -------------------------
def main():
    parser = argparse.ArgumentParser(description="nmap + AI анализ через DeepSeek")
    parser.add_argument("target", nargs="?", help="Цель сканирования (IP, хост, сеть)")
    parser.add_argument("--nmap-args", default="", help="Доп. аргументы nmap (в кавычках)")
    parser.add_argument("--xml-file", help="Готовый XML-файл (вместо сканирования)")
    parser.add_argument("--no-ai", action="store_true", help="Пропустить AI-анализ")
    parser.add_argument("--json", nargs="?", const="stdout", help="Сохранить результат в JSON (файл или stdout)")
    parser.add_argument("--no-cache", action="store_true", help="Отключить кэш")
    parser.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL, help="Время жизни кэша в секундах")
    args = parser.parse_args()

    if not args.xml_file and not args.target:
        parser.print_help()
        sys.exit("❌ Укажите цель или --xml-file")

    if args.xml_file:
        if not os.path.isfile(args.xml_file):
            sys.exit(f"❌ Файл {args.xml_file} не найден.")
        with open(args.xml_file, "r") as f:
            xml_content = f.read()
        print(f"{Fore.CYAN}📂 Загружен XML из {args.xml_file}{Style.RESET_ALL}")
    else:
        xml_content = run_nmap(args.target, args.nmap_args, not args.no_cache, args.cache_ttl)

    print(f"{Fore.CYAN}🔄 Парсинг XML...{Style.RESET_ALL}")
    scan_data = parse_nmap_xml(xml_content)
    if "error" in scan_data:
        sys.exit(f"{Fore.RED}❌ {scan_data['error']}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}📋 Результаты сканирования:{Style.RESET_ALL}")
    print(f"  Хост: {scan_data['target']}  (ОС: {scan_data['os']})")
    open_ports = [p for p in scan_data["ports"] if p["state"] == "open"]
    print(f"  Открыто портов: {len(open_ports)}")
    for p in open_ports:
        print(f"    {p['protocol']}/{p['port']}  {p['service']} {p['version']}")

    ai_response = None
    if not args.no_ai:
        api_key = get_deepseek_api_key()
        if not api_key:
            sys.exit(f"{Fore.RED}❌ Не удалось получить API-ключ.{Style.RESET_ALL}")
        if not validate_api_key(api_key):
            sys.exit(f"{Fore.RED}❌ Неверный API-ключ или сетевая проблема.{Style.RESET_ALL}")

        prompt = build_prompt(scan_data)
        print(f"{Fore.GREEN}🤖 Запрос к DeepSeek...{Style.RESET_ALL}")
        ai_response = query_deepseek(prompt, api_key)
        print(f"\n{Fore.MAGENTA}💡 Анализ и рекомендации DeepSeek:{Style.RESET_ALL}")
        print("=" * 60)
        print(ai_response)
        print("=" * 60)

    if args.json:
        output = {
            "scan_data": scan_data,
            "ai_analysis": ai_response if ai_response else None
        }
        if args.json == "stdout":
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            with open(args.json, "w") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"{Fore.GREEN}✅ Результаты сохранены в {args.json}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
