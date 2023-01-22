"""
Pull out up to 8 Waves from a DW7 file
"""



import wave
import struct
import pathlib

# pip install numpy
import numpy


def dw7_to_wav(INPUT : pathlib.Path, OUTPUT : pathlib.Path):

    with open(INPUT, "rb") as f1:
        X = f1.read()



    OVERALL_LENGTH, = struct.unpack_from("<I", X, 0x0C)
    if OVERALL_LENGTH + 0x114 != len(X):
        raise Exception

    LENGTHS = struct.unpack_from("<65I", X, 0x10)
    
    START = len(X) - sum(LENGTHS)
    
    print("{0:X}".format(START))
    
    
    if START < 0x114:
        raise Exception
    
    
    
    J = START
    
    for I, L in enumerate(LENGTHS):
      
        if L > 0:
      
            END = J + L


            Z = (numpy.frombuffer(X[J:END], dtype=numpy.int8) + 128).astype(numpy.uint8)
            
            f2 = wave.open(str(OUTPUT.parent.joinpath(str(OUTPUT.stem) + "_{0}".format(I) + OUTPUT.suffix)), "wb")
            f2.setnchannels(1)
            f2.setsampwidth(1)
            f2.setframerate(22050)

            f2.writeframes(bytes(Z))

            f2.close()
                    
            
            
            J = END



if __name__=="__main__":
    
    raise Exception("dw7_to_wav should be called as a function only")

