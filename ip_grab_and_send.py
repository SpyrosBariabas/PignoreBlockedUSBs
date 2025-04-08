import requests, json

last_ip_file = "/home/YOURUSER/.ipgrabber/last_ip.txt" # Replace 'YOURUSER' with your actual username

def get_ip():
    try:
        return requests.get("https://ipinfo.io").json().get("ip")
    except requests.RequestException:
        return None

def send_notification(ip, webhook_url):
    data = {"content": f"Your public IP address is: {ip}"}
    r = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    print("Sent!" if r.status_code == 204 else f"Error: {r.status_code}")

def get_last_ip():
    try:
        with open(last_ip_file) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_current_ip(ip):
    with open(last_ip_file, "w") as f:
        f.write(ip)

def main():
    webhook_url = "http://your.webhook.url"  # Replace with your webhook url
    current_ip = get_ip()
    if current_ip and current_ip != get_last_ip():
        send_notification(current_ip, webhook_url)
        save_current_ip(current_ip)

if __name__ == "__main__":
    main()
