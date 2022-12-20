"""
Reads in a WAV file and outputs a TW7 (Casio format).
"""


import math
import sys
import struct
import wave

import os
import os.path

# pip install numpy
import numpy

# pip install scipy
import scipy
import scipy.signal





LEN = 0x9090
PERIOD = 625.



#Z = numpy.frombuffer(X[0x176:], dtype=numpy.int8)


Y = bytearray(b'\x00' * LEN)


for I in range(LEN):
    A = int(127. * math.sin(   float(I)*2.*math.pi / float(PERIOD)  ))
    if A < 0:
        A = A + 256
    
    Y[I] = A
    

B = b"TW7FCTK-4400"
B += struct.pack("<3I", LEN + 0x62, 0, LEN)
B += b"\x00" * 0xFC


B += b"\xDB\xD4\x50\x97\x69" + b"S2:Orgnl        "

B += struct.pack("<2H", 0xEF, 0xE8)
B += struct.pack("<4I", 0x2000, 0x2000, 0, 0)
B += b"\x00"

B += struct.pack("<7I", 0x22, 0, 0x22, 0, 0x22, 0, 0x22)
B += b"\x00\x00"

B += struct.pack("<IIH", LEN - 0x28, 0x20000, LEN - 0x18)


with wave.open(os.path.join("..", "S2.wav"), "rb") as f:
    print(f.getsampwidth())
    print(f.getframerate())
    print("0x{0:X}".format(f.getnframes()))
    
    
    C = f.readframes(f.getnframes())
    
    
print(len(C))


#print(C[0x8000:0x8200].hex(" ").upper())


Z = (numpy.frombuffer(C, dtype=numpy.uint8) - 128).astype(numpy.int8)   # zero-positioned

TARGET_FREQ = 14250

U = scipy.signal.resample(Z, int( float(TARGET_FREQ) / float(f.getframerate()) * float(Z.size)  )  )

print(U)
print(max(U))
print(min(U))

m = max(max(U), -min(U))

if m <= 0:
    raise Exception

U = U * (127.5 / m)  # Scale to maximum extent

V = U.astype(numpy.int8)

print(V)
print(max(V))
print(min(V))

W = (V + 128).astype(numpy.uint8)

print(W)
print(max(W))
print(min(W))




f2 = wave.open("R2.wav", "wb")
f2.setnchannels(1)
f2.setsampwidth(1)
f2.setframerate(TARGET_FREQ)

f2.writeframes(bytes(W))

f2.close()

B += bytes(W)


with open("3.tw7", "wb") as f4:
    f4.write(B)



