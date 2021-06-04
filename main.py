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

print("Do you want receive:")
print("1. SMS alert.")
print("2. Email alert.")
print("3. Both.")
print("4. No alerts just log in console.")
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
if choice == str(4):
    pass

gmail_user = d['gmail_user']
gmail_password = d['gmail_password']

sent_from = gmail_user
to = [mail]

current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
day = current_time.day
month = current_time.month
year = current_time.year
print("\nToday's date is: " + str(day) + '/' + str(month) + '/' + str(year))

current_time += datetime.timedelta(days = int(d['period']))
day = current_time.day
month = current_time.month
year = current_time.year
print("Checking availability for: " + str(day) + '/' + str(month) + '/' + str(year) + "\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'accept': 'application/json',
    'Accept-Language': 'hi_IN',
}

r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states', headers=headers)
data = json.loads(r.text)

sid, did = None, None

while True:
    sname = {}
    print("Enter the name of state:")
    name = str(input(prompt))

    for i in data['states']:
        if name.lower() in i['state_name'].lower():
            sname[i['state_name']] = i['state_id']

    if len(sname.keys()) == 1:
        for i in sname.keys():
            sid = sname[i]
            sname = i
        print("State Name: " + sname)
        break
    
    elif len(sname.keys()) > 1:
        print("Do you mean:", end=" ")

        for j, i in enumerate(sname.keys()):
            if j < len(sname.keys()) - 1:
                print(i + " /", end=" ")
            
            else:
                print(i + "?")

    else:
        print("Wrong State Name Chosen!")

r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/districts/' + str(sid), headers=headers)
data = json.loads(r.text)

while True:
    dname = {}

    print("Enter the name of district:")
    name = str(input(prompt))

    for i in data['districts']:
        if name.lower() in i['district_name'].lower():
            dname[i['district_name']] = i['district_id']

    if len(dname.keys()) == 1:
        for i in dname.keys():
            did = dname[i]
            dname = i
        print("District Name: " + dname)
        break
    
    elif len(dname.keys()) > 1:
        print("Do you mean:", end=" ")

        for j, i in enumerate(dname.keys()):
            if j < len(dname.keys()) - 1:
                print(i + " /", end=" ")
            
            else:
                print(i + "?")

    else:
        print("Wrong District Name Chosen!")

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
            if i['available_capacity'] != 0:
                centerid_new.append(str(i['center_id']))
            if str(i['center_id']) not in centerid_old and i['available_capacity'] != 0:
                # print(str(i['center_id']) + '\n' + str(i['name']) + '\n' + str(i['pincode']) + '\n' + str(i['vaccine']) + '\n' + str(i['date']))
                message += f"""{i['name']}
{i['pincode']}
{i['vaccine']}
{i['date']}
{i['min_age_limit']}+
Dose 1: {i['available_capacity_dose1']}
Dose 2: {i['available_capacity_dose2']}
Total: {i['available_capacity']}"""
            if i['fee_type'] == 'Paid':
                message += f"""
{i['fee_type']}: INR{i['fee']}""" 

            message += """

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