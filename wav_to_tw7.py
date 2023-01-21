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



    """
    What are these? They appear to depend only on the position of the sample (i.e.
    whether it's S1, S2, etc.), and not on the waveform data at all. They may be
    magic numbers, but they may be something else. Note that there are 8 positions
    in a .AL7 file so 8 entries are given here, but the CTK-4400 only supports a
    maximum of 5 samples with content.    
    """
    MAGIC_NUMBERS = [
        ( b"\x4F\x62\x0E\xF6\x89",  0xE9 ),   # SLOT 1
        ( b"\xDB\xD4\x50\x97\x69",  0xEF ),   # SLOT 2
        ( b"\xE9\xCE\x01\xC3\x71",  0x0E ),   # SLOT 3
        ( b"\xBE\x18\xB0\x0E\xD4",  0x5C ),   # SLOT 4
        ( b"\xBE\x18\xB0\x0E\xD4",  0x5C ),   # SLOT 4
        ( b"\xE4\xB0\x31\xA1\xC2",  0x6C ),   # SLOT 5
        ( b"\x8A\x41\x47\x02\x43",  0x00 ),   # SLOT 6
        ( b"\x51\x67\x47\x02\x40",  0x3F ),   # SLOT 7
        ( b"\x93\xAD\xFF\xFF\x25",  0x53 ),   # SLOT 8
    ]


    if SLOT in (1, 2, 3, 4, 5, 6, 7, 8):
        B += MAGIC_NUMBERS[SLOT-1][0] + b"S{0:d}:Orgnl        ".format(SLOT)
        B += struct.pack("<2H", MAGIC_NUMBERS[SLOT-1][1], 0xE8)
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

    TARGET_FREQ = 21333

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



