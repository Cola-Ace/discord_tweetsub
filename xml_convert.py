import xml.etree.ElementTree as ET
import json

def xml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    return json.dumps({root.tag: xml_to_dict(root)})

def xml_to_dict(element):
    d = {}
    if element.attrib:
        d["@attributes"] = element.attrib
    if element.text:
        d[element.tag] = element.text
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in d:
            if type(d[child.tag]) is list:
                d[child.tag].append(child_data)
            else:
                d[child.tag] = [d[child.tag], child_data]
        else:
            d[child.tag] = child_data
    return d