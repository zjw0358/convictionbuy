#import reportlab
#from reportlab.lib.pagesizes import letter
#from reportlab.pdfgen import canvas


import os,sys
#from PyPDF2 import PdfFileWriter, PdfFileReader
from pyPdf import PdfFileWriter, PdfFileReader


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,NextPageTemplate 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, inch, landscape
        
import cgi
import tempfile
import win32api

class cb_report:
    def process0(self):        
        cv = canvas.Canvas("form.pdf", pagesize=letter)
        cv.setLineWidth(.3)
        cv.setFont('Helvetica', 12)
        
        cv.drawString(30,750,'OFFICIAL COMMUNIQUE')
        cv.drawString(30,735,'OF ACME INDUSTRIES')
        cv.drawString(500,750,"12/12/2010")
        cv.line(480,747,580,747)
        
        cv.drawString(275,725,'AMOUNT OWED:')
        cv.drawString(500,725,"$1,000.00")
        cv.line(378,723,580,723)
        
        cv.drawString(30,703,'RECEIVED BY:')
        cv.line(120,700,580,700)
        cv.drawString(120,703,"JOHN DOE")
        
        cv.save()        
        pass
    def process1(self):
        cv = canvas.Canvas("form.pdf", pagesize=letter)
        cv.setLineWidth(.3)
        cv.setFont('Helvetica', 8)
        f = open('dailyreport.txt', 'r')
        y = 750
        for line in f:
            cv.drawString(30,y,line)
            y = y - 15
            print line
        f.close()
        cv.save()

    def process2(self):
        print "starting"

        #files = [os.path.join(sys.argv[1],file) for file in os.listdir(sys.argv[1])]
        output = PdfFileWriter()


        #input = PdfFileReader(open('dailyreport.txt',"r"))
        input = PdfFileReader(file("cb_report.py","rb"))

        for page in range(0,input.getNumPages()):
            print "\tadding page %d" % page
            output.addPage(input.getPage(page))
        outputFile = 'dailyreport.pdf' #sys.argv[2]
        outStream = open(outputFile,"wb")
        output.write(outStream)
        outStream.close()
        
    def process3(self):  
        '''          
        source_file_name = "dailyreport.txt"
        pdf_file_name = "dailyreport.pdf"
        #pdf_file_name = tempfile.mktemp (".pdf")
        

#from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
#from reportlab.lib.styles import getSampleStyleSheet
 



        
        styles = getSampleStyleSheet ()
        h1 = styles["h1"]
        normal = styles["Normal"]
        
        #doc = SimpleDocTemplate (pdf_file_name)
        doc = SimpleDocTemplate(pdf_file_name, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        doc.pagesize = landscape(A4)
        #elements = []


        #
        # reportlab expects to see XML-compliant
        #  data; need to escape ampersands &c.
        #
        text = cgi.escape (open (source_file_name).read ()).splitlines ()
        
        #
        # Take the first line of the document as a
        #  header; the rest are treated as body text.
        #
        
                       
        story = [Paragraph (text[0], h1)]
        for line in text[1:]:
            #story.append(NextPageTemplate('landscape'))
            story.append (Paragraph (line, normal))
            story.append (Spacer (1, 0.2 * inch))
        
        doc.build (story)
        '''
        win32api.ShellExecute (0, "print", "dailyreport.txt", None, ".", 0)     
        
    def process(self):
        output = PdfFileWriter()


        #input = PdfFileReader(open('dailyreport.txt',"r"))
        input1 = PdfFileReader(file("Report_File.pdf","rb"))
        input2 = PdfFileReader(file("dailyreport.pdf","rb"))
        lst=[input1,input2]
        for item in lst:
            for page in range(0,item.getNumPages()):
                print "\tadding page %d" % page
                output.addPage(item.getPage(page))
                
        outputFile = 'merge.pdf' #sys.argv[2]
        outStream = open(outputFile,"wb")
        output.write(outStream)
        outStream.close()
        
if __name__ == "__main__":
    obj = cb_report()
    obj.process()
 
 