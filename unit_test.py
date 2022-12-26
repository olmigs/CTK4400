


import os
import shutil
import pathlib
import tempfile
import subprocess
import json

from tw7_to_wav import tw7_to_wav
from dw7_to_wav import dw7_to_wav
from wav_to_tw7 import wav_to_tw7
from wav_to_dw7 import wav_to_dw7


def compare_files(F1 : pathlib.Path, F2 : pathlib.Path):
    # Using hexdump comparison
    
    DIR = tempfile.mkdtemp()

    
    with open(pathlib.Path(DIR, "1.hex"), "w") as f1:
        subprocess.run(['hexdump', '-C', F1], stdout = f1)
    with open(pathlib.Path(DIR, "2.hex"), "w") as f2:
        subprocess.run(['hexdump', '-C', F2], stdout = f2)
    
    subprocess.run(['meld', pathlib.Path(DIR, "1.hex"), pathlib.Path(DIR, "2.hex")])
    




# Clean the output directory

shutil.rmtree("Wav")
os.mkdir("Wav")





# Do the first one

tw7_to_wav("S1_Orgnl.tw7", pathlib.Path("Wav", "S1.wav"))
wav_to_tw7(pathlib.Path("Wav", "S1.wav"), "2.tw7", 1)
compare_files("S1_Orgnl.tw7", "2.tw7")


# Do the second one

tw7_to_wav("S2_Orgnl.tw7", pathlib.Path("Wav", "S2.wav"))
wav_to_tw7(pathlib.Path("Wav", "S2.wav"), "3.tw7", 2)
compare_files("S2_Orgnl.tw7", "3.tw7")


# Do the third one

tw7_to_wav(pathlib.Path("Batch 2", "S2_Orgnl.tw7"), pathlib.Path("Wav", "S2_2.wav"))
wav_to_tw7(pathlib.Path("Wav", "S2_2.wav"), "4.tw7", 2)
compare_files(pathlib.Path("Batch 2", "S2_Orgnl.tw7"), "4.tw7")


# Do drums

dw7_to_wav(pathlib.Path("Batch 3", "Sample Drum Kit Pitch test.dw7"), pathlib.Path("Wav", "DW.wav"))
with open("drums.json", "r") as f5:
    J = json.load(f5)
wav_to_dw7(J, "5.dw7")
compare_files(pathlib.Path("Batch 3", "Sample Drum Kit Pitch test.dw7"), "5.dw7")
