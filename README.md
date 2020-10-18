# RFID Occupancy Tracker
An occupancy tracker for the RC522 and the Raspberry Pi

## Demo

![Demo](https://static.paolino.me/render1603055017831.gif)

## Features
* Works with your existing RFID cards/keys, as long as they are 13.56 MHz RFID cards.
* Check-in/check-out log with timestamps (useful for tracking who was where in Corona times)
* Plug and play
* Beautiful command line interface

## Quickstart

    sudo raspi-config

Enable SPI (in Interfacing Options), and reboot, then

    pipenv install
    pipenv run python rfid_tracker/app.py tracker

That's it!

## How to connect the RC522 to the Raspberry PI

More info at https://pimylifeup.com/raspberry-pi-rfid-rc522/

![RC522](https://pi.lbbcdn.com/wp-content/uploads/2017/10/RFID-Fritz-v2.png)
