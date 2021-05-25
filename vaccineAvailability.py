import datetime
import json
import smtplib
import time
from collections import defaultdict
from copy import deepcopy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from traceback import format_exc

import requests

with open('cred.json', 'r') as cred_file:
    cred = json.load(cred_file)
sender = cred["sender"]
auth = cred["auth"]
session = smtplib.SMTP('smtp.gmail.com', 587)

bot_token = '1865743998:AAFudOPsyhuqvuoraRC38M3tJ4T0aKF_2dc'

def notify(user, validSlots):
    if 'notifyOn' in user and user.get('notifyOn') == 'telegram':
        notifyUserViaTelegram(user, validSlots)
    else:
        notifyUserViaEmail(user.get('email'), validSlots)


def notifyUserViaTelegram(user, validSlots):
    chat_id = user.get('email')
    name = user.get('name')
    bot_message = f"Hi {name}, \nYou can select dose type as well \nVaccine available at {len(validSlots)} places, \none place is \n" + json.dumps(validSlots[0], indent=1)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&text=' + bot_message
    # send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&text=' + "hello"
    response = requests.get(send_text)
    # print(response.json())

def notifyUserViaEmail(email, validSlots):
    mail_content = json.dumps(validSlots, indent=1)
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = email
    message['Subject'] = 'Vaccine slots availablity | Please unsubscribe once you get the slots'
    message.attach(MIMEText(mail_content, 'plain'))
    message.attach(MIMEText(u'<a href="https://vickxy.github.io/vaccine-availability-covid19/">https://vickxy.github.io/vaccine-availability-covid19/</a>','html'))

    try:
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender, auth)
        text = message.as_string()
        session.sendmail(sender, email, text)
        session.quit()
    except Exception as e:
        print("Error: unable to send email")
        print(format_exc())


def getSlots(mode, dist_id, pin, date):
    time.sleep(5)

    if mode == 1:
        print(f"Fetching data for pincode {pin}")
        url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=' + pin + '&date=' + date
    else:
        print(f"Fetching data for dist_id {dist_id}")
        url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=' + dist_id + '&date=' + date
    res = requests.get(
        url=url,
        headers={
            'accept': 'application/json',
            'Accept-Language': 'hi_IN',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'X-Forwarded-For': '122.171.172.178'
        },
    )
    validSlots = []
    # print(res.json)
    try:
        if not "centers" in res.json():
            return validSlots
    except:
        print(res)
        return validSlots
    result = res.json()["centers"]
    for res in result:
        data = {}
        data['name'] = res['name']
        data['district_name'] = res['district_name']
        data['block_name'] = res['block_name']
        data['pincode'] = res['pincode']
        data['sessions'] = []
        for re in res['sessions']:
            if re['available_capacity'] >= 1:
                data['sessions'].append(re)
                validSlots.append(data)
    return validSlots


def checkVaccineAvailibility(mode, dist_id, pin, users):
    date = datetime.datetime.today().strftime('%d-%m-%Y')
    full_data = getSlots(mode, dist_id, pin, date)
    if not full_data:
        print(f"No slots available for district {dist_id} and pin {pin}")
        return
    print(f"Vaccine found at {len(full_data)} places")

    # Check for all the users
    for user in users:
        try:
            user_age = user.get('age')
            dose_type = user.get('dose') if 'dose' in user else "available_capacity";
            filtered_data = []
            for data in full_data:
                valid_session = []
                for session in data.get('sessions', []):
                    if int(session['min_age_limit']) <= user_age and session[dose_type] >= 1:
                        if 'vaccine' in user:
                            if user.get('vaccine').lower() == session.get('vaccine').lower():
                                valid_session.append(session)
                        else:
                            valid_session.append(session)
                if valid_session:
                    data_copy = deepcopy(data)
                    data_copy['sessions'] = valid_session
                    filtered_data.append(data_copy)

            if not filtered_data:
                continue
            print(
                f"User with age {user_age} vaccine is available at {len(filtered_data)} places and notifying to {user['email']}")
            # print(filtered_data)
            notify(user, filtered_data)
        except Exception as e:
            print(f"error for user {user.get('name')}:  {e}")


def main(user_data):
    print("fetching details...")
    try:
        region_user = defaultdict(lambda: [])
        for i in user_data['users']:
            pin = '560068'
            dist_id = 294
            mode = i['mode']
            if mode ==1:
                pin =i['pincode']
            else:
                if 'dist_id' not in i:
                    continue
                dist_id = i['dist_id']
            region_user[(mode, dist_id, pin)].append(i)

        for region, users in region_user.items():
            mode, dist_id, pin = region
            checkVaccineAvailibility(mode, dist_id, pin, users)
    except Exception as e:
        print("Error ")
        print(format_exc())


if __name__ == "__main__":
    while (True):
        with open('data.json', 'r') as f:
            user_data = json.load(f)
        main(user_data)
        print("sleeping for 7 minutes...")
        time.sleep(420)
