# coding: utf-8
'''the vast majority of this code was barrowed and tweeked from the Udacity
forums and the rest is taken from the classes I have taken on their amazing website'''
import xml.etree.cElementTree as ET
import re
from pprint import pprint
from collections import defaultdict
import json
import codecs

osm_file = "sample.osm"

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "st" : "Street",
            "STreet" : "Street",
            "Rd" : "Road",
            "Rd." : "Road",
            "Av" : "Avenue",
            "Ave" : "Avenue",
            "Ave." : "Avenue",
            "Ct" : "Court",
            "Blvd" : "Boulevard",
            "Dr" : "Drive",
            "Pl" : "Place"
            }
''' Start audit street type'''
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].append(street_name)


def is_street_name(element):
    return (element.attrib['k'] == "addr:street")


def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            name = re.sub(street_type_re, mapping[street_type], name)
    return name

'''Start Shape Element'''
def shape_element(element):
    node = {}
    if element.tag == 'node' or element.tag == 'way':
        created = {}
        for e in element.attrib.keys():

            if e in CREATED:
                created[e] = element.attrib[e]
            elif element.attrib[e] == element.get('lat') or element.attrib == element.get('lon'):
                pos = []
                pos.append(float(element.get('lat')))
                pos.append(float(element.get('lon')))
                node['pos'] = pos
            else:
                node[e] = element.get(e)

                node['type'] = element.tag
        node['created'] = created
#Audit street Types
        street_types = defaultdict(set)
        for tag in element.iter("tag"):
            if is_street_name(tag):
                audit_street_type(street_types, tag.attrib['v'])
        node['street_types'] = street_types

#end Audit street Types
        node_refs = []
        address = {}
        for subtags in element:
            if subtags.tag == 'tag':
                if re.search(problemchars, subtags.get('k')):
                    pass
                elif re.search(r'\w+:\w+:\w+', subtags.get('k')):
                    pass
                elif subtags.get('k').startswith('addr:'):
                    address[subtags.get('k')[10:]] = subtags.get('v')
                    node['address'] = address
                else:
                    node[subtags.get('k')] = subtags.get('v')
            else:
                if subtags.tag =='nd':

                    node_refs.append(subtags.get('ref'))

                else:
                    pass

        if node_refs:
            node['node_refs'] = node_refs

        return node
        pprint(node)

    else:
        return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
    pprint.pprint(data)



if __name__ == "__main__":
    finaljson = process_map(osm_file)
    pprint(finaljson)
