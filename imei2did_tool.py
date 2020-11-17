import struct


def did_to_imei(did):
    return str(struct.unpack('<Q', bytes.fromhex(did))[0])


with open('ids.txt', 'r') as f1, open('imei.txt', 'a') as f2:
    lines = f1.readlines()
    imeis = []

    for did in lines:
        imei = did_to_imei(did.strip(' \t\n\r'))
        imeis.append(imei)

    imeis.sort(key=lambda x: x[::-1])
    for imei in imeis:
        f2.write(imei + '\n')