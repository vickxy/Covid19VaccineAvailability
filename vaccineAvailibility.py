import requests
import datetime
import time
import json
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

cred_file = open('cred.json',)
cred = json.load(cred_file)


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
		print(e)


def getSlots(email, mode, dist_id, pin, age, date):
	time.sleep(5)
	print("fetching data for id: " + email)
	if mode == 1:
		url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=' + pin + '&date=' + date
	else:
		url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=' + dist_id +'&date=' + date
	res = requests.get(
		url = url,
		headers= {
	            'accept': 'application/json',
	            'Accept-Language': 'hi_IN'
	        },
		)

	result = res.json()["centers"]
	validSlots = []
	for res in result:
		data = {}
		data['name'] = res['name']
		data['sessions'] = []
		for re in res['sessions']:
			# if re['min_age_limit'] <= age:
			# 	print(re['available_capacity'])
			# 	print(re['date'])
			if re['min_age_limit'] <= age and re['available_capacity'] > 1:
				data['sessions'].append(re)
				validSlots.append(data)
	#import ipdb; ipdb.set_trace();
	return validSlots


def checkVaccineAvailibility(email, mode, dist_id, pin, age):
	date = datetime.datetime.today().strftime('%d-%m-%Y')
	full_data = getSlots(email, mode, dist_id, pin, age, date)
	if(full_data):
		print("notifying to " + email)
		notifyUser(email, full_data)

def main():
	print("fetching details...")
	try:
		f = open('data.json',)
		data = json.load(f)
		for i in data['users']:
			email = i['email']
			pin = i['pincode']
			age = i['age']
			mode = i['mode']
			dist_id=i['dist_id']
			checkVaccineAvailibility(email, mode, dist_id, pin, age)
	except Exception as e:
		print("Error ")
		print(e)
	


if __name__ == "__main__":
	while(True):
		main();
		print("sleeping for 4 minutes...")
		time.sleep(240);