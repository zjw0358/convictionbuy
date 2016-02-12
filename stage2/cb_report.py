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

'''
support chinese
http://blog.donews.com/limodou/archive/2005/08/22/521202.aspx
http://www.fredsneverland.com/blog/20/
'''
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib import fonts
import copy

class CbReport:
    def __init__(self):
        self.dfdict=OrderedDict()
        self.datacfg = ms_config.MsDataCfg("")
        folder = self.datacfg.getDataConfig("result","../result/")        
        self.output = folder + "dailyreport_" + self.datacfg.getFileSurfix() + ".pdf"
        self.windows = False
        pass
        
    def initFont(self):
        reportlab.rl_config.warnOnMissingFontGlyphs = 0
        #pdfmetrics.registerFont(TTFont('song', 'SURSONG.TTF'))
        pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))
        #pdfmetrics.registerFont(TTFont('hei', 'D:\\Windows\\fonts\\simkai.ttf'))

        #fonts.addMapping('song', 0, 0, 'song')
        #fonts.addMapping('song', 0, 1, 'song')
        #fonts.addMapping('song', 1, 0, 'hei')
        #fonts.addMapping('song', 1, 1, 'hei')
        fonts.addMapping('hei', 0, 0, 'hei')
        fonts.addMapping('hei', 0, 1, 'hei')
        fonts.addMapping('hei', 1, 0, 'hei')
        fonts.addMapping('hei', 1, 1, 'hei')
        self.windows = True
        
    def addTable(self,title,desc,df):
        self.dfdict[title] = desc,df
        
    def openPdf(self):
        self.elements = []
        self.styles = getSampleStyleSheet()
        self.doc = SimpleDocTemplate(self.output, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        self.doc.pagesize = landscape(A4)
        if (self.windows):
            self.descStyle = copy.deepcopy(self.styles['Normal'])
            self.descStyle.fontName ='hei'
            self.descStyle.fontSize = 12


    def writePdf(self,title, desc, df):      
        self.elements.append(Paragraph(title, self.styles['Title']))

        #styleCentered = ParagraphStyle(name="centeredStyle", alignment=TA_CENTER,fontName=baseFont)
        #line1 = Paragraph('24-Hour Delivery Service on<br />\n', styleCentered)
        #self.elements.append(line1)
        #desc=unicode(desc,'utf-8')
        text = "<para alignment=\"center\">%s</para>" % desc
        #text=desc
        #print text
        #styleText = self.styles['Normal']        

        if (self.windows):            
            self.elements.append(Paragraph(text, self.descStyle))

        
        self.elements.append(Spacer(1, 12))
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
        send_mail(self.output,self.datacfg.getFileSurfix(),self.windows)
        pass
        
    def process(self,desc):
       self.openPdf()
       df=pandas.DataFrame()
       key='title'
       #desc='中文'
       self.writePdf(key,desc,df)
       self.closePdf()
       pass     
if __name__ == "__main__":
    obj = CbReport()
    obj.process()