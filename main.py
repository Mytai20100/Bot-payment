import requests
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# === CONFIG ===
VRSC_ADDRESS = "yourverusaddress"
EMAIL_TO = "yourmail@gmail.com"
EMAIL_FROM = "yourmailbot@gmail.com"
EMAIL_PASS = "yourpasswordapp"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CHECK_INTERVAL = 60  # in seconds

# Store seen txids to avoid duplicates
seen_txids = set()

# === HTML Email Template ===
def build_email_html(tx):
    html = f"""
    <div style='font-family: Arial, sans-serif; padding: 20px; background: #f9f9f9;'>
      <div style='max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
        <img src='https://vipor.net/favicon.ico' style='width: 50px;'>
        <h2 style='color: #28a745;'>You have received VRSC!</h2>
        <p><strong>Balance:</strong> +{tx['amount']} VRSC</p>
        <p><strong>TxID:</strong> <a href='https://insight.verus.io/tx/{tx['txid']}'>{tx['txid'][:12]}...</a></p>
        <p><strong>Block Height:</strong> {tx['height']}</p>
        <p><strong>Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>This is an automated message, no reply needed.</p>
        <a href='https://vipor.net/miner/{VRSC_ADDRESS}/verus' style='display: inline-block; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;'>Check</a>
      </div>
    </div>
    """
    return html

# === SEND EMAIL ===
def send_email(subject, html):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

# === MAIN LOOP ===
print("\033[94m[+] VRSC Email Notifier Started...\033[0m")  # Blue for start message
while True:
    try:
        r = requests.get(f"https://insight.verus.io/api/addr/{VRSC_ADDRESS}/utxo")
        if r.status_code == 200:
            utxos = r.json()
            for tx in utxos:
                if tx['txid'] not in seen_txids:
                    html = build_email_html(tx)
                    send_email(f"[VRSC] You have received VRSC +{tx['amount']} VRSC", html)
                    print(f"\033[92m[✓] Sent notification for TXID: {tx['txid']}\033[0m")  # Green for success
                    seen_txids.add(tx['txid'])
        else:
            print("\033[91m[!] Failed to fetch UTXO\033[0m")  # Red for failure
    except Exception as e:
        print(f"\033[91m[!] Error: {e}\033[0m")  # Red for errors
    time.sleep(CHECK_INTERVAL)
