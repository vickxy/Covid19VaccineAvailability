# Covid19VaccineAvailability

We are looking into COWIN portal after every 5 minutes to check the availibility based on your State, District/Pincode and Age
## To run this script follow the steps given below
- Enable application access on your gmail with steps given here:
https://support.google.com/accounts/answer/185833?p=InvalidSecondFactor&visit_id=637554658548216477-2576856839&rd=1
- Enter sender details in cred.json
```
{
	"sender": "sender's_id",
	"auth": "sender's_auth"
}
```
- Enter receivers details in data.json [note mode 1 for Pincode 2 for District wise]
```
{
	"users":
	[
		{
			"email":"receiver@gmail.com",
			"pincode": "560068",
			"age":28,
			"mode": 2,
			"dist_id": "294"
		}
	]
}
```

- Fetch stateIDs from this API
curl -X GET "https://cdn-api.co-vin.in/api/v2/admin/location/states" -H "accept: application/json" -H "Accept-Language: hi_IN"
- Fetch dist_id from this API
curl -X GET "https://cdn-api.co-vin.in/api/v2/admin/location/districts/stateID" -H "accept: application/json" -H "Accept-Language: hi_IN"

- Compatible with python3 only
- On your termial type: python vaccineAvailibility.py
# Dependencies
- requests
- smtplib
