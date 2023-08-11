import json
import ipinfo
from reversedns import *
import socket
import requests
import os
import redis
access_token = '97da130c7c5c32'
handler = ipinfo.getHandler(access_token)


# def getCountry(ipadr):

#     # #try to use DNS method
#     # try:
#     #     host = socket.gethostbyaddr(ipadr)[0]
#     #     regexCoords = findRegexAndPlan(host)
#     #     coords = regexCoords[0] + ',' + regexCoords[1]

#     # except:
            
#     #try to use ripe method
#     # try:
#     #     ripeinfo = (requests.get('https://ipmap-api.ripe.net/v1/locate/all?resources=' + ipadr)).json()
#     #     coords = str(ripeinfo['data'][ipadr]['latitude']) + ',' + str(ripeinfo['data'][ipadr]['longitude'])

#     # except:

#         #ipinfo
#     try:
#         details = handler.getDetails(ipadr)
#         coords = details.loc
#     except Exception as e:
#         pass


#     try:
#         country = (requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + coords+'&key=AIzaSyAO-r75d8IVw3xwou82zXbABZnrNUFSKGY')).json()['plus_code']['compound_code'].split(', ')[-1]
#         # info = (requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + coords+'&key=AIzaSyAO-r75d8IVw3xwou82zXbABZnrNUFSKGY')).json()
#         # country = info['results'][0]['address_components'][-2]['long_name']
#         # if country.isnumeric():
#         #     country = info['results'][0]['address_components'][-3]['long_name']
#         # return country
#         return country
#     except:
#         pass

# Specify the file path
root_dir = "/home/lsh/ella/FindIPLocation/traceroutes/topology/ark/ipv4/probe-data/team-1/daily/2023"

def read_jsonl(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield json.loads(line)

Usa = 0
Uk = 0
France = 0
Germany = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    index = 0
    for filename in filenames:
        print(filename)
        # Only process .json files
        if filename.endswith('.json'):
            filepath = os.path.join(dirpath, filename)
            try:
                # x = 0
                for obj in read_jsonl(filepath):
                    foundUSA = False
                    foundUk = False
                    foundFrance = False
                    foundGermany = False
                    if (obj['type']) != 'cycle-start' and (obj['type'] != 'cycle-stop'):
                        # print('---------------------------')
                        for hop in obj['hops']:
                            info = getIPInfo(hop['addr'])
                            if info != False: 
                                country = info['country']
                                # print(country)
                                if country == 'USA':
                                    foundUSA = True
                                if country == 'UK':
                                    foundUk = True
                                if country == 'France':
                                    foundFrance = True
                                if country == 'Germany':
                                    foundGermany = True
    
                    if foundUSA == True:
                        Usa += 1
                    if foundUk == True:
                        Uk += 1
                    if foundFrance == True:
                        France += 1
                    if foundGermany == True:
                        Germany += 1
                    print(index)
                    # print(x)
                    # x += 1
                    print(Usa)
                    print(Uk)
                    print(France)
                    print(Germany)
            except Exception as e:
                print(f"Failed to process file {filepath}. Reason: {e}")
        print(Usa)
        print(Uk)
        print(France)
        print(Germany)
        index += 1

# print(Usa)
# print(Uk)
# print(France)
# print(Germany)


# for obj in read_jsonl(file_path):
#         if (obj['type']) != 'cycle-start' and (obj['type'] != 'cycle-stop'):
#             print('---------------------------')
#             for hop in obj['hops']:
#                 country = getCountry(hop['addr'])
#                 if country == 'USA':
#                     Usa +- 1
#                 if country == 'UK':
#                     Uk += 1
#                 if country == 'France':
#                     France += 1
#                 if country == 'Germany':
#                     Germany += 1
#                 print(country)




# try:
#     for obj in read_jsonl(file_path):
#         # print(obj['hops'])
#         # for hop in (obj['hops']):
#         #     print(hop['addr'])
#         print('---------------------------')
#         print(obj)
# except Exception as e:
#     print(f"Failed to process file {file_path}. Reason: {e}")
