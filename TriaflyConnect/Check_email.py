import Triafly_API_loadfact
import datetime
import imaplib
import os
import email
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import re

mail_pass = "qsrjenykhjlempbg"
username = "askuetestoviy@yandex.ru"
imap_server = "imap.yandex.ru"
imap = imaplib.IMAP4_SSL(imap_server)
imap.login(username, mail_pass)
imap.select("INBOX")
print('Проверка почты')
unread_letters_obj = imap.uid('search', "UNSEEN", "ALL")

unread_letters_uids_bytes = unread_letters_obj[1][0]
print(unread_letters_uids_bytes)
unread_letters_uids_str = str(unread_letters_uids_bytes, 'utf-8')
print(unread_letters_uids_str)
unread_letters_uids_list = unread_letters_uids_str.split(' ')
print(unread_letters_uids_list)
detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
    os.mkdir('attachments')
for letter in unread_letters_uids_list:
    if letter == '': continue
    res, msg = imap.uid('fetch', letter.encode(), '(RFC822)')

    msg = email.message_from_bytes(msg[0][1])

    letter_date = email.utils.parsedate_tz(msg["Date"]) # дата получения, приходит в виде строки, дальше надо её парсить в формат datetime
    letter_id = msg["Message-ID"] #айди письма
    letter_from = msg["Return-path"] # e-mail отправителя
    subject_rus = decode_header(msg["Subject"])[0][0].decode()
    print(letter_id, letter_from, subject_rus)

    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            fileName = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S.%f_")+decode_header(part.get_filename())[0][0].decode()
            print(fileName)
            if bool(fileName):
                filePath = os.path.join(detach_dir, 'attachments', fileName)
                #os.remove(filePath)
                if not os.path.isfile(filePath):
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    print('Скачали вложение. запускаем загрузку в триафлай')
                    Triafly_API_loadfact._load_excel_toTriafly(filePath)