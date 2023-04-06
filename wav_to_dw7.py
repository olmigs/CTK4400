
import struct
import wave
import pathlib
import numpy
import scipy
import scipy.signal



def wav_to_dw7(STRUCT, OUTPUT : pathlib.Path, SLOT : int = 1):


    if SLOT not in (1, 2, 3):
        raise Exception("SLOT needs to be in 1 - 3")


    S = set()
    for KEY in STRUCT:
        X = STRUCT[KEY].get('file', None)
        if X is not None:
            S.add(X)
  
    FILES = list(S)
    
    if len(FILES) not in [1,2,3,4,5,6,7,8]:
        raise Exception(f"Need between 1 and 8 distinct file name inputs. Found {len(FILES)} distinct file names.")
    
    LENGTHS = []
    BINARIES = []
    
    TARGET_FREQ = 21410
    
    for FF in FILES:


        with wave.open(str(FF), "rb") as f:
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
            # This is approximately 10s at 21410Hz. It may be worth trying longer than
            # this to see if it works?
            raise Exception(f"Input wave has {LEN} sample points which is too long!")



        BINARIES.append(bytes(W))
        LENGTHS.append(len(bytes(W)))





    """
    What are these? They appear to depend only on the position of the sample (i.e.
    whether it's S1, S2, etc.), and not on the waveform data at all. They may be
    magic numbers, but they may be something else. Note that there are 8 positions
    in a .AL7 file so 8 entries are given here, but only the last 3 are
    available for DW7 content.
    """
    MAGIC_NUMBERS = [
        ( bytes.fromhex("4F 62 0E F6 89"),  bytes.fromhex("E9") ),   # SLOT 1
        ( bytes.fromhex("DB D4 50 97 69"),  bytes.fromhex("EF") ),   # SLOT 2
        ( bytes.fromhex("E9 CE 01 C3 71"),  bytes.fromhex("0E") ),   # SLOT 3
        ( bytes.fromhex("BE 18 B0 0E D4"),  bytes.fromhex("5C") ),   # SLOT 4
        ( bytes.fromhex("E4 B0 31 A1 C2"),  bytes.fromhex("6C") ),   # SLOT 5
        ( bytes.fromhex("8A 41 47 02 43"),  bytes.fromhex("00") ),   # SLOT 6
        ( bytes.fromhex("51 67 47 02 40"),  bytes.fromhex("3F") ),   # SLOT 7
        ( bytes.fromhex("93 AD FF FF 25"),  bytes.fromhex("53") ),   # SLOT 8
    ]


    B = b''

    if SLOT in (1, 2, 3):
        B += MAGIC_NUMBERS[SLOT+5][0] + "SmplDrm{0:d}        ".format(SLOT).encode('latin-1')
        B += MAGIC_NUMBERS[SLOT+5][1]
    else:
        raise Exception

    K = 0x23   # Incrementing counter. Probably can be anything??
    
    for U in range(128):
        if str(U) in STRUCT and STRUCT[str(U)].get('file', None) is not None:
            B += struct.pack("<HHHHHHHHHBBBB", 0x8000+K, 0x7F, 0x8000+K, 0x7F, 0x8000+K, 0x7F, 0x8000+K, 0x7F,  0, min(255, round(200. * numpy.power(10., STRUCT[str(U)].get('vol', 0.0) / 40.)), STRUCT[str(U)].get('pan', 0)+0x40, 0, 0x20)
            K += 1
        else:
            B += struct.pack("<HHHHHHHHHBBBB",    0,   0x7F,    0,   0x7F,    0,   0x7F,    0,   0x7F,  0, 0x7F, 0x40, 0, 0x60)
    
    B += b'\x40\x40\x40\x80\x4A\x40\x40\x40\x40\x80\x40\x40\x00\x00'
    
    for U in range(128):
        if str(U) in STRUCT and STRUCT[str(U)].get('file', None) is not None:
            SAMPLE_IDX = FILES.index(STRUCT[str(U)]['file'])
            PITCH_SHIFT = STRUCT[str(U)]['pitch_shift']
            B += struct.pack("h", int(512.*PITCH_SHIFT)) + bytes.fromhex("00 20 00 00 00 20 00 00 00 20 00 00 01 00 80 3F 00 00 80 3F FF 03 80 3E 40 00 00 00 FF 01 00 00 64 00 00 00 20 03 00 00 20 03") + struct.pack("<H", 0x8000+SAMPLE_IDX) + bytes.fromhex("00 7F 02 00 02 7F 00 7F 01 00")
        else:
            B += struct.pack("h", 0)                     + bytes.fromhex("00 20 00 00 00 20 00 00 00 20 00 00 01 00 80 3F 00 00 80 3F FF 03 80 3E 40 00 00 00 FF 01 00 00 64 00 00 00 20 03 00 00 20 03") + struct.pack("<H", 0)  + bytes.fromhex("00 7F 02 00 02 7F 00 7F 01 00")
    
    for U in range(8):
        if U < len(FILES):
            LEN = LENGTHS[U]
        else:
            LEN = 0x526C   # Probably can be anything?
            
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
    #  pitch_shift:   values from -64 to +63. Units semitones
    #  pan:           values from -64 (full left) to +63 (full right)
    #  vol:           dB values (floating-point) from -92.0 to +4.2. Use -200. as
    #                       the "off" (no sound) setting.
    #
    S = {'60': {'file': "S1.wav", 'pitch_shift': -20, 'pan': -20, 'vol': -20.}}
  
  
    wav_to_dw7(S, "1.dw7")
