# import requests
import json
import re

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