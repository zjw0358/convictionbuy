'''
this is the main portal of conviction buy program

'''

#import os
#import sys
#from subprocess import Popen, PIPE
import subprocess
import marketscan
import marketscan
import ms_config
from collections import OrderedDict
from cb_email import send_mail

#pdf
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
import pandas as pd


'''
class multidict(dict):
    _unique = 0

    def __setitem__(self, key, val):
        print "setitem",key,val
        if isinstance(val, dict) and key in self:
            #print key,val,"isinstance dict"
            self._unique += 1
            key += str(self._unique)
            #print "insert",key
        dict.__setitem__(self, key, val)
        #print "insert",key,val
'''

class CbTasks:
    def __init__(self):
        #self.configFile = "cb_config.cfg"
        #self.cbparser = ConfigParser.RawConfigParser()        
        #self.cbparser = ConfigParser.RawConfigParser(None, multidict)
        self.msconfig = ms_config.MsDataCfg("cb_task.cfg") #file name
        self.datacfg = ms_config.MsDataCfg("")
        self.scaner = marketscan.MarketScan()
        self.dfdict=OrderedDict()
        pass
        
    def process0(self):
        #save daily output filename
        folder = self.datacfg.getDataConfig("folder","../cache/")        
        output = folder + "dailyreport_" + self.datacfg.getFileSurfix() + ".txt"
        self.datacfg.saveDataConfig('output_report',output)
        of = self.datacfg.getDataConfig("output_report")
        
        with open(of, "w") as myfile:
            myfile.write("===== Daily Report =====")    
        
        for sect in self.msconfig.getSections():
            cmdstr = self.msconfig.getConfig(sect,'cmd')
            with open(of, "a") as reportfile:
                print >>reportfile, "\n\n[ ",sect," ]\n"
                print >>reportfile, cmdstr
                
            print sect
            print cmdstr
            if (cmdstr!=""):
                p = subprocess.Popen("python "+cmdstr,stdin=PIPE, stderr=PIPE,stdout=PIPE) #stdout=PIPE, 
                
                #p = Popen(['program', 'arg1'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output, err = p.communicate(b"input data that is passed to subprocess' stdin")
                rc = p.returncode
                print type(output)
                #wait until it complete?     
                p.wait()
                print('Finished process')               
            
        pass
 
    def process(self):
        #save daily output filename
        folder = self.datacfg.getDataConfig("folder","../cache/")        
        output = folder + "dailyreport_" + self.datacfg.getFileSurfix() + ".txt"
        self.datacfg.saveDataConfig('output_report',output)
        of = self.datacfg.getDataConfig("output_report")
        
        with open(of, "w") as myfile:
            myfile.write("===== Daily Report =====")    
        
        for sect in self.msconfig.getSections():
            cmdstr = self.msconfig.getConfig(sect,'cmd')
            paramstr = self.msconfig.getConfig(sect,'param')
            
            with open(of, "a") as reportfile:
                print >>reportfile, "\n\n[ ",sect," ]\n"
                print >>reportfile, cmdstr
                
            print sect
            #print paramstr
            if (cmdstr!=""):
                df = self.scaner.process(paramstr)
                self.dfdict[sect] = df
                print('Finished process')               
     
        self.printPdf()
        pass
        
    def openPdf(self):
        folder = self.datacfg.getDataConfig("folder","../cache/")        
        self.output = folder + "dailyreport_" + self.datacfg.getFileSurfix() + ".pdf"
        self.elements = []
        self.styles = getSampleStyleSheet()
        self.doc = SimpleDocTemplate(self.output, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        self.doc.pagesize = landscape(A4)
        
    def writePdf(self,title, df):
        '''
        PATH_OUT = "./"        
        elements = []        
        styles = getSampleStyleSheet()       
        doc = SimpleDocTemplate('Report_File.pdf', pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        doc.pagesize = landscape(A4)
        '''
        self.elements.append(Paragraph(title, self.styles['Title']))
        
        lista = [df.columns[:,].values.astype(str).tolist()] + df.values.tolist()
        
        ts = [('ALIGN', (1,1), (-1,-1), 'CENTER'),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.purple),
            ('LINEBELOW', (0,0), (-1,0), 1, colors.purple),
            ('FONT', (0,0), (-1,0), 'Times-Bold'),
            ('LINEABOVE', (0,-1), (-1,-1), 1, colors.purple),
            ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.purple, 1, None, None, 4,1),
            ('LINEBELOW', (0,-1), (-1,-1), 1, colors.red),
            ('FONT', (0,-1), (-1,-1), 'Times-Bold'),
            ('BACKGROUND',(1,1),(-2,-2),colors.grey),
            ('TEXTCOLOR',(0,0),(1,-1),colors.black)]
        
        table = Table(lista, style=ts)
        self.elements.append(table)
        
    def closePdf(self):        
        self.doc.build(self.elements)
                
    def printPdf(self):
        self.openPdf()
        for key in self.dfdict:
            df = self.dfdict[key]
            self.writePdf(key,df)
        self.closePdf()
        send_mail(self.output)
        pass
        
if __name__ == "__main__":
    obj = CbTasks()
    obj.process()
 
 
 
 
 