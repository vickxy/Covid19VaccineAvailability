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
with open('data.json', 'r') as f:
    user_data = json.load(f)


def notifyUser(receiver, validSlots):
    sender = cred["sender"]
    auth = cred["auth"]

    mail_content = json.dumps(validSlots, indent=1)
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = 'Vaccine slots availablity'
    message.attach(MIMEText(mail_content, 'plain'))

    try:
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender, auth)
        text = message.as_string()
        session.sendmail(sender, receiver, text)
        session.quit()
    except Exception as e:
        print("Error: unable to send email")
        print(format_exc())


def getSlots(mode, dist_id, pin, date):
    # time.sleep(5)
    print(f"Fetching data for {date} and next 7 days")
    if mode == 1:
        url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=' + pin + '&date=' + date
    else:
        url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=' + dist_id + '&date=' + date
    res = requests.get(
        url=url,
        headers={
            'accept': 'application/json',
            'Accept-Language': 'hi_IN'
        },
    )

    result = res.json()["centers"]
    validSlots = []
    for res in result:
        data = {}
        # data = {f: v for k, v in res.items()}
        data['name'] = res['name']
        data['district_name'] = res['district_name']
        data['block_name'] = res['block_name']
        data['pincode'] = res['pincode']
        data['sessions'] = []
        for re in res['sessions']:
            # if re['min_age_limit'] <= age:
            # 	print(re['available_capacity'])
            # 	print(re['date'])
            if re['available_capacity'] >= 1:
                data['sessions'].append(re)
                validSlots.append(data)
    # import ipdb; ipdb.set_trace();
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
        user_age = user.get('age')
        filtered_data = []
        for data in full_data:
            valid_session = []
            for session in data.get('sessions', []):
                if int(session['min_age_limit']) <= user_age:
                    valid_session.append(session)
        if valid_session:
            data_copy = deepcopy(data)
            data_copy['sessions'] = valid_session
            filtered_data.append(data_copy)

        if not filtered_data:
            continue
        print(
            f"User with age {user_age} vaccine is available at {len(filtered_data)} places")
        email = user['email']

        print("notifying to " + email)
        notifyUser(email, filtered_data)


def main():
    print("fetching details...")
    try:
        region_user = defaultdict(lambda: [])
        for i in user_data['users']:
            pin = i['pincode']
            mode = i['mode']
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
        main()
        print("sleeping for 4 minutes...")
        time.sleep(240)
