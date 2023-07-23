import os
import json
import pickle


def km2ms(km):
    return float(km)/200000*1000


def add(d, x, y, z):
    if x not in d:
        d[x] = {}
    d[x][y] = z


def stripComment(line):
    p = line.find("#")
    if p != -1:
        return line[:p]
    return line.strip()


def splitColon(line):
    p = line.find(":")
    if p != -1:
        return line[:p], line[p+1:]
    return line, ''


def reader(filename):
    with open(filename, "r") as fin:
        for line in fin:
            line = stripComment(line)
            if len(line) == 0:
                continue
            yield line


def readFromCache(cachename, readFunc):
    if os.path.isfile(cachename):
        with open(cachename, "rb") as f:
            results = pickle.load(f)
            return results
    results = readFunc()
    with open(cachename, "wb") as f:
        pickle.dump(results, f)
    print(cachename+" finished")
    return results


def readNodes(filename):
    def f(filename):
        node_ifaces = {}
        iface_node = {}
        for line in reader(filename):
            node, ifaces = splitColon(line)
            nid = int(node.split()[1][1:])
            ifaces = [i.replace(".","") for i in ifaces.split()]
            node_ifaces[nid] = ifaces
            for iface in ifaces:
                iface_node[iface.replace(".","")] = nid
        return (node_ifaces, iface_node)
    return readFromCache("nodes.pickle", lambda: f(filename))


def readAS(filename):
    def f(filename):
        node_as = {}
        for line in reader(filename):
            row = line.split()
            nid = int(row[1][1:])
            AS = int(row[2])
            if AS == -1:
                continue
            node_as[nid] = AS
        return node_as
    return readFromCache("as.pickle", lambda: f(filename))


def readASRel(filename):
    provider_customer = set()
    peer_peer = set()
    for line in reader(filename):
        as1, as2, rel, bgp = line.split("|")
        if rel == "-1":
            provider_customer.add((int(as1), int(as2)))
        else:
            peer_peer.add((int(as1), int(as2)))
            peer_peer.add((int(as2), int(as1)))
    return provider_customer, peer_peer


def readLinks(filename):
    def f(filename):
        node_link = {}
        for line in reader(filename):
            link, nodes = splitColon(line)
            nodes = nodes.split()
            nids = []
            for node in nodes:
                nid = splitColon(node)[0]
                nids.append(int(nid[1:]))
            for i in nids:
                for j in nids:
                    if i == j:
                        continue
                    if i not in node_link:
                        node_link[i] = {}
                    node_link[i][j] = -1  # use -1 as a placeholder for distance
        return node_link
    return readFromCache("links.pickle", lambda: f(filename))


def readGeo(filename):
    def f(filename):
        node_latlng = {}
        for line in reader(filename):
            node, geo = splitColon(line)
            nid = node.split()[1]
            geo = geo.split('\t')
            node_latlng[nid] = [geo[5], geo[6]]
        return node_latlng
    return readFromCache("geo.pickle", lambda: f(filename))


def readTraceroute(filename, status):
    traces = []
    with open(filename, "r") as fin:
        for line in fin:
            trace = json.loads(line)
            if trace["type"] != "trace":
                continue
            if trace["stop_reason"] in status:
                traces.append(trace)
    print("read traceroute finished")
    return traces

# x = readNodes('static/midar-iff.nodes')[0]
x = readNodes('test.nodes.txt')[0]
print(x)

def determineNodeOfIP(ip,x):
    for node in x:
        for ipadr in x[node]:
            if ip.replace(".","") == ipadr:
                return node

a = determineNodeOfIP('187.253.253.101',x)
print(a)