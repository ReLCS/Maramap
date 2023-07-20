import socket
import argparse
import json
import re
from socket import gethostname
from bs4 import BeautifulSoup
import ipinfo
import pyasn
from flask import Flask, request, render_template
from collections import OrderedDict
from reversedns import *
asndb = pyasn.pyasn('static/asnum.dat')
access_token = 'dab5ee35a6b59c'
handler = ipinfo.getHandler(access_token)

def getData(ipadr):
    ipaddressinfo = {}
    asnum = asndb.lookup(ipadr)[0]
    ipaddressinfo['asnum'] = asnum
    try:
        a = socket.gethostbyaddr(ipadr)[0]
        ipaddressinfo['hostname'] = a
        b = findRegexAndPlan(a)
        ipaddressinfo['coordinates'] = b[0]+','+b[1]
        ipaddressinfo['method'] = 'regex'
        ipaddressinfo['ip'] = ipadr
        return ipaddressinfo
    except Exception as e: 
        print(e)
        try: 
            details = handler.getDetails(ipadr)
            ipaddressinfo['coordinates'] = details.loc
            ipaddressinfo['method'] = 'ipinfo'
            ipaddressinfo['ip'] = ipadr
            return ipaddressinfo
        except: 
            return "unable to get data"

for i in range(10):
    print(i)
    if i == 0:
        f = open('static/RIPE-Atlas-measurement-44104396.json')
    if i == 1:
        f = open('static/RIPE-Atlas-measurement-44104397.json')
    if i == 2:
        f = open('static/RIPE-Atlas-measurement-44104399.json')
    if i == 3:
        f = open('static/RIPE-Atlas-measurement-44104400.json')
    if i == 4:
        f = open('static/RIPE-Atlas-measurement-44104401.json')
    if i == 5:
        f = open('static/RIPE-Atlas-measurement-44104402.json')
    if i == 6:
        f = open('static/RIPE-Atlas-measurement-44104404.json')
    if i == 7:
        f = open('static/RIPE-Atlas-measurement-44104405.json')
    if i == 8:
        f = open('static/RIPE-Atlas-measurement-44104406.json')
    if i == 9:
        f = open('static/RIPE-Atlas-measurement-44104407.json')
        
    traceroutes = json.load(f)

    for tracert in traceroutes:
        try:
            ip = (((tracert['result'][-2])['result'][0])['from'])
            info = getData(ip)
            print(info)
        except:
            print("error")
    
    f.close()