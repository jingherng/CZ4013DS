from Config import *
import math

# packed object index format:
# 0 : service ID
# 1 : number of objects, n
# 2 to (n+1) : typeof(obj)
# rest : objects

    # [1, 3, STR, INT, INT, filePathname, offset, numBytes]
    # [1, 3, STR, INT, INT, 'abc', 1, 1]
    # [2, 3, STR, INT, STR, filePathname, offset, seq]
    # [3, 2, STR, INT, filePathname, monitorInterval]

def pack(msg):
    numObj = msg[1]
    packed = [msg[0], numObj]

    for i in range(2, numObj + 2):
        packed.append(msg[i])
        if msg[i] == INT:
            packed.extend(packInt(msg[numObj+i]))
        elif msg[i] == STR:
            packed.extend(packString(msg[numObj+i]))
        elif msg[i] == FLT:
            packed.extend(packFloat(msg[numObj+i]))
        elif msg[i] == ERR:
            packed.extend(packString(msg[numObj+i]))
    return bytes(packed)

def unpack(msg):
    serviceID = msg[0]
    numObj = msg[1]
    unpacked = [serviceID, numObj]
    currentIndex = 2
    for i in range(numObj):
        lenOfCurrentObj = msg[currentIndex + 1] + 1

        if msg[currentIndex] == INT:
            unpacked.append(unpackInt(msg[currentIndex+1: currentIndex+lenOfCurrentObj]))
        elif msg[currentIndex] == STR:
            unpacked.append(unpackString(msg[currentIndex+1: currentIndex+lenOfCurrentObj]))
        elif msg[currentIndex] == FLT:
            unpacked.append(unpackFloat(msg[currentIndex+1: currentIndex+lenOfCurrentObj]))
        elif msg[currentIndex] == ERR:
            unpacked.append(unpackString(msg[currentIndex+1: currentIndex+lenOfCurrentObj]))
        currentIndex += lenOfCurrentObj
        
    return unpacked

def packInt(obj):
    numList = []
    for i in range(4):
        numList.append(obj % 256)
        obj = obj // 256

    numList.append(4+1)
    numList = numList[::-1]
    return numList

def unpackInt(obj):
    num = 0
    for i in range(1, obj[0]):
        num += (obj[i]*int(math.pow(256, len(obj) - i - 1)))
    return num

def packString(obj):
    arr = [0 for i in range(len(obj)+1)]
    arr[0] = len(obj) + 1
    for i in range(len(obj)):
        arr[i+1] = ord(obj[i])
    return arr

def unpackString(obj):
    str = ''
    for i in range(1, obj[0]):
        str += chr(obj[i])
    return str

def packFloat(obj):
    return packString(str(obj))

def unpackFloat(obj):
    return float(unpackString(obj))