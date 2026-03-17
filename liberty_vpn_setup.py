"""
Настройка Liberty VPN для JARVIS
"""
import os
import sys

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("Настройка Liberty VPN для JARVIS")
print("=" * 40)

print("1. Скачайте и установите Liberty VPN клиент")
print("2. Откройте приложение и войдите в аккаунт")
print("3. Подключитесь к любому серверу")
print("4. В настройках Liberty VPN найдите 'Local Proxy' или 'SOCKS Proxy'")
print("5. Включите локальный прокси на порту 1080")
print("6. Убедитесь что Spotify работает через VPN")
print("7. Запустите бота: python jarvis\\bot.py")

print("\nЕсли порт 1080 не работает, попробуйте:")
print("- 1087")
print("- 7890") 
print("- 8080")

print("\nПроверка прокси:")
try:
    import requests
    response = requests.get('http://ipinfo.io/json', proxies={
        'http': 'http://127.0.0.1:1080',
        'https': 'http://127.0.0.1:1080'
    }, timeout=5)
    if response.status_code == 200:
        ip_info = response.json()
        print(f"✅ Прокси работает! IP: {ip_info.get('ip')}")
        print(f"Страна: {ip_info.get('country')}")
    else:
        print("❌ Прокси не отвечает")
except Exception as e:
    print(f"❌ Ошибка прокси: {e}")

print("\nГотово! Теперь бот должен работать через Liberty VPN")
