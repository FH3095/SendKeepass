#!/usr/bin/env python3

import os,datetime,sys
from configparser import ConfigParser
from datetime import date,timedelta
from smtplib import SMTP
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils

os.chdir(os.path.dirname(os.path.realpath(__file__)))


config=ConfigParser()
config.read_file(open('config.ini'))
config=config['CONFIG']
data=ConfigParser()
data['DATA']={'LastLogin': '2999-01-01'}
data.read('data.ini')


def checkConfig():
    mailTestDay = int(config['EMailTestDay'])
    if mailTestDay < 0 or mailTestDay > 7:
        print('Invalid value for EMailTestDay', mailTestDay)
        sys.exit(1)
    loginInterval = int(config['LoginInterval'])
    if loginInterval < 1 or loginInterval > 1000:
        print('Invalid value for LoginInterval', loginInterval)
        sys.exit(1)


def saveLoggedIn():
    data['DATA']['LastLogin']=date.today().isoformat()
    with open('data.ini', mode='w') as dataFile:
        data.write(dataFile)


def sendMail(to,subject,text,fileNames=[]):
    msg = MIMEText(text)
    if len(fileNames) > 0:
        tmp = MIMEMultipart()
        tmp.attach(msg)
        msg = tmp
    msg['From'] = config['MailServerSender']
    msg['To'] = to
    msg['Subject'] = subject
    msg['Date'] = email.utils.formatdate(localtime=True)
    for fileName in fileNames:
        part = None
        with open(fileName, 'rb') as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(fileName))
        part['Content-Disposition'] = 'attachment; filename="' + os.path.basename(fileName) + '"'
        msg.attach(part)
    with SMTP(host=config['MailServerHost'], port=int(config['MailServerPort'])) as smtp:
        smtp.send_message(msg)


def sendTest():
    todayWeekday = int(date.today().isoweekday())
    sendReminderOnWeekday = int(config['EMailTestDay'])
    if todayWeekday != sendReminderOnWeekday:
        return
    sendMail(config['EMailTestRecipient'], 'SendKeepass Test E-Mail',
             'SendKeepass is still active and E-Mails work, as you can see.')


def sendKeepassFile():
    remindInterval = int(config['RemindInterval'])
    loginInterval = int(config['LoginInterval'])
    today = date.today()
    lastLogin = date.fromisoformat(data['DATA']['LastLogin'])
    remindAfter = lastLogin + timedelta(days=remindInterval)
    sendAfter = lastLogin + timedelta(days=loginInterval)
    if today > remindAfter:
        sendMail(config['EMailRemindRecipient'], 'SendKeepass Login missing', 'You didn\'t logged in for more than ' + str(remindInterval) + ' days. ' +
                 'Your KeepassFile will be sent after ' + str(loginInterval) + ' days without login.')
    if today > sendAfter:
        print('SENDING KEEPASS FILE')
        sendMail(config['EMailNoLoginRecipient'], 'Keepass File', config['EMailNoLoginText'], ['Intermediate.kdbx','KeepassFile.kdbx'])
        saveLoggedIn()


def executeCommand(command):
    if command == 'Send':
        sendTest()
        sendKeepassFile()
    elif command == 'LoggedIn':
        saveLoggedIn()
    else:
        print('Valid parameters', sys.argv[0], '[LoggedIn|Send]')
        sys.exit(1)

    sys.exit(0)



argCommand = sys.argv[1] if len(sys.argv) >= 2 else ''
# For testing
#argCommand='Send'

checkConfig()
executeCommand(argCommand)
