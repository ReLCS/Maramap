import json
import re
from util import *
import pyasn
import socket
import requests
import redis
import ipinfo


r = redis.Redis(host='localhost', port=6379, db=0)

access_token = '97da130c7c5c32'
handler = ipinfo.getHandler(access_token)

# x = readNodes('static/midar-iff.nodes')

def getIPInfo_FromDB(ipadr):

    info = {}
    # print(ipadr)


    try:
        host = socket.gethostbyaddr(ipadr)[0]
        info['hostname'] = host
        # print('hostname found')

        try: 
            regexCoords = findRegexAndPlan(host)
            info['coordinates'] = regexCoords[0]+','+regexCoords[1]
            info['method'] = 'regex'
            # print('used regex method')

            try:
                country = (requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + info['coordinates'] +'&key=AIzaSyAO-r75d8IVw3xwou82zXbABZnrNUFSKGY')).json()['plus_code']['compound_code'].split(', ')[-1]
                info['country'] = country
            except:
                info['country'] = False
                pass

            return info
        
        except Exception as e:
            # print('Could not find regex in hostname')
            # print(e)
            pass

    except Exception as e:
        info['hostname'] = 'no hostname'
        # print('Hostname not found ')
        # print(e)    
    
    #try to use ripe method
    try:
        ripeinfo = (requests.get('https://ipmap-api.ripe.net/v1/locate/all?resources=' + ipadr)).json()
        info['coordinates'] = str(ripeinfo['data'][ipadr]['latitude']) + ',' + str(ripeinfo['data'][ipadr]['longitude'])
        info['method'] = 'ripe ip map'
        # print('used ripe ip map method')

        try:
            country = (requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + info['coordinates'] +'&key=AIzaSyAO-r75d8IVw3xwou82zXbABZnrNUFSKGY')).json()['plus_code']['compound_code'].split(', ')[-1]
            info['country'] = country
        except:
            info['country'] = False
            pass

        return info

    except Exception as e:
        # print('Ripe IP map did not work')
        # print(e)
        pass

    #use IPinfo
    try:
        details = handler.getDetails(ipadr)
        info['coordinates'] = details.loc
        info['method'] = 'ipinfo'
        # print('used ipInfo')

        try:
            country = (requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + info['coordinates'] +'&key=AIzaSyAO-r75d8IVw3xwou82zXbABZnrNUFSKGY')).json()['plus_code']['compound_code'].split(', ')[-1]
            info['country'] = country
        except:
            info['country'] = False
            pass

        return info
    except Exception as e:
        return False

def getIPInfo(ipadr):


    ipaddressinfo = r.get(ipadr)
    if ipaddressinfo:
        # print('used cache for query')
        return json.loads(ipaddressinfo)
    else: 
        ipaddressinfo = getIPInfo_FromDB(ipadr)
        r.set(ipadr, json.dumps(ipaddressinfo))
        return ipaddressinfo


def getHostnameEnd(hostname):
    hostnameEnd = hostname.split(".")[-2:][0] + '.' + hostname.split(".")[-2:][1]
    domains = open("static/domainlist.txt")
    domainList = (domains.read()).split(',')
    for domain in domainList:
        if hostnameEnd == domain:
            domains.close()
            return(hostnameEnd) 
    hostnameEnd = hostname.split(".")[-3:][0] + '.' + hostname.split(".")[-3:][1] + '.' + hostname.split(".")[-3:][2]
    domains.close()
    return (hostnameEnd)


def getCLLICode(cllicode):
    cllis = open('clli-lat-lon.230606.txt')
    cllilist = (cllis.read()).splitlines()
    for clli in cllilist:
        if cllicode.lower() == clli.split('\t')[0].lower():
            return clli.split('\t')[1] + ',' + clli.split('\t')[2]

def findRegexAndPlan(hostname):

    hostname = hostname.lower()

    hostnames = open("static/202103-midar-iff.geo-re.json")
    hostnameEnd = getHostnameEnd(hostname)
    hostnameList = json.load(hostnames)['foo']

    for domain in hostnameList:
        if domain['domain'] == hostnameEnd:

            rightRegexes = domain['re']
            for rightRegex in rightRegexes:
                if ',' in rightRegex:
                    rightRegex = rightRegex.replace(',','')
                if len(re.findall(rightRegex,hostname)) != 0:
                    parsedGeohints = re.findall(rightRegex,hostname)[0]
                
            plan = domain['plan'][0]

            for geohint in domain['geohints']:

                if geohint['type'] == 'clli':
                    hostnames.close()
                    latlng = getCLLICode(geohint['code'])
                    return latlng

                if isinstance(parsedGeohints, str) == True:
                    if parsedGeohints == geohint['code']: 
                        hostnames.close()
                        return(geohint['lat'],geohint['lng'])

                for parsedGeohint in parsedGeohints:
                    if parsedGeohint == geohint['code']: 
                        hostnames.close()
                        return(geohint['lat'],geohint['lng'])

            hostnames.close()
            return rightRegex, plan, parsedGeohints


def airportGetLoc(airportcode):
    airportcodes = open("static/iata-icao.csv","r")
    for row in airportcodes:
        if len(airportcode) == 4:
            matchedCode = (((row.split(','))[3]).lower())[1:-1]
            if airportcode == matchedCode:
                airportcodes.close()
                coords = []
                coords.append((row.split(',')[-2])[1:-1])
                coords.append((row.split(',')[-1])[1:(row.split(',')[-1]).rfind('"')])
                return coords


        if len(airportcode) == 3:
            matchedCode = (((row.split(','))[2]).lower())[1:-1]
            if airportcode == matchedCode:
                airportcodes.close()
                coords = []
                coords.append((row.split(',')[-2])[1:-1])
                coords.append((row.split(',')[-1])[1:(row.split(',')[-1]).rfind('"')])
                return coords