"""
Reads in a WAV file and outputs a TW7 (Casio format).
"""


import math
import sys
import struct
import wave
import tempfile

import os
import os.path
import pathlib

# pip install numpy
import numpy

# pip install scipy
import scipy
import scipy.signal



def wav_to_tw7(INPUT : pathlib.Path, OUTPUT : pathlib.Path, SLOT : int = 1):

    if SLOT not in [1, 2]:
        raise Exception("SLOT needs to be either 1 or 2")

    #LEN = 0x9090
    PERIOD = 625.


    with wave.open(str(INPUT), "rb") as f:
        print(f.getsampwidth())
        print(f.getframerate())
        print("0x{0:X}".format(f.getnframes()))
        
        
        C = f.readframes(f.getnframes())
        Z_FRAMERATE = f.getframerate()
        
        
    print(len(C))
    
    LEN = len(C)



    #Y = bytearray(b'\x00' * LEN)


    #for I in range(LEN):
    #    A = int(127. * math.sin(   float(I)*2.*math.pi / float(PERIOD)  ))
    #    if A < 0:
    #        A = A + 256
    #    
    #    Y[I] = A
        

    B = b"TW7FCTK-4400"
    B += struct.pack("<3I", LEN + 0x62, 0, LEN)
    B += b"\x00" * 0xFC


    if SLOT == 1:
        B += b"\x4F\x62\x0E\xF6\x89" + b"S1:Orgnl        "
        B += struct.pack("<2H", 0xE9, 0xE8)
    elif SLOT == 2:
        B += b"\xDB\xD4\x50\x97\x69" + b"S2:Orgnl        "
        B += struct.pack("<2H", 0xEF, 0xE8)
    else:
        raise Exception

    B += struct.pack("<3I", 0x20, 0x20, 0)
    B += b"\x00\x00\x00"

    B += struct.pack("<7I", 0x22, 0, 0x22, 0, 0x22, 0, 0x22)
    B += b"\x00\x00"

    B += struct.pack("<II", LEN - 0x28, 0x20000)
    B += b"\x00"
    B += struct.pack("<H", LEN - 0x18)
    B += b"\x00"
    B += struct.pack("<H", LEN - 0x08)
    B += struct.pack("<IH", 0, 2)
    B += b"\xa1\x53"
    B += struct.pack("<IH", 0x80023C, 0)


    Z = (numpy.frombuffer(C, dtype=numpy.uint8) - 128).astype(numpy.int8)   # zero-positioned

    TARGET_FREQ = 16000

    if Z_FRAMERATE == TARGET_FREQ:
        W = Z
    else:
        print("Resampling")
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

    B += bytes(W)


    with open(OUTPUT, "wb") as f4:
        f4.write(B)





if __name__=="__main__":
    
    raise Exception("wav_to_tw7 should be called as a function only")



