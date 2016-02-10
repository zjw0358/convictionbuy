# -*- coding: utf-8 -*-
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
#from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from collections import OrderedDict
from cb_email import send_mail
import ms_config
import pandas

class CbReport:
    def __init__(self):
        self.dfdict=OrderedDict()
        self.datacfg = ms_config.MsDataCfg("")
        folder = self.datacfg.getDataConfig("result","../result/")        
        self.output = folder + "dailyreport_" + self.datacfg.getFileSurfix() + ".pdf"

        pass
        
    def addTable(self,title,desc,df):
        self.dfdict[title] = desc,df
        
    def openPdf(self):
        self.elements = []
        self.styles = getSampleStyleSheet()
        self.doc = SimpleDocTemplate(self.output, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        self.doc.pagesize = landscape(A4)

    def writePdf(self,title, desc, df):
        '''
        PATH_OUT = "./"        
        elements = []        
        styles = getSampleStyleSheet()       
        doc = SimpleDocTemplate('Report_File.pdf', pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        doc.pagesize = landscape(A4)
        '''
        self.elements.append(Paragraph(title, self.styles['Title']))

        #styleCentered = ParagraphStyle(name="centeredStyle", alignment=TA_CENTER,fontName=baseFont)
        #line1 = Paragraph('24-Hour Delivery Service on<br />\n', styleCentered)
        #self.elements.append(line1)
        #desc=unicode(desc,'utf-8')
        #text = "<para alignment=\"center\">%s</para>" % desc
        text=desc
        print text
        styleText = self.styles['Normal']
        #styleText.wordWrap='CJK'
        self.elements.append(Paragraph(text, styleText))

        if len(df)==0:
            return
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
            desc,df = self.dfdict[key]
            self.writePdf(key,desc,df)
        self.closePdf()
        send_mail(self.output,self.datacfg.getFileSurfix())
        pass
        
    def process(self):
       self.openPdf()
       df=pandas.DataFrame()
       key='title'
       desc=u'中文'
       self.writePdf(key,desc,df)
       self.closePdf()
       pass     
if __name__ == "__main__":
    obj = CbReport()
    obj.process()