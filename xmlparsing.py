
"""
Author: Ameet Chitnis

Description: A simple script to parse the contents of an XML file and extract the details of all financial instruments

"""

import requests
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import csv

firstFileName = 'FirstFile.xml'
firstFileURL = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2020-01-08T00:00:00Z+TO+2020-01-08T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"

"""
This is a generic method to download a file given its URL

"""


def downloadFile(url, fileName):

    resp = requests.get(url)

    with open(fileName, 'wb') as f:
        f.write(resp.content)


downloadFile(firstFileURL, firstFileName)

"""
A method to parse the first XML file and return a dictionary containing the download links

"""


def parseFirstXML():

    tree = ET.parse(firstFileName)
    download_links = {}
    url = ''
    i = 0

    for doc in tree.getroot().findall("./result/doc"):

        for child in doc:

            attributes = dict(child.attrib)

            if (attributes.get("name") == "download_link"):
                url = child.text
            elif (attributes.get("name") == "file_type" and child.text == 'DLTINS'):
                download_links.update({child.text+str(i): url})
                i += 1


    return download_links


dl = parseFirstXML()

secondFileURL = dl.get("DLTINS0")
secondZipFileName = secondFileURL[secondFileURL.rindex("/")+1:]

secondFileName = secondZipFileName.replace(".zip", ".xml")

print(secondFileName)

downloadFile(secondFileURL, secondZipFileName)

"""
A method to extract the contents of a zip file

"""

def extractZipFile(fileName):

    with ZipFile(fileName, 'r') as zip:
        zip.printdir()
        zip.extractall()



extractZipFile(secondZipFileName)

fdata = []

"""
A method to flatten the tree structure of an XML, using a depth first search algorithm
Uses a filter to collect only those lines which contain the keys 
".FinInstrmGnlAttrbts_" or ".Issr_"

"""


def flatten(runningPath, complexObject):
    global fdata

    if (complexObject.__len__() == 0):

        if ( (".FinInstrmGnlAttrbts_" in runningPath) or (".Issr_" in runningPath) ):
            fdata.append(runningPath)

        return

    for each_item in complexObject:
        flatten(runningPath + "." + each_item.tag.split("}")[1].strip() + "_" + str(
            each_item.attrib).strip() + "_" + str(each_item.text).strip(), each_item)


flatten("", ET.parse(secondFileName).getroot())

mdicts = {}
count = 0
outputData = []

"""
Prepare a datastructure to hold all the financial instruments. This will eventually be dumped into a CSV

"""


for each_item in fdata:

    fval = each_item[each_item.rfind("_") + 1:]

    if (".Id_" in each_item):
        mdicts.update({"FinInstrmGnlAttrbts.Id": fval})
        count += 1
    elif (".FullNm_" in each_item):
        mdicts.update({"FinInstrmGnlAttrbts.FullNm": fval})
        count += 1
    elif (".ClssfctnTp_" in each_item):
        mdicts.update({"FinInstrmGnlAttrbts.ClssfctnTp": fval})
        count += 1
    elif (".CmmdtyDerivInd_" in each_item):
        mdicts.update({"FinInstrmGnlAttrbts.CmmdtyDerivInd": fval})
        count += 1
    elif (".NtnlCcy_" in each_item):
        mdicts.update({"FinInstrmGnlAttrbts.NtnlCcy": fval})
        count += 1
    elif (".Issr_" in each_item):
        mdicts.update({"FinInstrmGnlAttrbts.Issr": fval})
        count += 1

    if(count == 6):
        count = 0
        outputData.append(mdicts)
        mdicts = {}

fields = ['FinInstrmGnlAttrbts.Id', 'FinInstrmGnlAttrbts.FullNm', 'FinInstrmGnlAttrbts.ClssfctnTp',
          'FinInstrmGnlAttrbts.CmmdtyDerivInd', 'FinInstrmGnlAttrbts.NtnlCcy', 'FinInstrmGnlAttrbts.Issr']

outfileName = "outputdata.csv"

with open(outfileName, 'w') as csvfile:

    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(outputData)





