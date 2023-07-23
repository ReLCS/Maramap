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
from util import *
asndb = pyasn.pyasn('static/asnum.dat')

access_token = 'dab5ee35a6b59c'
handler = ipinfo.getHandler(access_token)

app = Flask(__name__)
@app.route('/')
def hello():
    return render_template("mapdisplay.html")


# def finalLocation(ipaddress):
#     a = socket.gethostbyaddr(ipaddress)[0]
#     print(a)
#     b = findRegexAndPlan(a)
#     return(b)
# a = finalLocation('176.58.90.161')
# print(a)

# x = readNodes('static/midar-iff.nodes')[0]
x = readNodes('test.nodes.txt')[0]


@app.route('/getip',methods = ['POST', 'GET'])
def postRequest():

    ips = (request.form['ipaddress']).split(',')
    print(request.form['ipaddress'])

    data = {}
    

    for ipadr in ips:
        
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
            data[ipadr] = ipaddressinfo
        except Exception as e: 
            print(e)
            try: 
                details = handler.getDetails(ipadr)
                ipaddressinfo['coordinates'] = details.loc
                ipaddressinfo['method'] = 'ipinfo'
                ipaddressinfo['ip'] = ipadr
                data[ipadr] = ipaddressinfo
            except Exception as e: 
                print(e)
        try:
            nodeid = determineNodeOfIP(ipadr,x)
            ipaddressinfo['nodeid'] = nodeid
        except Exception as e:
            print(e)

    print("____________________________")
    print(json.dumps(data))
    return json.dumps(data)
    
if __name__ == '__main__':
    app.run()