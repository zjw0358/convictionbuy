#import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
    def process(self):
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

        
        
if __name__ == "__main__":
    obj = cb_report()
    obj.process()
 
 