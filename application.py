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

            print('-----')

            print(ipadr)
            
            ipaddressinfo = {'ip': ipadr, 'tracertnum': str(int(tracert)+1), 'latency': allips[tracert][ipadr]}

            try:
                nodeid = determineNodeOfIP(ipadr,x)
                ipaddressinfo['nodeid'] = nodeid
                print('found node')
            except Exception as e:
                print('could not find node')
                print(e)
                continue


            #find as num
            try: 
                asnum = asndb.lookup(ipadr)[0]
                ipaddressinfo['asnum'] = asnum
                print('asnum found')
            except Exception as e:    
                print('AS Num exception: ' + e)


            #try to use DNS method
            try:
                host = socket.gethostbyaddr(ipadr)[0]
                ipaddressinfo['hostname'] = host
                print('hostname found')

                try: 
                    regexCoords = findRegexAndPlan(host)
                    ipaddressinfo['coordinates'] = regexCoords[0]+','+regexCoords[1]
                    ipaddressinfo['method'] = 'regex'
                    data[str(index)] = ipaddressinfo
                    print('used regex method')
                    index = index + 1
                    continue
                
                except Exception as e:
                    print('Could not find regex in hostname')
                    print(e)

            except Exception as e:
                ipaddressinfo['hostname'] = 'no hostname'
                print('Hostname not found ')
                print(e)

            
            #try to use ripe method
            try:
                ripeinfo = (requests.get('https://ipmap-api.ripe.net/v1/locate/all?resources=' + ipadr)).json()
                ipaddressinfo['coordinates'] = str(ripeinfo['data'][ipadr]['latitude']) + ',' + str(ripeinfo['data'][ipadr]['longitude'])
                ipaddressinfo['method'] = 'ripe ip map'
                data[str(index)] = ipaddressinfo
                print('used ripe ip map method')
                index = index + 1
                continue

            except Exception as e:
                print('Ripe IP map did not work')
                print(e)


            #use IPinfo
            try:
                details = handler.getDetails(ipadr)
                ipaddressinfo['coordinates'] = details.loc
                ipaddressinfo['method'] = 'ipinfo'
                data[str(index)] = ipaddressinfo
                print('used ipInfo')
                index = index + 1
            except Exception as e:
                print('ipinfo did not work ')
                print(e)

            #     a = socket.gethostbyaddr(ipadr)[0]
            #     b = findRegexAndPlan(a)
            #     ipaddressinfo['coordinates'] = b[0]+','+b[1]
            #     ipaddressinfo['method'] = 'regex'
            #     data[str(index)] = ipaddressinfo
            # except Exception as e: 
            #     print(e)
            #     ipaddressinfo['hostname'] = 'no hostname'
            #     try:
            #         ripeinfo = (requests.get('https://ipmap-api.ripe.net/v1/locate/all?resources=' + ipadr)).json()
            #         ipaddressinfo['coordinates'] = str(ripeinfo['data'][ipadr]['latitude']) + ',' + str(ripeinfo['data'][ipadr]['longitude'])
            #         ipaddressinfo['method'] = 'ripe ip map'
            #         data[str(index)] = ipaddressinfo
            #     except Exception as e:
            #         print(e)
            #         try: 
            #             details = handler.getDetails(ipadr)
            #             ipaddressinfo['coordinates'] = details.loc
            #             ipaddressinfo['method'] = 'ipinfo'
            #             data[str(index)] = ipaddressinfo
            #         except Exception as e: 
            #             print(e)


        
        finaldata[tracert] = data

    print("____________________________")
    print(json.dumps(finaldata))
    return json.dumps(finaldata)

    # return '{"0": {"0": {"ip": "147.28.0.5", "tracertnum": "1", "latency": "0.6886666666666666", "nodeid": 5095871, "asnum": 3130, "hostname": "r1.sea.rg.net", "coordinates": "47.60621,-122.33207", "method": "ripe ip map"}, "1": {"ip": "206.81.80.133", "tracertnum": "1", "latency": "1.0936666666666668", "nodeid": 5121755, "asnum": null, "hostname": "pr1.edge-fo.sea6.vrsn.com", "coordinates": "47.60621,-122.33207", "method": "ripe ip map"}}, "1": {"0": {"ip": "202.97.89.202", "tracertnum": "2", "latency": "5.666666666666667", "nodeid": 4069405, "asnum": 4134, "hostname": "no hostname", "coordinates": "23.0180,113.7487", "method": "ipinfo"}, "1": {"ip": "202.97.91.190", "tracertnum": "2", "latency": "6.377666666666666", "nodeid": 1304906, "asnum": 4134, "hostname": "no hostname", "coordinates": "23.1167,113.2500", "method": "ipinfo"}, "2": {"ip": "202.97.13.26", "tracertnum": "2", "latency": "205.37533333333332", "nodeid": 3091, "asnum": 4134, "hostname": "no hostname", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}, "3": {"ip": "118.85.205.242", "tracertnum": "2", "latency": "205.67499999999998", "nodeid": 5121742, "asnum": 4134, "hostname": "no hostname", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}, "4": {"ip": "209.131.147.127", "tracertnum": "2", "latency": "249.00900000000001", "nodeid": 21772387, "asnum": 7342, "hostname": "no hostname", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}}, "2": {"0": {"ip": "37.60.16.65", "tracertnum": "3", "latency": "38.46966666666666", "nodeid": 59526448, "asnum": 50923, "hostname": "gw-up.tm.metro-set.ru", "coordinates": "-5.11306,105.30667", "method": "ripe ip map"}, "1": {"ip": "80.81.192.245", "tracertnum": "3", "latency": "98.14166666666667", "nodeid": 2063574, "asnum": null, "hostname": "7c-25-86-0c-62-d1.080-081-192-245.pas-843.de-cix.fra.de.as7342.verisign.com", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}, "2": {"ip": "81.19.204.127", "tracertnum": "3", "latency": "93.38366666666667", "nodeid": 20857379, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "3": {"0": {"ip": "5.180.135.108", "tracertnum": "4", "latency": "1.7623333333333333", "nodeid": 313806, "asnum": 13030, "hostname": "r1zrh9.core.init7.net", "coordinates": "47.464699,8.549170", "method": "regex"}, "1": {"ip": "5.180.135.173", "tracertnum": "4", "latency": "6.959333333333333", "nodeid": 313800, "asnum": 13030, "hostname": "r1fra3.core.init7.net", "coordinates": "50.033333,8.570556", "method": "regex"}, "2": {"ip": "81.19.204.127", "tracertnum": "4", "latency": "6.489", "nodeid": 20857379, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "4": {"1": {"ip": "185.22.46.145", "tracertnum": "5", "latency": "5.913333333333334", "nodeid": 45411641, "asnum": 60294, "hostname": "no hostname", "coordinates": "50.93333,6.95", "method": "ripe ip map"}, "2": {"ip": "80.249.209.232", "tracertnum": "5", "latency": "28.168666666666667", "nodeid": 5121738, "asnum": null, "hostname": "et-0-0-5.pr1.edge-fo.ams5.vrsn.net", "coordinates": "52.308601,4.763890", "method": "regex"}, "3": {"ip": "209.131.146.127", "tracertnum": "5", "latency": "868.2674999999999", "nodeid": 21772386, "asnum": 7342, "hostname": "no hostname", "coordinates": "48.85341,2.3488", "method": "ripe ip map"}}, "5": {"0": {"ip": "80.81.192.223", "tracertnum": "6", "latency": "24.248333333333335", "nodeid": 1640350, "asnum": null, "hostname": "decix.proxad.net", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}, "1": {"ip": "81.19.204.127", "tracertnum": "6", "latency": "24.30933333333333", "nodeid": 20857379, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "6": {"0": {"ip": "62.115.134.96", "tracertnum": "7", "latency": "61.649", "nodeid": 14911, "asnum": 1299, "hostname": "adm-bb1-link.ip.twelve99.net", "coordinates": "45.46427,9.18951", "method": "ripe ip map"}, "1": {"ip": "62.115.136.195", "tracertnum": "7", "latency": "52.796666666666674", "nodeid": 10231, "asnum": 1299, "hostname": "adm-b1-link.ip.twelve99.net", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}, "2": {"ip": "62.115.184.125", "tracertnum": "7", "latency": "61.29566666666667", "nodeid": 5421541, "asnum": 1299, "hostname": "verisign-ic-368002.ip.twelve99-cust.net", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}, "3": {"ip": "217.30.82.127", "tracertnum": "7", "latency": "58.41133333333334", "nodeid": 21870690, "asnum": 7342, "hostname": "no hostname", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}}, "7": {"0": {"ip": "203.96.236.14", "tracertnum": "8", "latency": "19.627333333333333", "nodeid": 9362, "asnum": 4785, "hostname": "cs1708.q51.os1.xtom.jp", "coordinates": "34.69374,135.50218", "method": "ripe ip map"}, "1": {"ip": "4.69.217.14", "tracertnum": "8", "latency": "15.382", "nodeid": 240681, "asnum": 3356, "hostname": "ae1.3505.edge2.Tokyo4.level3.net", "coordinates": "35.689500,139.691710", "method": "regex"}, "2": {"ip": "113.29.9.210", "tracertnum": "8", "latency": "13.077333333333334", "nodeid": 21220684, "asnum": 3549, "hostname": "no hostname", "coordinates": "35.6895,139.69171", "method": "ripe ip map"}}, "8": {"0": {"ip": "69.30.209.220", "tracertnum": "9", "latency": "0.589", "nodeid": 1876510, "asnum": 32097, "hostname": "no hostname", "coordinates": "39.0997,-94.5786", "method": "ipinfo"}, "1": {"ip": "69.30.209.185", "tracertnum": "9", "latency": "0.6829999999999999", "nodeid": 1876515, "asnum": 32097, "hostname": "100ge0-25.edge-2.grand.mci.us.as32097.net", "coordinates": "39.09973,-94.57857", "method": "ripe ip map"}, "2": {"ip": "206.81.80.133", "tracertnum": "9", "latency": "42.10733333333334", "nodeid": 5121755, "asnum": null, "hostname": "pr1.edge-fo.sea6.vrsn.com", "coordinates": "47.60621,-122.33207", "method": "ripe ip map"}, "3": {"ip": "209.131.154.127", "tracertnum": "9", "latency": "0", "nodeid": 21772392, "asnum": 7342, "hostname": "no hostname", "coordinates": "47.60621,-122.33207", "method": "ripe ip map"}}, "9": {"0": {"ip": "195.2.18.182", "tracertnum": "10", "latency": "24.108666666666664", "nodeid": 4619953, "asnum": 1273, "hostname": "ae10.pcr1.fis.cw.net", "coordinates": "52.019540,4.429460", "method": "regex"}, "1": {"ip": "195.2.27.230", "tracertnum": "10", "latency": "28.503666666666664", "nodeid": 1686321, "asnum": 1273, "hostname": "ae20-xcr1.fix.cw.net", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}, "2": {"ip": "80.81.192.245", "tracertnum": "10", "latency": "24.8565", "nodeid": 2063574, "asnum": null, "hostname": "7c-25-86-0c-62-d1.080-081-192-245.pas-843.de-cix.fra.de.as7342.verisign.com", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}, "3": {"ip": "81.19.204.127", "tracertnum": "10", "latency": "21.73733333333333", "nodeid": 20857379, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "10": {"0": {"ip": "129.250.6.47", "tracertnum": "11", "latency": "2.073333333333333", "nodeid": 3648532, "asnum": 2914, "hostname": "ae-11.r31.tokyjp05.jp.bb.gin.ntt.net", "coordinates": "35.6895,139.69171", "method": "ripe ip map"}, "1": {"ip": "129.250.6.54", "tracertnum": "11", "latency": "1.5233333333333334", "nodeid": 58042, "asnum": 2914, "hostname": "ae-1.a00.tokyjp10.jp.bb.gin.ntt.net", "coordinates": "35.6,140.11667", "method": "ripe ip map"}, "2": {"ip": "120.88.54.74", "tracertnum": "11", "latency": "1.2773333333333332", "nodeid": 2616714, "asnum": 2914, "hostname": "ae-0.verisign.tokyjp10.jp.bb.gin.ntt.net", "coordinates": "35.6895,139.69171", "method": "ripe ip map"}}, "11": {"0": {"ip": "129.250.6.47", "tracertnum": "12", "latency": "1.1216666666666668", "nodeid": 3648532, "asnum": 2914, "hostname": "ae-11.r31.tokyjp05.jp.bb.gin.ntt.net", "coordinates": "35.6895,139.69171", "method": "ripe ip map"}, "1": {"ip": "129.250.6.54", "tracertnum": "12", "latency": "3.267666666666667", "nodeid": 58042, "asnum": 2914, "hostname": "ae-1.a00.tokyjp10.jp.bb.gin.ntt.net", "coordinates": "35.6,140.11667", "method": "ripe ip map"}, "2": {"ip": "120.88.54.74", "tracertnum": "12", "latency": "1.0986666666666667", "nodeid": 2616714, "asnum": 2914, "hostname": "ae-0.verisign.tokyjp10.jp.bb.gin.ntt.net", "coordinates": "35.6895,139.69171", "method": "ripe ip map"}}, "12": {"0": {"ip": "212.161.249.31", "tracertnum": "13", "latency": "24.492", "nodeid": 4585583, "asnum": 6730, "hostname": "lau01pe20.100ge3-0-0.bb.sunrise.net", "coordinates": "46.516,6.63282", "method": "ripe ip map"}, "1": {"ip": "84.116.134.53", "tracertnum": "13", "latency": "45.76133333333333", "nodeid": 2134837, "asnum": 6830, "hostname": "nl-ams17b-rc1-lag-5-0.aorta.net", "coordinates": "52.308601,4.763890", "method": "regex"}, "2": {"ip": "84.116.134.54", "tracertnum": "13", "latency": "50.263", "nodeid": 773152, "asnum": 6830, "hostname": "nl-ams09c-ri1-ae-5-0.aorta.net", "coordinates": "52.308601,4.763890", "method": "regex"}, "3": {"ip": "209.131.147.127", "tracertnum": "13", "latency": "55.37133333333333", "nodeid": 21772387, "asnum": 7342, "hostname": "no hostname", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}}, "13": {"0": {"ip": "5.56.21.153", "tracertnum": "14", "latency": "0.6413333333333333", "nodeid": 48475071, "asnum": 201011, "hostname": "ae22-501.fra10.core-backbone.com", "coordinates": "50.033333,8.570556", "method": "regex"}, "1": {"ip": "80.255.14.6", "tracertnum": "14", "latency": "0.6403333333333333", "nodeid": 304979, "asnum": 201011, "hostname": "ae2-2021.fra20.core-backbone.com", "coordinates": "50.033333,8.570556", "method": "regex"}, "2": {"ip": "80.81.192.245", "tracertnum": "14", "latency": "1.5316666666666665", "nodeid": 2063574, "asnum": null, "hostname": "7c-25-86-0c-62-d1.080-081-192-245.pas-843.de-cix.fra.de.as7342.verisign.com", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}, "3": {"ip": "81.19.204.127", "tracertnum": "14", "latency": "0.8693333333333334", "nodeid": 20857379, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "14": {"0": {"ip": "80.249.209.232", "tracertnum": "15", "latency": "3.9789999999999996", "nodeid": 5121738, "asnum": null, "hostname": "et-0-0-5.pr1.edge-fo.ams5.vrsn.net", "coordinates": "52.308601,4.763890", "method": "regex"}, "1": {"ip": "209.131.146.127", "tracertnum": "15", "latency": "0", "nodeid": 21772386, "asnum": 7342, "hostname": "no hostname", "coordinates": "48.85341,2.3488", "method": "ripe ip map"}}, "15": {"0": {"ip": "69.139.203.185", "tracertnum": "16", "latency": "9.278666666666666", "nodeid": 50730002, "asnum": 7922, "hostname": "no hostname", "coordinates": "41.85003,-87.65005", "method": "ripe ip map"}, "1": {"ip": "4.14.14.170", "tracertnum": "16", "latency": "44.544666666666664", "nodeid": 20209107, "asnum": 3356, "hostname": "VERISIGN-IN.ear4.Chicago2.Level3.net", "coordinates": "41.850030,-87.650050", "method": "regex"}}, "16": {"0": {"ip": "213.249.107.90", "tracertnum": "17", "latency": "19.982", "nodeid": 59964, "asnum": 3356, "hostname": "no hostname", "coordinates": "59.32938,18.06871", "method": "ripe ip map"}, "1": {"ip": "213.19.192.110", "tracertnum": "17", "latency": "44.309666666666665", "nodeid": 21830962, "asnum": 3356, "hostname": "VERISIGN-NE.ear4.Amsterdam1.Level3.net", "coordinates": "52.374030,4.889690", "method": "regex"}}, "17": {"0": {"ip": "80.249.209.232", "tracertnum": "18", "latency": "48.64033333333333", "nodeid": 5121738, "asnum": null, "hostname": "et-0-0-5.pr1.edge-fo.ams5.vrsn.net", "coordinates": "52.308601,4.763890", "method": "regex"}, "1": {"ip": "209.131.146.127", "tracertnum": "18", "latency": "54.109", "nodeid": 21772386, "asnum": 7342, "hostname": "no hostname", "coordinates": "48.85341,2.3488", "method": "ripe ip map"}}, "18": {"0": {"ip": "52.93.143.93", "tracertnum": "19", "latency": "4.692333333333333", "nodeid": 21663, "asnum": null, "hostname": "no hostname", "coordinates": "59.32938,18.06871", "method": "ripe ip map"}, "1": {"ip": "81.19.207.127", "tracertnum": "19", "latency": "20.084", "nodeid": 20857381, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "19": {"0": {"ip": "180.87.39.25", "tracertnum": "20", "latency": "3.6543333333333337", "nodeid": 3253520, "asnum": 6453, "hostname": "ix-ae-1-100.tcore2.mlv-mumbai.as6453.net", "coordinates": "19.072830,72.882610", "method": "regex"}, "1": {"ip": "180.87.38.1", "tracertnum": "20", "latency": "106.998", "nodeid": 300072, "asnum": 6453, "hostname": "if-ae-2-2.tcore1.mlv-mumbai.as6453.net", "coordinates": "19.072830,72.882610", "method": "regex"}, "2": {"ip": "195.219.156.150", "tracertnum": "20", "latency": "109.45766666666668", "nodeid": 300436, "asnum": 6453, "hostname": "if-ae-29-2.tcore1.fnm-frankfurt.as6453.net", "coordinates": "50.115520,8.684170", "method": "regex"}, "3": {"ip": "81.19.207.127", "tracertnum": "20", "latency": "108.96199999999999", "nodeid": 20857381, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "20": {"0": {"ip": "111.125.73.1", "tracertnum": "21", "latency": "1.9563333333333333", "nodeid": 35065037, "asnum": 17639, "hostname": "1.73.125.111.-rev.convergeict.com", "coordinates": "14.6488,121.0509", "method": "ripe ip map"}, "1": {"ip": "129.250.2.114", "tracertnum": "21", "latency": "208.768", "nodeid": 58011, "asnum": 2914, "hostname": "ae-1.a02.lsanca20.us.bb.gin.ntt.net", "coordinates": "34.05223,-118.24368", "method": "ripe ip map"}, "2": {"ip": "129.250.194.126", "tracertnum": "21", "latency": "214.0683333333333", "nodeid": 21319226, "asnum": 2914, "hostname": "ce-2-2-1.a02.lsanca20.us.ce.gin.ntt.net", "coordinates": "14.5786,121.1222", "method": "ripe ip map"}}, "21": {"0": {"ip": "185.183.127.249", "tracertnum": "22", "latency": "0.62", "nodeid": 21540534, "asnum": 205790, "hostname": "b9b77ff9.ip.as205790.net", "coordinates": "52.52437,13.41053", "method": "ripe ip map"}, "1": {"ip": "212.74.67.15", "tracertnum": "22", "latency": "14.113666666666665", "nodeid": 4412145, "asnum": null, "hostname": "no hostname", "coordinates": "50.93333,6.95", "method": "ripe ip map"}, "2": {"ip": "80.249.209.232", "tracertnum": "22", "latency": "15.384", "nodeid": 5121738, "asnum": null, "hostname": "et-0-0-5.pr1.edge-fo.ams5.vrsn.net", "coordinates": "52.308601,4.763890", "method": "regex"}}, "22": {"0": {"ip": "80.231.158.30", "tracertnum": "23", "latency": "43.531", "nodeid": 11056, "asnum": 6453, "hostname": "if-ae-1-3.tcore1.sv8-highbridge.as6453.net", "coordinates": "51.216670,-2.983330", "method": "regex"}, "1": {"ip": "80.231.139.1", "tracertnum": "23", "latency": "42.817", "nodeid": 24269, "asnum": 6453, "hostname": "if-ae-2-2.tcore2.sv8-highbridge.as6453.net", "coordinates": "51.216670,-2.983330", "method": "regex"}, "2": {"ip": "80.231.130.4", "tracertnum": "23", "latency": "42.53733333333333", "nodeid": 500974, "asnum": 6453, "hostname": "no hostname", "coordinates": "51.50853,-0.12574", "method": "ripe ip map"}, "3": {"ip": "80.231.130.47", "tracertnum": "23", "latency": "44.865", "nodeid": 46311, "asnum": 6453, "hostname": "if-ae-35-2.thar1.lrt-london.as6453.net", "coordinates": "51.508530,-0.125740", "method": "regex"}, "4": {"ip": "209.131.129.127", "tracertnum": "23", "latency": "46.32566666666667", "nodeid": 21772374, "asnum": 7342, "hostname": "no hostname", "coordinates": "51.50853,-0.12574", "method": "ripe ip map"}}, "23": {"0": {"ip": "80.231.158.5", "tracertnum": "24", "latency": "36.04233333333333", "nodeid": 24272, "asnum": 6453, "hostname": "no hostname", "coordinates": "38.71667,-9.13333", "method": "ripe ip map"}, "1": {"ip": "80.231.158.30", "tracertnum": "24", "latency": "35.03333333333333", "nodeid": 11056, "asnum": 6453, "hostname": "if-ae-1-3.tcore1.sv8-highbridge.as6453.net", "coordinates": "51.216670,-2.983330", "method": "regex"}, "2": {"ip": "80.231.139.1", "tracertnum": "24", "latency": "35.23", "nodeid": 24269, "asnum": 6453, "hostname": "if-ae-2-2.tcore2.sv8-highbridge.as6453.net", "coordinates": "51.216670,-2.983330", "method": "regex"}, "3": {"ip": "80.231.130.47", "tracertnum": "24", "latency": "35.67933333333334", "nodeid": 46311, "asnum": 6453, "hostname": "if-ae-35-2.thar1.lrt-london.as6453.net", "coordinates": "51.508530,-0.125740", "method": "regex"}, "4": {"ip": "199.7.80.152", "tracertnum": "24", "latency": "35.069", "nodeid": 5121725, "asnum": null, "hostname": "no hostname", "coordinates": "52.3740,4.8897", "method": "ipinfo"}, "5": {"ip": "209.131.129.127", "tracertnum": "24", "latency": "93.25600000000001", "nodeid": 21772374, "asnum": 7342, "hostname": "no hostname", "coordinates": "51.50853,-0.12574", "method": "ripe ip map"}}, "24": {"0": {"ip": "129.250.3.179", "tracertnum": "25", "latency": "97.164", "nodeid": 3647179, "asnum": 2914, "hostname": "ae-12.r25.lsanca07.us.bb.gin.ntt.net", "coordinates": "52.37403,4.88969", "method": "ripe ip map"}, "1": {"ip": "129.250.2.114", "tracertnum": "25", "latency": "232.67033333333333", "nodeid": 58011, "asnum": 2914, "hostname": "ae-1.a02.lsanca20.us.bb.gin.ntt.net", "coordinates": "34.05223,-118.24368", "method": "ripe ip map"}, "2": {"ip": "129.250.194.126", "tracertnum": "25", "latency": "157.18999999999997", "nodeid": 21319226, "asnum": 2914, "hostname": "ce-2-2-1.a02.lsanca20.us.ce.gin.ntt.net", "coordinates": "14.5786,121.1222", "method": "ripe ip map"}}, "25": {"0": {"ip": "85.132.90.153", "tracertnum": "26", "latency": "74.995", "nodeid": 20914552, "asnum": 29049, "hostname": "no hostname", "coordinates": "40.3777,49.8920", "method": "ipinfo"}, "1": {"ip": "80.81.192.245", "tracertnum": "26", "latency": "97.529", "nodeid": 2063574, "asnum": null, "hostname": "7c-25-86-0c-62-d1.080-081-192-245.pas-843.de-cix.fra.de.as7342.verisign.com", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}, "2": {"ip": "81.19.204.127", "tracertnum": "26", "latency": "76.99400000000001", "nodeid": 20857379, "asnum": 7342, "hostname": "no hostname", "coordinates": "50.11552,8.68417", "method": "ripe ip map"}}, "26": {"0": {"ip": "80.231.158.30", "tracertnum": "27", "latency": "47.06933333333333", "nodeid": 11056, "asnum": 6453, "hostname": "if-ae-1-3.tcore1.sv8-highbridge.as6453.net", "coordinates": "51.216670,-2.983330", "method": "regex"}, "1": {"ip": "80.231.138.22", "tracertnum": "27", "latency": "44.574", "nodeid": 1720104, "asnum": 6453, "hostname": "if-ae-19-2.tcore2.l78-london.as6453.net", "coordinates": "51.508530,-0.125740", "method": "regex"}, "2": {"ip": "80.231.131.118", "tracertnum": "27", "latency": "44.528", "nodeid": 241384, "asnum": 6453, "hostname": "if-ae-15-2.tcore2.ldn-london.as6453.net", "coordinates": "51.508530,-0.125740", "method": "regex"}, "3": {"ip": "80.231.62.74", "tracertnum": "27", "latency": "44.129333333333335", "nodeid": 46311, "asnum": 6453, "hostname": "if-ae-3-2.thar1.lrt-london.as6453.net", "coordinates": "51.508530,-0.125740", "method": "regex"}, "4": {"ip": "209.131.129.127", "tracertnum": "27", "latency": "56.406000000000006", "nodeid": 21772374, "asnum": 7342, "hostname": "no hostname", "coordinates": "51.50853,-0.12574", "method": "ripe ip map"}}}'
   
   
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