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
import redis
import time
asndb = pyasn.pyasn('static/asnum.dat')

# access_token = '97da130c7c5c32'
# handler = ipinfo.getHandler(access_token)

# r = redis.Redis(host='localhost', port=6379, db=0)

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



@app.route('/getip',methods = ['POST', 'GET'])
def postRequest():

    allips = json.loads(request.form['ipaddress'])
    print(allips)

    finaldata = {}

    for tracert in allips:

        data = {}
        index = 0

        for ipadr in allips[tracert]:

            print('----')
            print(ipadr)


            ipaddressinfo = getIPInfo(ipadr)

            if ipaddressinfo != False:
                try:
                    nodeid = determineNodeOfIP(ipadr,x)
                    ipaddressinfo['nodeid'] = nodeid
                    
                    ipaddressinfo['ip'] = ipadr
                    ipaddressinfo['latency'] = allips[tracert][ipadr]
                    ipaddressinfo['tracertnum'] = str(int(tracert)+1)
                    ipaddressinfo['asnum'] = asndb.lookup(ipadr)[0]

                    data[str(index)] = ipaddressinfo

                    print(ipaddressinfo)

                    index += 1
                    # print('found node')
                except Exception as e:
                    # print('could not find node')
                    print('node not found')



            # print('-----')

            # print(ipadr)
            
            # ipaddressinfo = {'ip': ipadr, 'tracertnum': str(int(tracert)+1), 'latency': allips[tracert][ipadr]}




            # #find as num
            # try: 
            #     asnum = asndb.lookup(ipadr)[0]
            #     ipaddressinfo['asnum'] = asnum
            #     print('asnum found')
            # except Exception as e:    
            #     print('AS Num exception: ' + e)


            # #try to use DNS method
            # try:
            #     host = socket.gethostbyaddr(ipadr)[0]
            #     ipaddressinfo['hostname'] = host
            #     print('hostname found')

            #     try: 
            #         regexCoords = findRegexAndPlan(host)
            #         ipaddressinfo['coordinates'] = regexCoords[0]+','+regexCoords[1]
            #         ipaddressinfo['method'] = 'regex'
            #         data[str(index)] = ipaddressinfo
            #         print('used regex method')
            #         index = index + 1
            #         continue
                
            #     except Exception as e:
            #         print('Could not find regex in hostname')
            #         print(e)

            # except Exception as e:
            #     ipaddressinfo['hostname'] = 'no hostname'
            #     print('Hostname not found ')
            #     print(e)

            
            # #try to use ripe method
            # try:
            #     ripeinfo = (requests.get('https://ipmap-api.ripe.net/v1/locate/all?resources=' + ipadr)).json()
            #     ipaddressinfo['coordinates'] = str(ripeinfo['data'][ipadr]['latitude']) + ',' + str(ripeinfo['data'][ipadr]['longitude'])
            #     ipaddressinfo['method'] = 'ripe ip map'
            #     data[str(index)] = ipaddressinfo
            #     print('used ripe ip map method')
            #     index = index + 1
            #     continue

            # except Exception as e:
            #     print('Ripe IP map did not work')
            #     print(e)


            # #use IPinfo
            # try:
            #     details = handler.getDetails(ipadr)
            #     ipaddressinfo['coordinates'] = details.loc
            #     ipaddressinfo['method'] = 'ipinfo'
            #     data[str(index)] = ipaddressinfo
            #     print('used ipInfo')
            #     index = index + 1
            # except Exception as e:
            #     print('ipinfo did not work ')
            #     print(e)


        
        finaldata[tracert] = data

    print("____________________________")
    print(json.dumps(finaldata))
    return json.dumps(finaldata)

   
   
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
    # app.run(debug = True, port = 8001)