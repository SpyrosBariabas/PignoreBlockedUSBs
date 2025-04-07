# PignoreBlockedUSBs
Bypass USB storage restrictions in Active Directory environments using Raspberry Pi Zero and Samba.
# 🔌USB Bypass using Raspberry Pi (Active Directory Environments)

Hello!
In this guide, we’ll explore a method to bypass a common technique used in Active Directory environments to disable USB ports. Most of the time, this countermeasure focuses on storage devices rather than USB functionality entirely—so I came up with this idea.


⚠️ **Note:** I haven't tested this in a production environment.

# 🛠️Getting Started

Download and install the Raspberry Pi Imager and choose Debian (with or without a Desktop Environment). You don't actually need a DE, but if it makes you more comfortable, go ahead and install the version with it.

#### Make sure to configure your settings here:
![image](https://github.com/user-attachments/assets/3520e067-fe38-4cac-bfdf-ab3a24fa1128)

![image](https://github.com/user-attachments/assets/15cb3adb-e283-4447-9c40-58cd3aa81a69)

![image](https://github.com/user-attachments/assets/f929eef2-d594-478c-ae32-796bc1c0f84a)


Click **Save** and wait for the installation to complete.

If you're setting up your Pi headlessly (no monitor attached), configure the settings now and take note of them—you'll need them for SSH access!
Tip:

I prefer setting up a phone hotspot for the Pi to connect to—it’s convenient, and you can control it via SSH from your phone or a laptop connected to the same hotspot.

# 📦Materials List:

- Raspberry Pi Zero 2 Wh (the "H" just means headers—either version will work since GPIO isn’t needed)
- Micro USB to USB-A Female adapter
- 2x USB to Ethernet adapters (I used TP-Link UE200s)
If your Pi has a LAN port, you only need one adapter.
- Micro USB cable and 5V phone charger
- Ethernet cable
- SD card reader (or microSD to SD adapter)



# 🔩Anatomy Overview

![image](https://github.com/user-attachments/assets/4670838e-15c0-4a44-94be-6d0c700785ea)

![image](https://github.com/user-attachments/assets/bc0e0fa1-3685-434e-99af-72cd5c6c3083)

![image](https://github.com/user-attachments/assets/3a6c7684-c8a8-4ffe-b428-c688d5f8853b)


# ⚙️Setup Instructions (Step-by-Step)

```
ssh poc@poc.local  # Replace 'poc' with your actual username
sudo apt update    # I don't use arch BTW
sudo apt install samba samba-common-bin dnsmasq -y
```
If you installed the Desktop Environment, it's a good idea to enable the VNC server:
```
sudo raspi-config
```
From that menu choose: Interface Options >  I3 VNC > yes > Finish

```
mkdir -p /home/poc/shared    # Replace 'poc' with your user
chmod 777 /home/poc/shared   # Open permissions
sudo smbpasswd -a poc        # Set Samba password
sudo smbpasswd -e poc        # Enable Samba user
```
### 🗂️Configure Samba Share
```
sudo nano /etc/samba/smb.conf
```
Add the following at the bottom of the file:
```plaintext
[Shared]
   path = /home/poc/shared
   browseable = yes
   writable = yes
   valid users = poc
   create mask = 0775
   directory mask = 0775
```
Save and close (Ctrl + X, then Y + Enter). to write changes. (Sorry Vim fans.😅)
```
sudo systemctl restart smbd
```

### 🌐 Configure Network

If you haven’t already, plug in the USB-to-Ethernet adapter and check connections:
```
nmcli con show
```
Look for Wired connection 1. That’s the one we’ll configure.
```plaintext
NAME                UUID                 TYPE      DEVICE
preconfigured       HEX NUMBER (UUID)  wifi      wlan0
lo                  HEX NUMBER (UUID)  loopback  lo
Wired connection 1  HEX NUMBER (UUID)  ethernet  --
```

```
sudo nmcli con modify "Wired connection 1" ipv4.addresses 192.168.16.1/24
sudo nmcli con modify "Wired connection 1" ipv4.method manual
sudo nmcli con modify "Wired connection 1" ipv4.gateway ""
sudo nmcli con up "Wired connection 1"
```

Now verify:
```
ip a show eth0
```
you should get:
```
inet 192.168.16.1/24 ...
```

### 🧠 Configure dnsmasq for DHCP
Open /etc/dnsmasq.conf with ~~Vim~~
```
sudo nano /etc/dnsmasq.conf
```
At the bottom of the file, add:
```plaintext
interface=eth0
bind-interfaces
dhcp-range=192.168.16.2,192.168.16.5,255.255.255.0,12h
```
Ctrl+x and then Y and Enter to write changes.
```
sudo systemctl restart dnsmasq
sudo systemctl enable dnsmasq
```
Run systemctl status to check if it is running

```
sudo systemctl status dnsmasq
```

Yes, your keyboard works—press q to exit.
No, you don’t need to type :q! unless you opened Vim by accident or want to feel powerful.

### 🔌Connect the Target PC

Plug the other end of the Ethernet cable into the target machine.

Use ipconfig on the target to check its IP address. It should be something like 192.168.16.2 to 192.168.16.5.

You can test connectivity::
```
ping 192.168.16.1       # Pi's IP
```

```
ssh poc@192.168.16.1 # Or poc@poc.local
```

To access the Samba share:

    Open File Explorer on the target PC

    Navigate to \\192.168.16.1

    Use the Samba credentials you created earlier


### 🚀 Use Cases

From here, the possibilities are endless:

    Use scp or ssh to transfer files

    Host payloads using Python’s HTTP server

    Add FTP if needed (not covered here)



### 🧪 Future Improvements

- Make the setup more compact
- Use smaller USB-to-Ethernet adapters
- Add 4G module or SIM module (pricey though) for remote C2
- Power the Pi via USB passthrough or LiPo batteries + buck converter
- VPN access for remote control

**📡Bonus Tip:** Use a cronjob and Python script to get your current IP via webhook if using LTE module (no static IP).

##### Cronjob Example

Run every 25 minutes:
```
*/25 * * * * /usr/bin/python3 /home/YOURUSER/.ipgrabber/ip_grab_and_send.py

```

##### Python Script

```python
import requests, json

last_ip_file = "/home/YOURUSER/.ipgrabber/last_ip.txt"

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
    webhook_url = "http://your.webhook.url"  # Replace
    current_ip = get_ip()
    if current_ip and current_ip != get_last_ip():
        send_notification(current_ip, webhook_url)
        save_current_ip(current_ip)

if __name__ == "__main__":
    main()
```

##### 🕵️ Ping Sweep (Optional)

If you want to scan your phone’s hotspot subnet:
Save this as scan.bat and run it on a Windows machine:
```
@echo off
for /L %%i in (1,1,254) do (
	ping -n 1 -w 200 192.168.120.%%i | find "TTL=" > nul
	if not errorlevel 1 (
		echo 192.168.120.%%i is alive. 
	)
) 
```
Note: It's single-threaded, so... grab a snack. 🍕

# 🧪 Testing Notes

I tested this setup on:
- 2 laptops
- 2 desktops
- A basic Active Directory lab (following Practical Ethical Hacking by [TCM Security](https://academy.tcm-sec.com/)) AKA The Cyber Mentor. There is also a free version on youtube this link [Hacking Active Directory for Beginners (over 5 hours of content!)](https://www.youtube.com/watch?v=VXxH4n684HE&list=PLLKT__MCUeixqHJ1TRqrHsEd6_EdEvo47&index=12)

- I applied a GPO that blocks USB storage:

Computer Configuration > Policies > Administrative Templates > System > Removable Storage Access > Deny All Access

# 🙏Special Thanks
#### Huge thanks to the amazing content creators who made this possible:

[TCM Security Academy](https://academy.tcm-sec.com/) AKA [The Cyber Mentor](https://www.youtube.com/@TCMSecurityAcademy) also a youtube channel,
[John Hammond](https://www.youtube.com/@_JohnHammond),
[Hack The Box Academy](https://academy.hackthebox.com/),
[TryHackMe](https://tryhackme.com/)

**This is my first post—I hope it was clear and helpful. Thanks for reading! ✌️**
