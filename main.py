# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 12:25:26 2022

@author: Nathan Woodburn
"""

#change this KEY
apikey = 'API KEY'

#Network port is 12039 for mainnet and 14039
networkport = '12039'

# Delay to check for new names in Bob (in minutes)
checknames = 10

# Delay to check for expired names using webhook block (in minutes)
checkexpiration = 1

#HSD Name (default bob.exe) Linux is usually `hsd` note no caps
hsdname = 'bob.exe'


# Blocks before exipation to alert user
expblock = 2000

# Linux command to run on name expiry alert. This is where you can use
# any email, sms or other method to alert the user
script = "./alert.sh"

# Import needed stuff
import requests
import subprocess
import time
import os
import sys

# Get current OS
import platform
osname = platform.system()

# Get cli args

# Runs program once if cli passed
cli = False
# You can pass the api key and settings through cli args
i = 0
for arg in sys.argv:
    if (i == 1):
        cli = True
        apikey = arg
    if (i == 2):
        networkport = arg
    if (i == 3):
        expblock = int(arg)
    i+=1


def process_exists(process_name):
    '''
    Check whether the process is running

    Parameters
    ----------
    process_name : string
        Process Name to check

    Returns
    -------
    bool
        Whether process exists

    '''
    # Get the operating system
    global osname
    
    #Either check via windows or linux commands
    if (osname == "Windows"):
        call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
        # use buildin check_output right away
        output = subprocess.check_output(call).decode()
        # check in last line for process name
        last_line = output.strip().split('\r\n')[-1]
        # because Fail message could be translated
        return last_line.lower().startswith(process_name.lower())
    if (osname == "Linux"):
        tmp = os.popen("ps a -Af").read()
        proccount = tmp.count(process_name)
        
        if proccount > 0:
            return True
        else:
            return False
    return False

def getnextexp():
    if not process_exists(hsdname):
        print("HSD not running")
        return
    global nextexp
    global nextexpblock
    r = requests.get('http://x:'+apikey+'@127.0.0.1:'+networkport+'/wallet')
    wallets = r.json()
    
    names = []
    for wallet in wallets:
        r = requests.get('http://x:'+apikey+'@127.0.0.1:'+networkport+'/wallet/'+wallet+'/name?own=true')
        names.extend(r.json())
        
    
    for name in names:
        if ("renewalPeriodEnd" in name["stats"]):
            if(name["stats"]["renewalPeriodEnd"] < nextexpblock or nextexpblock == 0):
               nextexpblock = name["stats"]["renewalPeriodEnd"]
               nextexp = name["name"]
               
    

def checkexp():
    r = requests.get('https://api.handshakeapi.com/hsd')
    api = r.json()
    block = api["chain"]["height"]
    
    global nextexpblock
    global nextexp
    print(nextexp,"will expire in",nextexpblock-block,"blocks")
    print("Current block",block)
    if block > nextexpblock - expblock and not cli:
        global osname
        if (osname == "Windows"):
            # from win10toast import ToastNotifier
            time = (nextexpblock-block)/144
            
            from plyer import notification
            notification.notify(
            title = "HNS Alarm",
            message = nextexp+" will expire in "+str(nextexpblock-block)+" blocks (~"+str(round(time))+" days)!\nPlease renew it in Bob/HSD",
            timeout = 10
            )
            return
        if (osname == "Linux"):
           os.system(script)
           return
        
        print("Sorry we don\'t currently support",osname)
    




nextexp = ''
nextexpblock = 0
getnextexp()
print("Next name to expire",nextexp)
print("Expiry block",nextexpblock)
if (nextexpblock != 0):
    checkexp()

timenew = -1
timeexp = -1

# Time between loops
timeloop = 1

while not cli:
    timenew += timeloop
    timeexp += timeloop
    if timenew >= checknames*60:
        getnextexp()
        print(nextexp)
        print(nextexpblock)
        
    if timeexp >= checkexpiration*60:
        if (nextexpblock != 0):
            checkexp()
        
        
    time.sleep(timeloop)