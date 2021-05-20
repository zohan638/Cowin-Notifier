import requests
import json
import sys
import datetime
import pytz
import time
import smtplib
import numpy as np

from ipaddress import IPv4Address  # for your IP address
from pyairmore.request import AirmoreSession  # to create an AirmoreSession
from pyairmore.services.messaging import MessagingService  # to send messages

d = {}

with open("params.txt") as f:
    for line in f:
        (key, val) = line.split()
        d[key] = val

try:
    ip = IPv4Address(d['ipadress'])  # let's create an IP address object
    session = AirmoreSession(ip)
    if session.is_server_running:
        print(session.request_authorization())
except:
    print('Phone not available - SMS NOT WORKING!')

print("Do you want:")
print("1. SMS alert.")
print("2. Email alert.")
print("3. Both.")
prompt = '> '
phone = None
mail = None
choice = input(prompt)
if choice == str(1):
    print("Enter Mobile Number:")
    phone = input(prompt)
if choice == str(2):
    print("Enter Email-ID:")
    mail = input(prompt)
if choice == str(3):
    print("Enter Mobile Number:")
    phone = input(prompt)
    print("Enter Email-ID:")
    mail = str(input(prompt))

gmail_user = d['gmail_user']
gmail_password = d['gmail_password']

sent_from = gmail_user
to = [mail]

print("Enter the name of state:")
sname = str(input(prompt))
print("Enter the name of district:")
dname = str(input(prompt))
sid, did = None, None

current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
day = current_time.day
month = current_time.month
year = current_time.year
print("Today's date is: " + str(day) + '/' + str(month) + '/' + str(year))

current_time += datetime.timedelta(days = int(d['period']))
day = current_time.day
month = current_time.month
year = current_time.year
print("Checking availability for: " + str(day) + '/' + str(month) + '/' + str(year))

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'accept': 'application/json',
    'Accept-Language': 'hi_IN',
}

r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states', headers=headers)
data = json.loads(r.text)

for i in data['states']:
    if sname.lower() in i['state_name'].lower():
        sid = i['state_id']

r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/districts/' + str(sid), headers=headers)
data = json.loads(r.text)

for i in data['districts']:
    if dname.lower() in i['district_name'].lower():
        did = i['district_id']

if (did == None or sid == None):
    print("District or State name INVALID.")
    sys.exit()

params = (
    ('district_id', str(did)),
    ('date', str(day) + '-' + str(month) + '-' + str(year) + '-'),
)

centerid_old = []
while True:
    r = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict', headers=headers, params=params)
    data = json.loads(r.text)

    if data['sessions']:
        message = ""
        centerid_new = []
        for i in data['sessions']:
            centerid_new.append(str(i['center_id']))
            if str(i['center_id']) not in centerid_old:
                # print(str(i['center_id']) + '\n' + str(i['name']) + '\n' + str(i['pincode']) + '\n' + str(i['vaccine']) + '\n' + str(i['date']))
                message += f"""{i['name']}
{i['pincode']}
{i['vaccine']}
{i['date']}
{i['min_age_limit']}+

"""     
        print(f"{centerid_new} , {centerid_old}")
        if not np.array_equal(np.sort(np.array(centerid_new)), np.sort(np.array(centerid_old))):
            if phone != None:
                try:
                    service = MessagingService(session)
                    service.send_message(str(phone), str(message))
                except:
                    print('SMS ERROR!')

            if mail != None:
                if message == "":
                    message = "Some of the Vaccine slots are filled!! Hurry up!!!"
                subject = 'Cowin Vaccine available'
                body = message
                email_text = "Subject: " + str(subject) + "\n" + str(body)
                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_password)
                    server.sendmail(sent_from, to, email_text)
                    server.close()

                    print('Email sent!')
                except:
                    print('Email ERROR!')
            print(message)
        centerid_old = list.copy(centerid_new)
    time.sleep(int(d['speed']))