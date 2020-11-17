'''
Created on 2018

@author: programmer
'''
import ctypes, struct

'''tsclibrary = ctypes.WinDLL("c:\\64\\TSCLIB.dll");'''
tsclibrary = ctypes.WinDLL(".//libs//TSCLIB.dll")

if __name__ == '__main__':
    pass
a_str = "HELLO WORLD"
print(a_str)

'''
tsclibrary.about()
'''


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


cid = '1000'


tsclibrary.openportW("TSC TTP-244 Pro")
tsclibrary.sendcommandW("SIZE 97 mm, 20 mm")
tsclibrary.sendcommandW("GAP 2 mm, 0 mm")
tsclibrary.sendcommandW("REFERENCE 12, 0")
tsclibrary.sendcommandW("DIRECTION 1")
tsclibrary.sendcommandW("CLS")


def put_label(imei, counter):
    did = imei_to_did(imei)
    did_cid = did + ':' + cid
    # shift = 0
    # shift = 260
    # shift = 520
    shift = (counter % 3) * 260
    tsclibrary.sendcommandW('TEXT ' + str(shift + 40) + ',25,"1",90,1,1,"' + did_cid[:12] + '"')
    tsclibrary.sendcommandW('TEXT ' + str(shift + 20) + ',25,"1",90,1,1,"' + did_cid[12:] + '"')
    tsclibrary.sendcommandW('QRCODE ' + str(shift + 55) + ',25,H,4,A,0,M2,"' + did_cid + '"')
    tsclibrary.sendcommandW('TEXT ' + str(shift + 220) + ',25,"1",90,1,1,"' + imei[:10] + '"')
    tsclibrary.sendcommandW('TEXT ' + str(shift + 200) + ',25,"1",90,1,1,"' + imei[10:] + '"')


with open('.//imei.txt', 'r') as f:
    lines = f.readlines()
    lines.sort()
    counter = 0
    for line in lines:
        if len(line) < 10:
            continue
        imei = line.strip(' \t\n\r')
        print(imei)
        put_label(imei, counter)
        counter = counter + 1
        if counter % 3 == 0:
            tsclibrary.sendcommandW('PRINT 1,1')
            tsclibrary.sendcommandW("CLS")

    if counter % 3 != 0:
        tsclibrary.sendcommandW('PRINT 1,1')
        tsclibrary.sendcommandW("CLS")


tsclibrary.about()
tsclibrary.closeport()

