import time
import subprocess
import sys
from time import gmtime, strftime
import pandas as pd
import traceback
import os

try:
    print(strftime("[%H:%M:%S]")+" Start Bot")
except:
    print(f'Error Start Bot')
    time.sleep(10)
    sys.exit()
os.system('cls' if os.name == 'nt' else 'clear')
try:
    subprocess.Popen(f'py index.py ', shell=True)
    time.sleep(0.5)
    time.sleep(999999)
except:
    traceback.print_exc()
    time.sleep(10)