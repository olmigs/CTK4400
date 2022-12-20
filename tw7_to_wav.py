"""
Pull out a Wave from a TW7 file
"""



import wave
import struct
import pathlib

# pip install numpy
import numpy


def tw7_to_wav(INPUT : pathlib.Path, OUTPUT : pathlib.Path):

    with open(INPUT, "rb") as f1:
        X = f1.read()

    Z = (numpy.frombuffer(X[0x176:], dtype=numpy.int8) + 128).astype(numpy.uint8)


    f2 = wave.open(str(OUTPUT), "wb")
    f2.setnchannels(1)
    f2.setsampwidth(1)
    f2.setframerate(16000)

    f2.writeframes(bytes(Z))

    f2.close()




if __name__=="__main__":
    
    tw7_to_wav("S2_Orgnl.tw7", pathlib.Path("Wav", "S2.wav"))


