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
	time.sleep(2)
	# import ipdb; ipdb.set_trace();
	if mode == 1:
		url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=' + pincode + '&date=' + date
	else:
		url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=' + dist_id +'&date=' + date
	res = requests.get(
		url = url,
		headers= {
	            'accept': 'application/json',
	            'Accept-Language': 'hi_IN'
	        },
		)

	result = res.json()["sessions"];
	validSlots = []
	for res in result:
		if res['min_age_limit'] <= age:
			validSlots.append(res)
	return validSlots


def checkVaccineAvailibility(email, mode, dist_id, pin, age):
	dates = next10Days()
	full_data = []
	for date in dates:
		full_data.extend(getSlots(email, mode, dist_id, pin, age, date))
	if(full_data):
		print("notifying to " + email)
		notifyUser(email, full_data)


def next10Days():
	base = datetime.datetime.today()
	dates = []
	for x in range(0, 5):
		data = base + datetime.timedelta(days=x)
		dates.append(data.strftime('%d-%m-%Y'))
	return dates


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
	# main()
	while(True):
		main();
		print("sleeping for 5 minutes...")
		time.sleep(300);