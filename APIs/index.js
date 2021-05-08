var express = require('express');
var app = express();
app.use(express.json());
var fs = require('fs')
const https = require('https')

app.post('/districts', function (re, resp) {
	const options = {
	  hostname: 'cdn-api.co-vin.in',
	  port: 443,
	  path: '/api/v2/admin/location/districts/'+re.body['state_id'],
	  method: 'GET',
	  headers: {
	  	'accept': 'application/json',
			'Accept-Language': 'hi_IN'
	  }
	}
	const req = https.request(options, res => {
	  res.on('data', d => {
			resp.json(JSON.parse(d.toString()));
	  })
	})

	req.on('error', error => {
	  console.error(error)
		resp.json({"error": 1});
	})

	req.end()
});

app.post('/userinfo', function(re, res){
	try{
		saveData(re.body)
		res.send("subscribed successfully")
	}catch(err){
		console.log(err)
		res.send("subscription failed")
	}
})

app.post('/unsubscribe', function(re, res){
	try{
		var email = re.body['email']

		fs.readFile('../data.json', function (err, data) {
	    var users = JSON.parse(data)['users']
	    function RemoveNode(email) {
		    return users.filter(function(user) {
		      if (user['email'] == email) {
		          return false;
		      }
		      return true;
		  	});
			}

			var newUsers = {}
			newUsers['users'] = RemoveNode(email)
	  	fs.writeFile("../data.json", JSON.stringify(newUsers, null, 1))
		})
		res.send("ubsubscribed for user: " + email)
	}catch(err){
		console.log(err)
		res.send("ubsubscrib failed for user: " + email)
	}
})

app.listen(8000, function () {
  console.log('Listening to Port 8000');
});


function saveData(user){
	fs.readFile('../data.json', function (err, data) {
	    var json = JSON.parse(data)
	    json['users'].push(user)

	    fs.writeFile("../data.json", JSON.stringify(json, null, 1))
	})
}