# -*- coding:utf-8 -*-
import sys
import urllib
import re
import xml.etree.ElementTree as ET
##check it on http://postcalc.usps.com/


def clean_element(element_name, content):
    element_pattern = "<" + element_name + ">.*?</" + element_name + ">"
    element_replace = "<" + element_name + "></" + element_name + ">"
    return re.sub(element_pattern, element_replace, content, flags=re.MULTILINE|re.DOTALL)

def usps_intl_rate(country, origin_zip="18701", pounds="0", ounces="0", valueofcontents="0.0"):
    shipping_uri = "http://production.shippingapis.com/ShippingAPI.dll?API=IntlRateV2&XML="
    userid = "718Z2SYS3029"
    xml_request_template = "<IntlRateV2Request USERID=\"%(USERID)s\"><Revision>2</Revision><Package ID=\"1ST\"><Pounds>%(Pounds)s</Pounds><Ounces>%(Ounces)s</Ounces><Machinable>True</Machinable><MailType>Package</MailType><ValueOfContents>%(ValueOfContents)s</ValueOfContents><Country>%(Country)s</Country><Container>RECTANGULAR</Container><Size>REGULAR</Size><Width>0</Width><Length>0</Length><Height>0</Height><Girth>0</Girth><OriginZip>%(OriginZip)s</OriginZip></Package></IntlRateV2Request>"
    param = {"USERID" : userid,
            "Pounds": pounds,
            "Ounces": ounces,
            "ValueOfContents": valueofcontents,
            "Country": country,
            "OriginZip": origin_zip}
    xml_request = xml_request_template % param
    http_request = shipping_uri + xml_request
    #print "http_request:"
    #print  http_request
    print ""
    http_response = urllib.urlopen(http_request)
    response_content = http_response.read()
    print "http_response:"
    
    response_content = clean_element("Prohibitions", response_content)
    response_content = clean_element("Restrictions", response_content)
    response_content = clean_element("CustomsForms", response_content)
    response_content = clean_element("ExpressMail", response_content)
    response_content = clean_element("Observations", response_content)
    response_content = response_content.replace("><", ">\n<")
    #print response_content
    #save_response(response_content)
    tidyString(response_content)
    return response_content

def usps_rate(zipDestination="18701", zipOrigination="18701", pounds="0", ounces="0"):
    shipping_uri = "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML="
    userid = "718Z2SYS3029"
    xml_request_template = "<RateV4Request USERID=\"%(USERID)s\"><Revision>2</Revision><Package ID=\"1ST\"><Service>ALL</Service><FirstClassMailType>PARCEL</FirstClassMailType><ZipOrigination>%(ZipOrigination)s</ZipOrigination><ZipDestination>%(ZipDestination)s</ZipDestination><Pounds>%(Pounds)s</Pounds><Ounces>%(Ounces)s</Ounces><Container/><Size>REGULAR</Size><Machinable>true</Machinable></Package></RateV4Request>"
    param = {"USERID" : userid,
            "Pounds": pounds,
            "Ounces": ounces,
            "ZipDestination": zipDestination,
            "ZipOrigination": zipOrigination}
    xml_request = xml_request_template % param
    http_request = shipping_uri + xml_request
    #print "http_request:"
    #print  http_request
    print ""
    http_response = urllib.urlopen(http_request)
    response_content = http_response.read()
    #print "http_response:"
    
    response_content = clean_element("Prohibitions", response_content)
    response_content = clean_element("Restrictions", response_content)
    response_content = clean_element("CustomsForms", response_content)
    response_content = clean_element("ExpressMail", response_content)
    response_content = clean_element("Observations", response_content)
    response_content = response_content.replace("><", ">\n<")
    #print response_content
    #save_response(response_content)
    tidyRateString(response_content)
    return response_content

def save_response(response_content):
    filename = "usps_response.xml"
    with open(filename, mode='wb') as a_file:
        a_file.write(response_content)
        a_file.flush()

def tidy(filename):
    root = ET.parse(filename).getroot()
    all_packages = root.findall("Package")
    print "Package size = ", len(all_packages)
    for package in all_packages:
        print ""
        print "==================================="
        print "PackageID = ", package.attrib["ID"]
        all_services = package.findall("Service")
        print "Services size = ", len(all_services)
        for service in all_services:
            svcDescription = service.find('SvcDescription').text
            svcDescription = svcDescription.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            postage = service.find('Postage').text
            svcCommitments = None
            try:
                svcCommitments = service.find('SvcCommitments').text
            except:
                pass
            if None != svcCommitments:
                svcDescription = svcDescription + "(" + svcCommitments + ")"
            print "$"+postage+"\t\t"+svcDescription

def tidyString(content):
    root = ET.XML(content)
    all_packages = root.findall("Package")
    print "Package size = ", len(all_packages)
    for package in all_packages:
        print ""
        print "==================================="
        print "PackageID = ", package.attrib["ID"]
        all_services = package.findall("Service")
        print "Services size = ", len(all_services)
        for service in all_services:
            svcDescription = service.find('SvcDescription').text
            svcDescription = svcDescription.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            postage = service.find('Postage').text
            svcCommitments = None
            try:
                svcCommitments = service.find('SvcCommitments').text
            except:
                pass
            if None != svcCommitments:
                svcDescription = svcDescription + "(" + svcCommitments + ")"
            print "$"+postage+"\t\t"+svcDescription

def tidyRateString(content):
    root = ET.XML(content)
    all_packages = root.findall("Package")
    print "Package size = ", len(all_packages)
    for package in all_packages:
        print ""
        print "==================================="
        print "PackageID = ", package.attrib["ID"]
        all_services = package.findall("Postage")
        print "Services size = ", len(all_services)
        for service in all_services:
            svcDescription = service.find('MailService').text
            svcDescription = svcDescription.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            postage = service.find('Rate').text
            svcCommitments = None
            try:
                svcCommitments = service.find('SvcCommitments').text
            except:
                pass
            if None != svcCommitments:
                svcDescription = svcDescription + "(" + svcCommitments + ")"
            print "$"+postage+"\t\t"+svcDescription

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "A python script to test shipping type and cost for international and in American."
        print "Usage: usps.py pounds ounces"
        sys.exit(1)
    pounds = sys.argv[1]
    ounces = sys.argv[2]
    print "Weight:", pounds, " pounds  ", ounces, " ounces "
    print "-------International------------------------------"
    usps_intl_rate(country="Canada", origin_zip="", pounds=pounds, ounces=ounces, valueofcontents="15.0")
    
    print ""
    print "-------American------------------------------"
    usps_rate(zipDestination="10701", zipOrigination="18701", pounds=pounds, ounces=ounces)
    print "-------------------------------------"
    #filename = "usps_response.xml"
    #tidy(filename)