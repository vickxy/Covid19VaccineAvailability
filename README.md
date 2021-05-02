# Covid19VaccineAvailibility

We are looking into COWIN portal after every 5 minutes to check the availibility based on your State, District/Pincode and Age
To run this script follow the steps given below
 - Enable application access on your gmail with steps given here: https://support.google.com/accounts/answer/185833?p=InvalidSecondFactor&visit_id=637554658548216477-2576856839&rd=1
- Enter sender details in cred.json
- Enter receivers details in data.json
-- email
-- pincode
-- mode [1/2 : 1 for pincode and 2 for district wise search]
-- age
-- dist_id
- Fetch stateIDs from this API
curl -X GET "https://cdn-api.co-vin.in/api/v2/admin/location/states" -H "accept: application/json" -H "Accept-Language: hi_IN"
- Fetch dist_id from this API
curl -X GET "https://cdn-api.co-vin.in/api/v2/admin/location/districts/stateID" -H "accept: application/json" -H "Accept-Language: hi_IN"

- Dependencies
-- requests
-- smtplib
- Compatible with python3 only
- On your termial type: python vaccineAvailibility.py