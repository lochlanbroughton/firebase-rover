// ----------------------------------------
// REQUIRES
// ----------------------------------------
var firebase        = require("firebase"),
    firebaseConfig  = require("./firebase-config.json"),
    PythonShell     = require('python-shell');


// ----------------------------------------
// CONFIGURE FIREBASE
// ----------------------------------------
var firebaseConfig = {
  apiKey: firebaseConfig.apiKey,
  authDomain: firebaseConfig.authDomain,
  databaseURL: firebaseConfig.databaseURL,
};
firebase.initializeApp(firebaseConfig);

// Establish database and assign vehicles and sessions
const database        = firebase.database(),
      roverKey        = 'mk1',
      sessionKey      = database.ref('sessions').push().key;

database.ref('sessions/' + sessionKey + '/vehicles').set({[roverKey]: true});
database.ref('vehicles/' + roverKey + '/sessions').set({[sessionKey]: true});


// ----------------------------------------
// PYTHON-SHELL SETUP AND LISTENERS
// ----------------------------------------
var rover = new PythonShell('rover.py', {
  mode: 'json',
  pythonOptions: ['-u'],
});

// Establish listeners
rover.on('message', function(data) { // Message received (in JSON format)

    var msg   = data.msg;

    if (msg != undefined) {

      if (msg.type == 'message') {
        console.log(msg.body);
        database.ref('sessions/' + sessionKey + '/msg').push(msg);
      } else if (msg.type == 'status') {
        database.ref('vehicles/' + roverKey + '/status').set(msg);
      }

    } else {
      console.log('No message body found');
    }

}).on('close', function (result) { // Script ends

  console.log('rover closed');
  process.exit();

}).on('error', function (err) { // Error detected

  console.log('rover error:');
  console.log(err);

});