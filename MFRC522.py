#!/usr/bin/env python
# -*- coding: utf8 -*-

from spidev import SpiDev
from time import sleep


class MifareError(Exception):
    pass


class NoCardInField(MifareError):
    pass


class InvalidCard(MifareError):
    pass


class MifareAuthError(MifareError):
    pass


class MFRC522:
    NRSTPD = 22

    MAX_LEN = 16

    PCD_IDLE = 0x00
    PCD_AUTHENT = 0x0E
    PCD_RECEIVE = 0x08
    PCD_TRANSMIT = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC = 0x03

    PICC_REQIDL = 0x26
    PICC_REQALL = 0x52
    PICC_ANTICOLL = 0x93
    PICC_SElECTTAG = 0x93
    PICC_AUTHENT1A = 0x60
    PICC_AUTHENT1B = 0x61
    PICC_READ = 0x30
    PICC_WRITE = 0xA0
    PICC_DECREMENT = 0xC0
    PICC_INCREMENT = 0xC1
    PICC_RESTORE = 0xC2
    PICC_TRANSFER = 0xB0
    PICC_HALT = 0x50

    Reserved00 = 0x00
    CommandReg = 0x01
    CommIEnReg = 0x02
    DivlEnReg = 0x03
    CommIrqReg = 0x04
    DivIrqReg = 0x05
    ErrorReg = 0x06
    Status1Reg = 0x07
    Status2Reg = 0x08
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    WaterLevelReg = 0x0B
    ControlReg = 0x0C
    BitFramingReg = 0x0D
    CollReg = 0x0E
    Reserved01 = 0x0F

    Reserved10 = 0x10
    ModeReg = 0x11
    TxModeReg = 0x12
    RxModeReg = 0x13
    TxControlReg = 0x14
    TxAutoReg = 0x15
    TxSelReg = 0x16
    RxSelReg = 0x17
    RxThresholdReg = 0x18
    DemodReg = 0x19
    Reserved11 = 0x1A
    Reserved12 = 0x1B
    MifareReg = 0x1C
    Reserved13 = 0x1D
    Reserved14 = 0x1E
    SerialSpeedReg = 0x1F

    Reserved20 = 0x20
    CRCResultRegM = 0x21
    CRCResultRegL = 0x22
    Reserved21 = 0x23
    ModWidthReg = 0x24
    Reserved22 = 0x25
    RFCfgReg = 0x26
    GsNReg = 0x27
    CWGsPReg = 0x28
    ModGsPReg = 0x29
    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D
    TCounterValueRegH = 0x2E
    TCounterValueRegL = 0x2F

    Reserved30 = 0x30
    TestSel1Reg = 0x31
    TestSel2Reg = 0x32
    TestPinEnReg = 0x33
    TestPinValueReg = 0x34
    TestBusReg = 0x35
    AutoTestReg = 0x36
    VersionReg = 0x37
    AnalogTestReg = 0x38
    TestDAC1Reg = 0x39
    TestDAC2Reg = 0x3A
    TestADCReg = 0x3B
    Reserved31 = 0x3C
    Reserved32 = 0x3D
    Reserved33 = 0x3E
    Reserved34 = 0x3F

    serNum = []

    def __init__(self, port=0, device=0):
        self.spi = SpiDev()
        self.spi.open(port, device)
        self.MFRC522_Init()

    def MFRC522_Reset(self):
        self.Write_MFRC522(self.CommandReg, self.PCD_RESETPHASE)

    def Write_MFRC522(self, addr, val):
        self.spi.xfer([(addr << 1) & 0x7E, val])

    def Read_MFRC522(self, addr):
        val = self.spi.xfer([((addr << 1) & 0x7E) | 0x80, 0])
        return val[1]

    def SetBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp | mask)

    def ClearBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp & (~mask))

    def AntennaOn(self):
        temp = self.Read_MFRC522(self.TxControlReg)
        if(~(temp & 0x03)):
            self.SetBitMask(self.TxControlReg, 0x03)

    def AntennaOff(self):
        self.ClearBitMask(self.TxControlReg, 0x03)

    def MFRC522_ToCard(self, command, send_data):
        irqEn = 0x00
        waitIRq = 0x00

        if command == self.PCD_AUTHENT:
            irqEn = 0x12
            waitIRq = 0x10
        if command == self.PCD_TRANSCEIVE:
            irqEn = 0x77
            waitIRq = 0x30

        self.Write_MFRC522(self.CommIEnReg, irqEn | 0x80)
        self.ClearBitMask(self.CommIrqReg, 0x80)
        self.SetBitMask(self.FIFOLevelReg, 0x80)

        self.Write_MFRC522(self.CommandReg, self.PCD_IDLE)

        for value in send_data:
            self.Write_MFRC522(self.FIFODataReg, value)

        self.Write_MFRC522(self.CommandReg, command)

        if command == self.PCD_TRANSCEIVE:
            self.SetBitMask(self.BitFramingReg, 0x80)

        def await_interrupt(retry_count=100, delay=0.01):
            for _ in range(retry_count):
                sleep(delay)
                interrupts = self.Read_MFRC522(self.CommIrqReg)
                if (interrupts & 0x01) or (interrupts & waitIRq):
                    return interrupts
            raise MifareError("No response within waiting period.")

        try:
            interrupts = await_interrupt()
        finally:
            self.ClearBitMask(self.BitFramingReg, 0x80)

        if (self.Read_MFRC522(self.ErrorReg) & 0x1B):
            raise MifareError()

        if interrupts & irqEn & 0x01:
            raise NoCardInField()

        if command == self.PCD_TRANSCEIVE:
            count = self.Read_MFRC522(self.FIFOLevelReg)
            last_bits = self.Read_MFRC522(self.ControlReg) & 0x07
            if last_bits:
                length_in_bits = (count - 1) * 8 + last_bits
            else:
                length_in_bits = count * 8

            count = min(self.MAX_LEN, max(1, count))

            returned_data = [
                self.Read_MFRC522(self.FIFODataReg) for _ in range(count)
            ]

            return (returned_data, length_in_bits)
        else:
            return ([], 0)

    def MFRC522_Request(self, req_mode):
        tag_type = [req_mode]

        self.Write_MFRC522(self.BitFramingReg, 0x07)

        (backData, backBits) = self.MFRC522_ToCard(
            self.PCD_TRANSCEIVE, tag_type
        )

        if (backBits != 0x10):
            raise MifareError()

        return backData

    def MFRC522_Anticoll(self):  # Anticollision
        serial = [self.PICC_ANTICOLL, 0x20]

        self.Write_MFRC522(self.BitFramingReg, 0x00)

        serial_number, _ = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, serial)

        if len(serial_number) != 5:
            raise InvalidCard("Serial number had invalid length")

        checksum = 0
        for byte in serial_number:
            checksum ^= byte
        if checksum:
            raise InvalidCard("Serial number checksum failed")

        return serial_number

    def CalulateCRC(self, data):
        self.ClearBitMask(self.DivIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80)
        for byte in data:
            self.Write_MFRC522(self.FIFODataReg, byte)
        self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)
        for _ in range(0xFF):
            if self.Read_MFRC522(self.DivIrqReg) & 0x04:
                break
        pOutData = [
            self.Read_MFRC522(self.CRCResultRegL),
            self.Read_MFRC522(self.CRCResultRegM)
        ]
        return pOutData

    def MFRC522_SelectTag(self, serial_number):
        backData = []
        buf = [self.PICC_SElECTTAG, 0x70]
        buf.extend(serial_number)
        buf.extend(self.CalulateCRC(buf))
        try:
            backData, backLen = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
        except MifareError:
            return 0  # No idea why, but the original code did this

        if backLen == 0x18:
            print("Size: {}".format(backData[0]))
            return backData[0]
        else:
            return 0

    def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
        buf = [
            authMode,  # First byte should be the authMode (A or B)
            BlockAddr  # Second byte is the trailerBlock (usually 7)
        ]

        # Now we need to append the authKey which usually is 6 bytes of 0xFF
        buf.extend(Sectorkey)

        # Next we append the first 4 bytes of the UID
        buf.extend(serNum[:4])

        # Now we start the authentication itself
        try:
            backData, backLen = self.MFRC522_ToCard(self.PCD_AUTHENT, buf)
        except NoCardInField:
            raise
        except MifareError:
            raise MifareAuthError()

        # Check if crypto1 unit is switched on
        if not (self.Read_MFRC522(self.Status2Reg) & 0x08):
            MifareAuthError("MFCrypto1On bit not enabled")

    def MFRC522_StopCrypto1(self):
        self.ClearBitMask(self.Status2Reg, 0x08)

    def MFRC522_Read(self, block_address):
        recv_data = [self.PICC_READ, block_address]
        recv_data.extend(self.CalulateCRC(recv_data))
        returned_data, _ = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recv_data)
        if len(returned_data) == 16:
            print("Sector {} {}".format(block_address, returned_data))
        return returned_data

    def MFRC522_Write(self, block_address, data):
        buf = [self.PICC_WRITE, block_address]
        buf.extend(self.CalulateCRC(buf))
        returned_data, length = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
        if length != 4 or (returned_data[0] & 0x0F) != 0x0A:
            raise MifareError()

        buf = []
        buf.extend(data)
        buf.extend(self.CalulateCRC(buf))
        returned_data, length = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
        if length != 4 or (returned_data[0] & 0x0F) != 0x0A:
            raise MifareError()

    def MFRC522_DumpClassic1K(self, key, uid):
        for i in range(64):
            self.MFRC522_Auth(self.PICC_AUTHENT1A, i, key, uid)
            print(self.MFRC522_Read(i))

    def MFRC522_Init(self):
        self.MFRC522_Reset()

        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)

        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)
        self.AntennaOn()
