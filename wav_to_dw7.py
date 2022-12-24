
import struct
import wave
import numpy
import scipy
import scipy.signal



def wav_to_dw7(STRUCT):
  
    S = set()
    for KEY in STRUCT:
        S.add(STRUCT[KEY]['file'])
  
    FILES = list(S)
    
    LENGTHS = []
    BINARIES = []
    
    TARGET_FREQ = 16000
    
    for FF in FILES:
        
        with wave.open(str(FF), "rb") as f:
            print(f.getsampwidth())
            print(f.getframerate())
            print("0x{0:X}".format(f.getnframes()))
            
            
            C = f.readframes(f.getnframes())
            Z_FRAMERATE = f.getframerate()
            
            
        print(len(C))
        
        LEN = len(C)
    
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

        BINARIES.append(bytes(W))
        LENGTHS.append(len(bytes(W)))
    
    
    B = b''
    B += b'\x8A\x41\x47\x02\x43' + b'SmplDrm1        ' + b'\x00'
    
    K = 0x23   # Incrementing counter. Probably can be anything??
    
    for U in range(128):
        if U in STRUCT:
            B += struct.pack("<HHHHHHHHHBBBB", 0x80+K, 0x7F, 0x80+K, 0x7F, 0x80+K, 0x7F, 0x80+K, 0x7F, 0, 0xC8, 0x40, 0, 0x20)
            K += 1
        else:
            B += struct.pack("<HHHHHHHHHBBBB", 0, 0x7F, 0, 0x7F, 0, 0x7F, 0, 0x7F, 0, 0x7F, 0x40, 0, 0x60)
    
    B += b'\x40\x40\x40\x80\x4A\x40\x40\x40\x40\x80\x40\x40\x00\x00'
    
    for U in range(128):
        if U in STRUCT:
            SAMPLE_IDX = FILES.index(STRUCT[U])
            B += bytes.fromhex("00 D8 00 20 00 00 00 20 00 00 00 20 00 00 01 00 80 3F 00 00 80 3F FF 03 80 3E 40 00 00 00 FF 01 00 00 64 00 00 00 20 03 00 00 20 03") + struct.pack("<H", 0x80+SAMPLE_IDX) + bytes.fromhex("00 7F 02 00 02 7F 00 7F 01 00")
        else:
            B += bytes.fromhex("00 00 00 20 00 00 00 20 00 00 00 20 00 00 01 00 80 3F 00 00 80 3F FF 03 80 3E 40 00 00 00 FF 01 00 00 64 00 00 00 20 03 00 00 20 03") + struct.pack("<H", 0)  + bytes.fromhex("00 7F 02 00 02 7F 00 7F 01 00")
    
    for U in range(8):
        if U < len(FILES):
            LEN = LENGTHS[U]
        else:
            LEN = 0x5270   # Probably can be anything?
            
        B += bytes.fromhex("00 E8 00 20 00 00 00 20 00 00 00 00 00 00 00 00 00 00 22 00 00 00 00 00 00 00 22 00 00 00 00 00 00 00 22 00 00 00 00 00 00 00 22 00 00 00 00 00") + \
                      struct.pack("<H", LEN-0x28) + \
                      bytes.fromhex("00 00 00 00 02 00 00 ") + \
                      struct.pack("<H", LEN-0x18) + b'\x00' + \
                      struct.pack("<H", LEN-0x08) + \
                      bytes.fromhex("00 00 00 00 02 00 A1 53 3C 02 80 00 00 00")

    for BB in BINARIES:
        B += BB

    with open("1.dw7", "wb") as f:
        f.write(b"DW7FCTK-4400")
        f.write(struct.pack("<II", len(B), 0)
        for U in range(64):
            if U < len(LENGTHS):
                f.write(struct.pack("<I", LENGTHS[U]))
            else:
                f.write(struct.pack("<I", 0))
        f.write(B)



if __name__=="__main__":
  
    S = {60: {'file': "S1.wav", 'pitch_shift': -20}}
  
  
    wav_to_dw7(S)
