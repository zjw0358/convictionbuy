import traceback
#import datetime

#"DDD","3D Systems Corporation","31.78","3534479215.54","n/a","n/a","Technology","Computer Software: Prepackaged Software","http://www.nasdaq.com/symbol/ddd",
def importStockListFile(filename,dbconn):
    cursor = dbconn.cursor()
    file_object = open(filename, 'r', -1)
    file_object.readline() # skip first line
    tb=""
    try: 
        for line in file_object:
            columns = line.replace("\",\"","_").replace("\"","").split('_')
            #columns = line.split("\",\"")
            sql = "insert into Stocklist(symbol,name,lastprice,marketcap,sector,industry) values('%s','%s','%s','%s','%s','%s')" \
                    % (columns[0],columns[1],columns[2],columns[3],columns[6],columns[7])
            try:
                cursor.execute(sql)
                dbconn.commit()
            except:
                print "stocklist insert error=",sql
                #tb = traceback.format_exc()
    except:
        print "stocklist error"
        tb = traceback.format_exc()
        print tb
        dbconn.rollback()
    finally:        
        #print tb  
        file_object.close()
        print "import done"

def display(dbconn):
    cursor = dbconn.cursor()
    tb=""
    try: 
        sql = "select count(*) from Stocklist"
        cursor.execute(sql)
        result = cursor.fetchone()
        print "strocklist count=",result[0]
    except:
        print "stocklist display error"
        tb = traceback.format_exc()
        print tb      
        
def getSector(sym,dbconn):
    cursor = dbconn.cursor()
    tb=""
    try: 
        sql = "select sector from Stocklist where symbol='%s'" % (sym)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]
    except:
        print "stocklist getSector error"
        tb = traceback.format_exc()
        print tb


def usage():
    print "usage <reset|display|import> [filename]"

def process(args,dbconn):
    arglen = len(args)
    #print args
    if arglen==0:
        usage()
        return
    if args[0]=="import":
        if arglen<2:
            usage()
            return
        importStockListFile(args[1],dbconn)
    elif args[0]=="display":
        display(dbconn)