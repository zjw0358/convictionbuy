import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
#import sys


def send_mail(attachment):
    test_str="daily report"
    me="wirelesser@hotmail.com"
    me_password="Cv60faqq"
    you="wirelesser@gmail.com"
    msg = MIMEMultipart()
    msg['Subject'] = test_str
    msg['From'] = me
    msg['To'] = you
    msg.preamble = test_str
    '''
    msg_txt = ("<html>"
                "<head></head>"
                "<body>"
                    "<h1>Yey!!</h1>"
                    "<p>%s</p>"
                "</body>"
            "</html>" % test_str)
    msg.attach(MIMEText(msg_txt, 'html'))
    '''
    #attachment = "../cache/dailyreport_2015-12-05.pdf"
    ctype, encoding = mimetypes.guess_type(attachment)
    maintype, subtype = ctype.split('/', 1)
    fp = open(attachment, 'rb')
    msg_pdf = MIMEBase(maintype, subtype)
    msg_pdf.set_payload(fp.read())
    fp.close()
    # Encode the payload using Base64
    encoders.encode_base64(msg_pdf)
    # Set the filename parameter
    msg_pdf.add_header('Content-Disposition', 'attachment', filename=attachment)
    msg.attach(msg_pdf)
    # Now send or store the message
    #composed = msg.as_string()
    
    #print ctype,encoding
    #sys.exit()
    #msg.attach(MIMEText(file(attachment).read()))
    '''
    with open(attachment) as f:
        msg.attach(MIMEImage(f.read()))
        
    with open(attachment) as f:
        msg.attach(MIMEText(f.read()))
    '''
    smtp_conn = smtplib.SMTP("smtp.live.com", timeout=10)
    print "connection stablished"
    smtp_conn.starttls()
    smtp_conn.ehlo_or_helo_if_needed()
    smtp_conn.login(me, me_password)
    smtp_conn.sendmail(me, you, msg.as_string())
    smtp_conn.quit()

if __name__ == "__main__":
    send_mail()