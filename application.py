import socket
import argparse
import json
import requests
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

x = readNodes('static/midar-iff.nodes')


# x = readNodes('test.nodes.txt')


@app.route('/getip',methods = ['POST', 'GET'])
def postRequest():

    allips = json.loads(request.form['ipaddress'])
    print(allips)

    finaldata = {}

    for tracert in allips:

        data = {}
        index = 0

        for ipadr in allips[tracert]:
            
            ipaddressinfo = {}
            asnum = asndb.lookup(ipadr)[0]
            ipaddressinfo['tracertnum'] = str(int(tracert)+1)
            ipaddressinfo['asnum'] = asnum
            ipaddressinfo['latency'] = allips[tracert][ipadr]
            ipaddressinfo['ip'] = ipadr
            try:
                a = socket.gethostbyaddr(ipadr)[0]
                ipaddressinfo['hostname'] = a
                b = findRegexAndPlan(a)
                ipaddressinfo['coordinates'] = b[0]+','+b[1]
                ipaddressinfo['method'] = 'regex'
                data[str(index)] = ipaddressinfo
            except Exception as e: 
                print(e)
                ipaddressinfo['hostname'] = 'no hostname'
                try:
                    ripeinfo = (requests.get('https://ipmap-api.ripe.net/v1/locate/all?resources=' + ipadr)).json()
                    ipaddressinfo['coordinates'] = str(ripeinfo['data'][ipadr]['latitude']) + ',' + str(ripeinfo['data'][ipadr]['longitude'])
                    ipaddressinfo['method'] = 'ripe ip map'
                    data[str(index)] = ipaddressinfo
                except Exception as e:
                    print(e)
                    try: 
                        details = handler.getDetails(ipadr)
                        ipaddressinfo['coordinates'] = details.loc
                        ipaddressinfo['method'] = 'ipinfo'
                        data[str(index)] = ipaddressinfo
                    except Exception as e: 
                        print(e)

            try:
                nodeid = determineNodeOfIP(ipadr,x)
                ipaddressinfo['nodeid'] = nodeid
            except Exception as e:
                print(e)
            index = index + 1
        
        finaldata[tracert] = data

    print("____________________________")
    print(json.dumps(finaldata))
    return json.dumps(finaldata)

    # return '{"0": {"0": {"tracertnum": "1", "asnum": 30263, "latency": "0.42533333333333334", "ip": "216.7.112.25", "hostname": "no hostname", "coordinates": "42.2249,-121.7817", "method": "ipinfo", "nodeid": 29936}, "1": {"tracertnum": "1", "asnum": 30263, "latency": "0.6886666666666666", "ip": "216.7.112.241", "hostname": "no hostname", "coordinates": "42.2249,-121.7817", "method": "ipinfo", "nodeid": 29936}, "2": {"tracertnum": "1", "asnum": 133090, "latency": "1.0936666666666668", "ip": "27.123.21.90", "hostname": "no hostname", "coordinates": "-36.8485,174.7635", "method": "ipinfo", "nodeid": 6171}}, "1": {"0": {"tracertnum": "2", "asnum": 30263, "latency": "3.985333333333333", "ip": "216.7.112.241", "hostname": "no hostname", "coordinates": "42.2249,-121.7817", "method": "ipinfo", "nodeid": 29936}, "1": {"tracertnum": "2", "asnum": 37027, "latency": "4.49", "ip": "196.202.168.177", "hostname": "no hostname", "coordinates": "-1.2833,36.8167", "method": "ipinfo", "nodeid": 4562}, "2": {"tracertnum": "2", "asnum": 15399, "latency": "4.406333333333333", "ip": "197.211.11.209", "hostname": "no hostname", "coordinates": "-1.2833,36.8167", "method": "ipinfo", "nodeid": 4562}, "3": {"tracertnum": "2", "asnum": 4837, "latency": "3.439", "ip": "60.218.50.154", "hostname": "no hostname", "coordinates": "45.7500,126.6500", "method": "ipinfo", "nodeid": 5012}, "4": {"tracertnum": "2", "asnum": 4837, "latency": "6.6463333333333345", "ip": "61.168.239.126", "hostname": "no hostname", "coordinates": "34.7578,113.6486", "method": "ipinfo", "nodeid": 5099}, "5": {"tracertnum": "2", "asnum": 7679, "latency": "4.257333333333333", "ip": "61.203.193.121", "hostname": "no hostname", "coordinates": "35.6895,139.6917", "method": "ipinfo", "nodeid": 5152}, "6": {"tracertnum": "2", "asnum": 2497, "latency": "5.166666666666667", "ip": "210.138.70.62", "hostname": "no hostname", "coordinates": "35.6895,139.6917", "method": "ipinfo", "nodeid": 5152}, "7": {"tracertnum": "2", "asnum": 7679, "latency": "3.5229999999999997", "ip": "61.203.192.45", "hostname": "no hostname", "coordinates": "33.6000,130.4167", "method": "ipinfo", "nodeid": 5152}, "8": {"tracertnum": "2", "asnum": 7922, "latency": "3.983333333333333", "ip": "96.110.38.109", "hostname": "no hostname", "coordinates": "39.7392,-104.9847", "method": "ipinfo", "nodeid": 5419}, "9": {"tracertnum": "2", "asnum": 16097, "latency": "5.666666666666667", "ip": "109.104.59.180", "hostname": "no hostname", "coordinates": "52.52437,13.41053", "method": "ripe ip map", "nodeid": 5459}, "10": {"tracertnum": "2", "asnum": 18101, "latency": "6.377666666666666", "ip": "124.124.65.126", "hostname": "no hostname", "coordinates": "19.0728,72.8826", "method": "ipinfo", "nodeid": 5563}, "11": {"tracertnum": "2", "asnum": 4837, "latency": "205.37533333333332", "ip": "121.31.0.186", "hostname": "no hostname", "coordinates": "22.8167,108.3167", "method": "ipinfo", "nodeid": 5612}, "12": {"tracertnum": "2", "asnum": 4837, "latency": "205.67499999999998", "ip": "121.31.0.26", "hostname": "no hostname", "coordinates": "22.8167,108.3167", "method": "ipinfo", "nodeid": 5612}, "13": {"tracertnum": "2", "asnum": 7473, "latency": "249.00900000000001", "ip": "203.208.151.94", "hostname": "no hostname", "coordinates": "22.54554,114.0683", "method": "ripe ip map", "nodeid": 5689}}, "2": {"0": {"tracertnum": "3", "asnum": 7473, "latency": "0.723", "ip": "203.208.173.45", "hostname": "no hostname", "coordinates": "22.54554,114.0683", "method": "ripe ip map", "nodeid": 5689}, "1": {"tracertnum": "3", "asnum": 2914, "latency": "9.843333333333334", "ip": "129.250.66.154", "hostname": "no hostname", "coordinates": "22.54554,114.0683", "method": "ripe ip map", "nodeid": 5689}, "2": {"tracertnum": "3", "asnum": 58541, "latency": "9.798333333333332", "ip": "150.138.161.174", "hostname": "no hostname", "coordinates": "36.0649,120.3804", "method": "ipinfo", "nodeid": 5707}, "3": {"tracertnum": "3", "asnum": 53785, "latency": "21.80333333333333", "ip": "152.13.222.1", "hostname": "no hostname", "coordinates": "36.0726,-79.7920", "method": "ipinfo", "nodeid": 5724}, "4": {"tracertnum": "3", "asnum": 9808, "latency": "38.46966666666666", "ip": "221.183.95.58", "hostname": "no hostname", "coordinates": "39.9075,116.3972", "method": "ipinfo", "nodeid": 5919}, "5": {"tracertnum": "3", "asnum": 25899, "latency": "98.14166666666667", "ip": "206.192.251.228", "hostname": "no hostname", "coordinates": "47.60621,-122.33207", "method": "ripe ip map", "nodeid": 6020}, "6": {"tracertnum": "3", "asnum": 4134, "latency": "93.38366666666667", "ip": "14.148.55.78", "hostname": "no hostname", "coordinates": "22.5455,114.0683", "method": "ipinfo", "nodeid": 6113}}}'
   
   
   
    # ips = (request.form['ipaddress']).split(',')
    # print(request.form['ipaddress'])

    # data = {}
    

    # for ipadr in ips:
        
    #     ipaddressinfo = {}
    #     asnum = asndb.lookup(ipadr)[0]
    #     ipaddressinfo['asnum'] = asnum
    #     try:
    #         a = socket.gethostbyaddr(ipadr)[0]
    #         ipaddressinfo['hostname'] = a
    #         b = findRegexAndPlan(a)
    #         ipaddressinfo['coordinates'] = b[0]+','+b[1]
    #         ipaddressinfo['method'] = 'regex'
    #         ipaddressinfo['ip'] = ipadr
    #         data[ipadr] = ipaddressinfo
    #     except Exception as e: 
    #         print(e)
    #         try: 
    #             details = handler.getDetails(ipadr)
    #             ipaddressinfo['coordinates'] = details.loc
    #             ipaddressinfo['method'] = 'ipinfo'
    #             ipaddressinfo['ip'] = ipadr
    #             data[ipadr] = ipaddressinfo
    #         except Exception as e: 
    #             print(e)
    #     try:
    #         nodeid = determineNodeOfIP(ipadr,x)
    #         ipaddressinfo['nodeid'] = nodeid
    #     except Exception as e:
    #         print(e)

    # print("____________________________")
    # print(json.dumps(data))
    # return json.dumps(data)
    
if __name__ == '__main__':
    app.run()
    # app.run()