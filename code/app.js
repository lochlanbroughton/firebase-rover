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
      vehicleKey      = 'mk1',
      sessionKey      = database.ref('sessions').push().key;
      userKey         = false

database.ref('sessions/' + sessionKey + '/vehicles').set({[vehicleKey]: true});
database.ref('sessions/' + sessionKey + '/users').set({[userKey]: true});
database.ref('vehicles/' + vehicleKey + '/sessions').set({[sessionKey]: true});
database.ref('users/' + userKey + '/sessions').set({[sessionKey]: true});


// ----------------------------------------
// PYTHON-SHELL SETUP AND LISTENERS
// ----------------------------------------
var rover = new PythonShell('rover.py', {
  mode: 'json',
  pythonOptions: ['-u'],
});

// Establish listeners
rover.on('message', function(data) { // Message received (in JSON format)

  var dataType   = data.output.type,
      dataOutput = JSON.encode(data);

      console.log('Message received. dataType: ' + dataType);
      console.log('Message received. dataOutput: ' + dataOutput);

      switch (dataType) {
        case 'session_logs':
          database.ref(dataType + '/' + sessionKey).push(data[dataType]);
          break;
        case 'vehicle_output':
          database.ref(dataType + '/' + vehicleKey).push(data[dataType]);
          break;
      }

}).on('close', function (result) { // Script ends

  console.log('rover closed');
  process.exit();

}).on('error', function (err) { // Error detected

  console.log('rover error:');
  console.log(err);

});
