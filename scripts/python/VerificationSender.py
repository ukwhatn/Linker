import time

import mysql.connector as mysql
import wikidot
import socket
from datetime import datetime
import random
import string

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def main():
    logger.info(f"\n[{datetime.now()}] Boot")
    con = mysql.connect(**{
        "host": "localhost" if socket.gethostname() == "ukvps" else "ukwhatn.com",
        "port": "50121",
        "user": "Linker-app",
        "password": "4cLYb4Yr4kgrDftTqgmHtkJF",
        "database": "Linker",
        "charset": "utf8mb4",
        "collation": "utf8mb4_general_ci",
        "autocommit": False
    })

    # データ取得
    with wikidot.Client(user="Linker_App", password="AK4EJ74eoACzr9Njp6JeZA") as client:
        logger.debug(client)
        with con.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM Accounts")
            accounts = cursor.fetchall()
            accounts = {a["DiscordID"]: a for a in accounts}

            cursor.execute("SELECT * FROM LinkRequests WHERE Status IN (0, 11, 12) ORDER BY id")
            requests = cursor.fetchall()

        for request in requests:
            account = accounts[request["DiscordID"]]

            wikidotUser = client.getUser(request["WikidotUserName"])

            if wikidotUser is None:
                # ユーザが存在しない
                # DB反映
                with con.cursor(dictionary=True) as cursor:
                    # Request更新
                    status = 10
                    cursor.execute(
                        "UPDATE LinkRequests SET Status = %s WHERE id = %s",
                        (status, request["id"]))
                con.commit()
            else:
                code = randomname(15)

                subject = "[Linker] 認証コード / Verification Code"
                body = "\n".join([
                    "**[*https://apps.ukwhatn.com/linker/ Linker] 認証コード(verification code):**",
                    f"> @@{code}@@",
                    ""
                ])
                try:
                    # 送信
                    client.createNewMessage(recipient=wikidotUser, subject=subject, body=body).send()
                    status = 1
                    logger.info(
                        f"[{datetime.now()}] Send complete: {wikidotUser.name}({wikidotUser.unixName}/{wikidotUser.id}) => {code}")
                except wikidot.Forbidden:
                    status = 11
                    logger.warning(
                        f"[{datetime.now()}] Permission Error: {wikidotUser.name}({wikidotUser.unixName}/{wikidotUser.id})")
                except Exception as e:
                    status = 12
                    logger.error(
                        f"[{datetime.now()}] Unexpected Error: {wikidotUser.name}({wikidotUser.unixName}/{wikidotUser.id}) => {e}")

                # DB反映
                with con.cursor(dictionary=True) as cursor:
                    # Request更新
                    cursor.execute(
                        "UPDATE LinkRequests SET WikidotID = %s, VerificationCode = %s, Status = %s WHERE id = %s",
                        (wikidotUser.id, code, status, request["id"]))
                    # Account更新
                    cursor.execute(
                        "UPDATE Accounts SET WikidotID = %s, WikidotUserName = %s, WikidotUserUnixName = %s WHERE id = %s",
                        (wikidotUser.id, wikidotUser.name, wikidotUser.unixName, account["id"]))
                con.commit()


while True:
    main()
    time.sleep(500)
