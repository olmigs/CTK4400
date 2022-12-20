


import os
import shutil
import pathlib
import tempfile

from tw7_to_wav import tw7_to_wav
from wav_to_tw7 import wav_to_tw7


def compare_files(F1 : pathlib.Path, F2 : pathlib.Path):
    # Using hexdump comparison
    
    DIR = tempfile.mkdtemp()

    os.system('hexdump -C {0} > {1}'.format(str(F1), os.path.join(DIR, "1.hex")))
    os.system('hexdump -C {0} > {1}'.format(str(F2), os.path.join(DIR, "2.hex")))

    os.system('meld {0} {1}'.format(os.path.join(DIR, "1.hex"), os.path.join(DIR, "2.hex")))




# Clean the output directory

shutil.rmtree("Wav")
os.mkdir("Wav")





# Do the first one

tw7_to_wav("S2_Orgnl.tw7", pathlib.Path("Wav", "S2.wav"))
wav_to_tw7(pathlib.Path("Wav", "S2.wav"), "3.tw7")
compare_files("S2_Orgnl.tw7", "3.tw7")
