import traceback
import perfdata

# delete records from tables: stockeod, stockmetadata
def reset(dbconn):    
    ret = perfdata.resetTable(dbconn)
    if ret == False:
        return ret

    cursor = dbconn.cursor()
    sql=""
    try:
        tb=""
        sql = "delete from stockeod"
        cursor.execute(sql)
        sql = "delete from stockmetadata"
        cursor.execute(sql)
        dbconn.commit()
        return True
    except:
        print "resetdb error in %s" % (sql)
        tb = traceback.format_exc()
        dbconn.rollback()
        return False
    finally:        
        print tb