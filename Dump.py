#!/usr/bin/env python
# -*- coding: utf8 -*-

from time import sleep
import MFRC522

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

card_detected = False  # to eliminate duplicate no card errors

# This loop keeps checking for chips.
# If one is near it will get the UID and authenticate
while True:
    try:
        # Scan for cards
        MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        print("Card detected")
        card_detected = True

        # Get the UID of the card
        uid = MIFAREReader.MFRC522_Anticoll()

        # Print UID
        print("Card read UID: {!r}".format(uid[:4]))

        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Dump the data
        MIFAREReader.MFRC522_DumpClassic1K(key, uid)

        # Stop
        MIFAREReader.MFRC522_StopCrypto1()

    except MFRC522.NoCardInField:
        if card_detected:
            card_detected = False
            print("No card in field")
        sleep(0.1)
    except MFRC522.MifareError as error:
        print("Error: {!r}".format(error))
    except KeyboardInterrupt:
        print("Ctrl+C captured, ending read.")
        break
