#!/usr/bin/env python3
import ctypes, struct, requests, json, time
from config import cids, remote_url


'''tsclibrary = ctypes.WinDLL("c:\\64\\TSCLIB.dll");'''
tsclibrary = ctypes.WinDLL(".//libs//TSCLIB.dll")


def imei_to_did(imei):
    return struct.pack('<Q', int(imei)).hex().lower()


# Returns True if n is valid EMEI
def isValidEMEI(s):
    # If length is not 15 then IMEI is Invalid
    if type(s) is not str or len(s) != 15 or s.isdigit() is not True:
        return False
    n = int(s)
    checksum = 0
    for i in range(15, 0, -1):
        d = n % 10
        if i % 2 == 0:
            # Doubling every alternate digit
            d = 2 * d
        # Finding checksum of the digits
        checksum = checksum + (d % 10) + (d // 10)
        n = n // 10
    return (checksum % 10) == 0


while True:
    cid = input("CID:")
    if cid in cids:
        break
    else:
        print('invalid cid, try again!')


def printer_prepare():
    tsclibrary.openportW("TSC TTP-244 Pro")
    tsclibrary.sendcommandW("SIZE 97 mm, 20 mm")
    tsclibrary.sendcommandW("GAP 2 mm, 0 mm")
    tsclibrary.sendcommandW("REFERENCE 12, 0")
    tsclibrary.sendcommandW("DIRECTION 1")
    tsclibrary.sendcommandW("CLS")


def printer_flush():
    tsclibrary.printlabelW("1", "1")
    tsclibrary.sendcommandW("CLS")
    tsclibrary.closeport()


def put_label(imei, counter):
    print(imei)
    did = imei_to_did(imei)
    did_cid = did + ':' + cid
    # shift = 0
    # shift = 260
    # shift = 520
    shift = (counter % 3) * 260
    did_pos = ',25,"1",90,1,1,"'
    qr_pos = ',25,H,4,A,0,M2,"'
    imei_pos = ',25,"1",90,1,1,"'
    tsclibrary.sendcommandW('TEXT ' + str(shift + 40) + did_pos + did_cid[:12] + '"')
    tsclibrary.sendcommandW('TEXT ' + str(shift + 20) + did_pos + did_cid[12:] + '"')
    tsclibrary.sendcommandW('QRCODE ' + str(shift + 55) + qr_pos + did_cid + '"')
    tsclibrary.sendcommandW('TEXT ' + str(shift + 220) + imei_pos + imei[:10] + '"')
    tsclibrary.sendcommandW('TEXT ' + str(shift + 200) + imei_pos + imei[10:] + '"')


current_imei = ''


def get_imei():
    while True:
        time.sleep(1)
        para = {'imei': 'imei'}
        r = requests.get(remote_url, params=para)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            # print(r.headers.get('content-type'))
            data = json.loads(r.text)
            global current_imei
            if data['imei'] != current_imei:
                current_imei = data['imei']
                return data['imei']


counter = 0


printer_prepare()


while True:
    imei = get_imei()
    if not isValidEMEI(imei):
        continue    # ignore invalid data
    put_label(imei, counter)
    counter = counter + 1
    if counter % 3 == 0:        # flush every 3rd labels
        printer_flush()
        time.sleep(1)
        print('*******************')
        printer_prepare()


# flush if there is label pending in printer
if counter % 3 != 0:
    printer_flush()


