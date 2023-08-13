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
import ipaddress
asndb = pyasn.pyasn('static/asnum.dat')

# access_token = '97da130c7c5c32'
# handler = ipinfo.getHandler(access_token)

r = redis.Redis(host='localhost', port=6379, db=0)

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


    info = json.loads(request.form['ipaddress'])

    allips = {}

    n = 0

    for trace in info: 
        iplist, rttlist = list((info[trace]).keys()), list((info[trace]).values())[1:] 

        if len(iplist) != 0 and len(rttlist) != 0:

            traceips = {iplist[0]: 'first'}

            del iplist[0]

            print(iplist)
            print(rttlist)

            i = 0
            lastvalidrtt = 0.0

            for ip in iplist:
                

                currentrtt = float(rttlist[i])
                # lastrtt = int(rttlist[i-1])
                latency = (currentrtt-lastvalidrtt)/2
                print('-------')
                print(ip)
                print(lastvalidrtt)
                print(currentrtt)
                print(latency)
                
                if latency>0.0 or abs(latency)<(0.1*lastvalidrtt) or i == 0:
                    # print('yay')
                    lastvalidrtt = currentrtt
                    traceips[ip] = latency
                else:
                    i += 1
                    continue

                i += 1

            
            allips[n] = traceips
            n += 1

 

#     orignial_hops=[ xx,  xx ,x ]

# latency=(RTT[i]-RTT[i-1])/2
# If (latency<0) && (latency>0.1*RTT[i-1])
# 	Skip hop i
# 	Replace hop i with hop i+1


    # allips = json.loads(request.form['ipaddress'])
    print(allips)

    finaldata = {}

    tracertindex = 0

    for tracert in allips:

        data = {}
        noskipindex = 0
        index = 0
        missingHops = False

        for ipadr in allips[tracert]:
            noskipindex += 1

            # print('----')
            # print(ipadr)

            ipaddressinfo = getIPInfo(ipadr)

            if ipaddressinfo != False:
                lasthop = False
                if noskipindex == len(allips[tracert]):
                    lasthop = True

                ipaddressinfo['latency'] = allips[tracert][ipadr]

                if index == 0:
                    ipaddressinfo['predictedlatency'] = 'first'

                elif previouscoords != False:
                    ipaddressinfo['predictedlatency'] = calculate_latency(float(ipaddressinfo['coordinates'].split(',')[0]),float(ipaddressinfo['coordinates'].split(',')[1]),float(previouscoords.split(',')[0]),float(previouscoords.split(',')[1]))
                    # print(ipaddressinfo['predictedlatency'])
                    # print(ipaddressinfo['latency'])
                    if ipaddressinfo['method'] == 'ipinfo':
                        ipaddressinfo['hostname'] = 'not available'

                    if ipaddressinfo['predictedlatency'] != 0.0:
                        if 1.1*float(ipaddressinfo['latency']) < ipaddressinfo['predictedlatency']:
                            # print('yes')
                            if ipaddressinfo['method'] == 'regex':
                                hostname = ipaddressinfo['hostname']
                                ripeinfo = getFromRipe(ipadr)
                                ipaddressinfo = ripeinfo
                                if ipaddressinfo != 'X':
                                    ipaddressinfo['hostname'] = hostname
                                    ipaddressinfo['latency'] = allips[tracert][ipadr]
                                    ipaddressinfo['predictedlatency'] = calculate_latency(float(ipaddressinfo['coordinates'].split(',')[0]),float(ipaddressinfo['coordinates'].split(',')[1]),float(previouscoords.split(',')[0]),float(previouscoords.split(',')[1]))

                                if ipaddressinfo == 'X' or 1.1*float(ipaddressinfo['latency']) < ipaddressinfo['predictedlatency']:
                                    ipinfo = getFromIPInfo(ipadr)
                                    ipaddressinfo = ipinfo
                                    if ipaddressinfo != 'X':
                                        ipaddressinfo['hostname'] = hostname
                                        ipaddressinfo['latency'] = allips[tracert][ipadr]
                                        ipaddressinfo['predictedlatency'] = calculate_latency(float(ipaddressinfo['coordinates'].split(',')[0]),float(ipaddressinfo['coordinates'].split(',')[1]),float(previouscoords.split(',')[0]),float(previouscoords.split(',')[1]))
                                    if ipaddressinfo == 'X' or 1.5*float(ipaddressinfo['latency']) < ipaddressinfo['predictedlatency']:
                                        previouscoords = False
                                        missingHops = True
                                        break
                                    r.set(ipadr, json.dumps(ipinfo))
                                    r.expire(ipadr, 86400)
                                
                                r.set(ipadr, json.dumps(ripeinfo))
                                r.expire(ipadr, 86400)

                            elif ipaddressinfo['method'] == 'ripe ip map':
                                ipinfo = getFromIPInfo(ipadr)
                                ipaddressinfo = ipinfo

                                if ipaddressinfo != 'X':
                                    ipaddressinfo['hostname'] = 'n/a'
                                    ipaddressinfo['latency'] = allips[tracert][ipadr]
                                    ipaddressinfo['predictedlatency'] = calculate_latency(float(ipaddressinfo['coordinates'].split(',')[0]),float(ipaddressinfo['coordinates'].split(',')[1]),float(previouscoords.split(',')[0]),float(previouscoords.split(',')[1]))
                                if ipaddressinfo == 'X' or 1.1*float(ipaddressinfo['latency']) < ipaddressinfo['predictedlatency']:
                                    previouscoords = False
                                    missingHops = True
                                    break
                            
                                r.set(ipadr, json.dumps(ipinfo))
                                r.expire(ipadr, 86400)
                            elif ipaddressinfo['method'] == 'ipinfo':
                                previouscoords = False
                                missingHops = True
                                break


                else: 
                    missingHops = True
                    break


                ipaddressinfo['ip'] = ipadr
                ipaddressinfo['tracertnum'] = str(int(tracertindex)+1)
                ipaddressinfo['asnum'] = asndb.lookup(ipadr)[0]


                # ipaddressinfo['inarea'] = True

                36.764608, -70.848102/43.094246, -70.117774/44.039477, -87.935092/36.770450, -90.955393
                lat,lng = float(ipaddressinfo['coordinates'].split(',')[0]), float(ipaddressinfo['coordinates'].split(',')[1])

                print(lat,lng)

                ipaddressinfo['inarea'] = True

                # if lat > 36.764608 and lat < 44.039477 and lng > - 80 and lng <-70:
                #     ipaddressinfo['inarea'] = True


                # if lasthop == True:
                #     ipaddressinfo['lasthop'] = True
                # else:
                #     ipaddressinfo['lasthop'] = False


                try:
                    nodeid = determineNodeOfIP(ipadr,x)
                    ipaddressinfo['nodeid'] = nodeid
                    # print('found node')
                except Exception as e:
                    # print('could not find node')
                    ipaddressinfo['nodeid'] = ipadr




                data[str(index)] = ipaddressinfo

                # print(ipaddressinfo)

                previouscoords = ipaddressinfo['coordinates']

                index += 1
            else:
                previouscoords = False



        if missingHops == False:

            # inarealist = []

            # for index in data:
            #     inarealist.append(data[index]['inarea'])

            # print(inarealist)

            # if False in inarealist:
            #     continue
            # else:
            #     finaldata[tracertindex] = data
            #     tracertindex += 1

            finaldata[tracertindex] = data
            tracertindex += 1

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
    # app.run(debug = True, port = 6000)