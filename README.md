# firebase-rover
An experiment using Google Firebase Realtime Database to drive a Raspberry Pi rover remotely.

This project is in development and may not be stable.

Contributors welcome.

## Rover build
Instructions should eventually end up here.

## Initial rover setup
This project is built for a rover running on a Raspberry Pi 3.

SSH to RPI
```bash
$ ssh USERNAME@IP_ADDRESS
```

Clone repo
```bash
$ git clone https://github.com/lochlanbroughton/firebase-rover.git
```

Replace `firebase-config-example.json` contents with own Firebase app config 
```bash
$ cp firebase-config-example.json firebase-config.json
$ nano firebase-config.json
```

### Install dependencies

Install Firebase
```bash
$ npm i firebase
```

While developing we use an Xbox controller paired with the RPI to drive the vehicle. For more info check out: https://github.com/FRC4564/Xbox
```bash
$ sudo apt-get install xboxdrv
```
