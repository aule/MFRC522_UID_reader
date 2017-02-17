#!/usr/bin/env python
# -*- coding: utf8 -*-

import MFRC522

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

# This loop keeps checking for chips.
# If one is near it will get the UID and authenticate
while True:
    try:
        # Scan for cards
        tag_type = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        print("Card detected")

        # Get the UID of the card
        uid = MIFAREReader.MFRC522_Anticoll()

        print("Card read UID: {!r}".format(uid[:4]))

        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        print(MIFAREReader.MFRC522_Read(8))
        MIFAREReader.MFRC522_StopCrypto1()

    except MFRC522.MifareError as error:
        print("Error: {!r}".format(error))
    except KeyboardInterrupt:
        print("Ctrl+C captured, ending read.")
        break
