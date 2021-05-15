var express = require('express');
var app = express();
app.use(express.json());
var fs = require('fs')
const https = require('https');
const http = require('http');

app.get('/test', (req, res) => {
  res.send('Hello dev.to!');
});

app.get('/users', (req, res) => {
	try {
		fs.readFile('../data.json', function (err, data) {
			var data = JSON.parse(data)
		    res.json({"status": 200, "data": data['total']})
		})
	}catch(err){
		console.log(err)
		resp.json({"status": 500, "data": "error in calling API"})
	}
});

app.post('/districts', function (re, resp) {
	var state_id = re.body['state_id']
	try{
		fs.readFile('state_dist.json', function (err, data) {
			var arr = JSON.parse(data.toString())['states']
			for (var i=0; i < arr.length; i++){
			    if (arr[i]['state_id'] == state_id){
	    			resp.json({"status": 200, "data": arr[i]})
					return;
				}
			}
			resp.json({"status": 404})
		})
	}catch(err){
		console.log(err)
		resp.json({"status": 500})
	}
	
});

app.post('/userinfo', function(re, res){
	try{
		fs.readFile('../data.json', function (err, data) {
	    	var users = JSON.parse(data)['users']
	    	var email = re.body['email']
			const found = users.find(element => element.email === email);
			if(found === undefined){
				saveData(re.body)
				res.json({"status": 200, "data": "subscribed successfully"})
			}else{
				res.json({"status": 200, "data": "user already present with email: " + email})
			}
		})
	}catch(err){
		console.log(err)
		res.json({"status": 400, "data": "subscription failed"})
	}
})

app.post('/unsubscribe', function(re, res){
	try{
		var email = re.body['email']

		fs.readFile('../data.json', function (err, data) {
		var info = JSON.parse(data);
		var total = info['total']
	    var users = info['users']
	    function RemoveNode(email) {
		    return users.filter(function(user) {
		      if (user['email'] == email) {
		          return false;
		      }
		      return true;
		  	});
			}

			var newUsers = {}
			newUsers['total'] = total;
			newUsers['users'] = RemoveNode(email)
		  	fs.writeFile("../data.json", JSON.stringify(newUsers, null, 1), function(err, data){
		    	if(err) console.log('unsubscribe() error', err);
		    });
		})
		res.json({"status": 400, "data": "ubsubscribed for user: " + email})
	}catch(err){
		console.log(err)
		res.json({"status": 400, "data": "ubsubscrib failed for user: " + email})
	}
})

// app.listen(8080, function () {
//   console.log('Listening to Port 8080');
// });


function saveData(user){
	fs.readFile('../data.json', function (err, data) {
	    var json = JSON.parse(data)
	    var total = json['total'] + 1;
	    json['total'] = total;
	    json['users'].push(user)
	    fs.writeFile("../data.json", JSON.stringify(json, null, 1), function(err, data){
	    	if(err) console.log('saveData() error', err);
	    });
	})
}

// Listen both http & https ports
const httpServer = http.createServer(app);
const httpsServer = https.createServer({
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem'),
}, app);

httpServer.listen(80, () => {
    console.log('HTTP Server running on port 80');
});

httpsServer.listen(443, () => {
    console.log('HTTPS Server running on port 443');
});