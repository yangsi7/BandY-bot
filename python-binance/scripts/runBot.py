#!/usr/bin/python3
from binance.client import Client
from datetime import datetime
import sys
import subprocess
import sys
from datetime import datetime
sys.path.append('/Users/yangsi/Box Sync/Crypto/scripts/python-binance/scripts')

import subprocess

def main():
    command = './runYangiBot.py > log.log'
    while True:
        now = datetime. now()
        dt_string = now. strftime("%d%m%Y-%H%M%S")
        command = './runYangiBot.py > YanginoBot.log.' + dt_string
        p = execute(command)
    
        if p != 0:
            continue
        else:
            break

def execute(command):
    p = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    return p

if __name__ == "__main__":
    main()
