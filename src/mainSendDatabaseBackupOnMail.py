import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from src.connections import config

DB_NAME = "tech-support"
MAIL_RECIPIENT = config["mail_address"]
MAIL_HTML = """<html>
  <head></head>
  <body>
    <h1>Ура, новый бэкап!</h1>
  </body>
</html>"""
PG_DUMP_FILENAME = f"{datetime.now().strftime('%A')}.sql.backup"
PG_DUMP_FULLPATH = f"/pg_backups/{PG_DUMP_FILENAME}"
MAKE_BACKUP_CMD = f"pg_dump -F c -b -U \"backups\" tech-support > {PG_DUMP_FULLPATH}"

if __name__ == '__main__':
    os.system(MAKE_BACKUP_CMD)  # make backup

    WEEKDAY = datetime.today().strftime('%A')
    TIMESTAMP = datetime.today().strftime('%Y%m%d%H%M%S')
    MAIL_FILE_NAME = f"backup_{WEEKDAY}_{TIMESTAMP}.sql.backup"

    msg = MIMEMultipart()
    msg['Subject'] = f"{WEEKDAY}(GMT) Backup of {DB_NAME}"
    msg['From'] = config["mail_sender_name"]
    msg['To'] = MAIL_RECIPIENT
    msg.attach(MIMEText(MAIL_HTML, 'html'))
    with open(PG_DUMP_FULLPATH, "rb") as f:
        part = MIMEApplication(
            f.read(),
            Name=MAIL_FILE_NAME
        )
    # After the file is closed
    part['Content-Disposition'] = f'attachment; filename="{MAIL_FILE_NAME}"'
    msg.attach(part)

    server = smtplib.SMTP(host=config["SMTP_mail_server_host"], port=config["SMTP_mail_server_port"])
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(config["mail_address"], config["mail_password"])
    server.send_message(msg)
    server.quit()
    print('Successfully sent the mail!')
