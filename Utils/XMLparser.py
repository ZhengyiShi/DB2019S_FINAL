import xml.etree.ElementTree as ET
import pandas as pd
import Utils

#mode: enum class in util
#returns a pandas dataframe
class XMLparser:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        
    def parse(self):
        etree = ET.parse(self.path)
        root = etree.getroot()
        
        dat = dict()
        
        for tag in self.mode:
            dat[tag.value] = []
            #print(tag)
        
        #print(dat.keys())
        
        #struct: <response><rows><rows><...content>
        for row in root[0]:
            for tag in self.mode:
                row_val = row.find(tag.value)
                if tag.value == "location":
                    dat[tag.value].append(row_val.attrib)
                elif row_val is not None:
                    dat[tag.value].append(row_val.text)
                else:
                    dat[tag.value].append("")
        
        return pd.DataFrame(data=dat)