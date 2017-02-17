MFRC522-python based UID reader
==============

A small class to interface with the NFC reader Module MFRC522 on the Raspberry Pi.

This is a modified Python port of the example code for the NFC module MF522-AN.

##Requirements
This code requires you to have spidev installed from pip

##Disclaimer
This code is only intended to be able to read UIDs, and all other functionality left over from
the original code is untested.


## Pins
You can use [this](http://i.imgur.com/y7Fnvhq.png) image for reference.

| Name | Pin # | Pin name   |
|------|-------|------------|
| SDA  | 24    | GPIO8      |
| SCK  | 23    | GPIO11     |
| MOSI | 19    | GPIO10     |
| MISO | 21    | GPIO9      |
| IRQ  | None  | None       |
| GND  | Any   | Any Ground |
| RST  | 17    | Any High   |
| 3.3V | 1     | 3V3        |

##Usage
Import the class by importing MFRC522 in the top of your script. For more info see the examples.
