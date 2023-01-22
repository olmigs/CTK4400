
import struct
import wave
import pathlib
import numpy
import scipy
import scipy.signal



def wav_to_dw7(STRUCT, OUTPUT : pathlib.Path):
  
    S = set()
    for KEY in STRUCT:
        S.add(STRUCT[KEY]['file'])
  
    FILES = list(S)
    
    if len(FILES) not in [1,2,3,4,5,6,7,8]:
        raise Exception(f"Need between 1 and 8 distinct file name inputs. Found {len(FILES)} distinct file names.")
    
    LENGTHS = []
    BINARIES = []
    
    TARGET_FREQ = 22050
    
    for FF in FILES:
        
        with wave.open(str(FF), "rb") as f:
            print(f.getsampwidth())
            print(f.getframerate())
            print("0x{0:X}".format(f.getnframes()))
            
            
            C = f.readframes(f.getnframes())
            Z_FRAMERATE = f.getframerate()
            
            
        print(len(C))
        
        LEN = len(C)
    
        Z = (numpy.frombuffer(C, dtype=numpy.uint8) - 128).astype(numpy.int8)   # zero-positioned
    
    
        if Z_FRAMERATE == TARGET_FREQ:
            W = (Z + 0).astype(numpy.uint8)
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

            W = (V + 0).astype(numpy.uint8)

        print(W)
        print(max(W))
        print(min(W))

        BINARIES.append(bytes(W))
        LENGTHS.append(len(bytes(W)))
    
    
    B = b''
    B += b'\x8A\x41\x47\x02\x43' + b'SmplDrm1        ' + b'\x00'
    
    K = 0x23   # Incrementing counter. Probably can be anything??
    
    for U in range(128):
        if str(U) in STRUCT:
            B += struct.pack("<HHHHHHHHHBBBB", 0x80+K, 0x7F, 0x80+K, 0x7F, 0x80+K, 0x7F, 0x80+K, 0x7F,  0, 0xC8, 0x40, 0, 0x20)
            K += 1
        else:
            B += struct.pack("<HHHHHHHHHBBBB",    0,   0x7F,    0,   0x7F,    0,   0x7F,    0,   0x7F,  0, 0x7F, 0x40, 0, 0x60)
    
    B += b'\x40\x40\x40\x80\x4A\x40\x40\x40\x40\x80\x40\x40\x00\x00'
    
    for U in range(128):
        if str(U) in STRUCT:
            SAMPLE_IDX = FILES.index(STRUCT[str(U)]['file'])
            PITCH_SHIFT = STRUCT[str(U)]['pitch_shift']
            B += struct.pack("2b", 0, int(2.*PITCH_SHIFT)) + bytes.fromhex("00 20 00 00 00 20 00 00 00 20 00 00 01 00 80 3F 00 00 80 3F FF 03 80 3E 40 00 00 00 FF 01 00 00 64 00 00 00 20 03 00 00 20 03") + struct.pack("<H", 0x80+SAMPLE_IDX) + bytes.fromhex("00 7F 02 00 02 7F 00 7F 01 00")
        else:
            B += struct.pack("2b", 0, 0)                   + bytes.fromhex("00 20 00 00 00 20 00 00 00 20 00 00 01 00 80 3F 00 00 80 3F FF 03 80 3E 40 00 00 00 FF 01 00 00 64 00 00 00 20 03 00 00 20 03") + struct.pack("<H", 0)  + bytes.fromhex("00 7F 02 00 02 7F 00 7F 01 00")
    
    for U in range(8):
        if U < len(FILES):
            LEN = LENGTHS[U]
        else:
            LEN = 0x5270   # Probably can be anything?
            
        B += bytes.fromhex("00 E8 00 20 00 00 00 20 00 00 00 00 00 00 00 00 00 00 22 00 00 00 00 00 00 00 22 00 00 00 00 00 00 00 22 00 00 00 00 00 00 00 22 00 00 00 00 00") + \
                      struct.pack("<I", LEN-0x28) + \
                      bytes.fromhex("00 00 02 00 00 ") + \
                      struct.pack("<I", LEN-0x18)[:3] + \
                      struct.pack("<I", LEN-0x08) + \
                      bytes.fromhex("00 00 02 00 A1 53 3C 02 80 00 00 00")

    for BB in BINARIES:
        B += BB

    with open(str(OUTPUT), "wb") as f:
        f.write(b"DW7FCTK-4400")
        f.write(struct.pack("<II", len(B), 0))
        for U in range(64):
            if U < len(LENGTHS):
                f.write(struct.pack("<I", LENGTHS[U]))
            else:
                f.write(struct.pack("<I", 0))
        f.write(B)



if __name__=="__main__":
  
    # A dictionary of key values mapped to sounds.
    #
    #  Key:   MIDI pitch of the key which produces the sound. (E.g. 60 is the
    #                Middle C key).
    #  file:  File name, relative to current working directory. Up to 8 distinct
    #                file names are accepted.
    #  pitch_shift:   values from -64 to +63. Units possibly semitones?
    #
    S = {'60': {'file': "S1.wav", 'pitch_shift': -20}}
  
  
    wav_to_dw7(S, "1.dw7")
