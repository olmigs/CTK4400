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

    if SLOT not in (1, 2, 3, 4, 5):
        raise Exception("SLOT needs to be in 1 - 5")


    with wave.open(str(INPUT), "rb") as f:
        print(f.getsampwidth())
        print(f.getframerate())
        print("0x{0:X}".format(f.getnframes()))
        
        
        C = f.readframes(f.getnframes())
        Z_FRAMERATE = f.getframerate()
        
        
        print(len(C))
        
        if f.getsampwidth() == 1:   # 8-Bit unsigned
            Z = (numpy.frombuffer(C, dtype=numpy.uint8) - 128).astype(numpy.int8)
        elif f.getsampwidth() == 2:   # 16-Bit signed
            Z = numpy.frombuffer(C, dtype=numpy.int16)
        elif f.getsampwidth() == 4:   # 32-Bit signed
            Z = numpy.frombuffer(C, dtype=numpy.int32)
        else:
            raise Exception("Only 8-, 16- and 32-bit PCM wave formats supported")
        
        
        
        # Choose the first channel only. From a stereo signal, this will be the
        # left one.
        # A stereo-to-mono conversion would be better, but this script is really
        # intended for mono inputs -- just do the simplest thing possible here.

        if f.getnchannels() != 1:
            Z = Z[::f.getnchannels()]



    TARGET_FREQ = 22050

    if Z_FRAMERATE == TARGET_FREQ:

        # No re-sampling required, we're already at the correct sample rate
        U = Z

    else:
        print("Resampling")
        U = scipy.signal.resample(Z, int( float(TARGET_FREQ) / float(Z_FRAMERATE) * float(Z.size)  )  )

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

    W = (V + 0).astype(numpy.uint8)

    print(W)
    print(max(W))
    print(min(W))





    LEN = len(bytes(W))
    
    if LEN > 0x3FFFF:
        # This is approximately 10s at 22050Hz. It may be worth trying longer than
        # this to see if it works?
        raise Exception(f"Input wave has {LEN} sample points which is too long!")

        

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
        ( b"\xE4\xB0\x31\xA1\xC2",  0x6C ),   # SLOT 5
        ( b"\x8A\x41\x47\x02\x43",  0x00 ),   # SLOT 6
        ( b"\x51\x67\x47\x02\x40",  0x3F ),   # SLOT 7
        ( b"\x93\xAD\xFF\xFF\x25",  0x53 ),   # SLOT 8
    ]


    if SLOT in (1, 2, 3, 4, 5, 6, 7, 8):
        B += MAGIC_NUMBERS[SLOT-1][0] + "S{0:d}:Orgnl        ".format(SLOT).encode('latin-1')
        B += struct.pack("<2H", MAGIC_NUMBERS[SLOT-1][1], 0xE8)
    else:
        raise Exception

    B += struct.pack("<3I", 0x20, 0x20, 0)
    B += b"\x00\x00\x00"

    B += struct.pack("<7I", 0x22, 0, 0x22, 0, 0x22, 0, 0x22)
    B += b"\x00\x00"

    B += struct.pack("<II", LEN - 0x28, 0x20000)
    B += b"\x00"
    B += struct.pack("<I", LEN - 0x18)[:3]  # Lowest 3 bytes only
    B += struct.pack("<I", LEN - 0x08)
    B += struct.pack("<HH", 0, 2)
    B += b"\xa1\x53"
    B += struct.pack("<IH", 0x80023C, 0)



    B += bytes(W)


    with open(OUTPUT, "wb") as f4:
        f4.write(B)





if __name__=="__main__":
    
    raise Exception("wav_to_tw7 should be called as a function only")



