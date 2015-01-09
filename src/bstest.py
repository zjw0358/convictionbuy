from bs4 import BeautifulSoup
import urllib2
import re
import datetime

'''url="http://www.utexas.edu/world/univ/alpha/"
page=urllib2.urlopen(url)
soup = BeautifulSoup(page.read())

universities=soup.findAll('a',{'class':'institution'})
for eachuniversity in universities:
    print eachuniversity['href']+","+eachuniversity.string'''
    
'''url="http://www.zacks.com/stock/research/msft/earnings-announcements"
page=urllib2.urlopen(url)
soup = BeautifulSoup(page.read())
allitems=soup.findAll('script')'''

fp = open("retest.txt",'r',-1)
#input_str = fp.read()

input_str="var OMNITURE_S_ACCOUNT_JS   = '';"


#earning_exp = '^window.app_data_earnings[\d\D]*\\"data\\"[ :\[]*(.*)]'
earning_exp ='^window.app_data_earnings[\d\D]*\\"data\\"[ :\\[]*(.*)]'
print input_str
an = re.match(earning_exp,input_str)

if an!=None:
    str1=an.group(1)
    erlst=[]
    for pairstr in str1.split(','):
        name,value = pairstr.split(':')
    
        #name = name.replace("{", "") 
        name=re.sub('[{} "]','',name)
        #print name,value
        if name=='Date':
            value=re.sub('[ "]','',value)
            d = datetime.datetime.strptime(value, '%m/%d/%Y')
            erlst.append(d)
    print erlst

else:
    str1=""
print an


'''for index,item in enumerate(allitems):
    an = re.match(earning_exp,item.string)
    print index,"=",an'''

