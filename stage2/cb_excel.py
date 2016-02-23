import xlsxwriter
class cb_excel:
    def saveExcelFile(self, table, saveFileName, offset=2):
        # save to excel
        #try:
        outputFnXls = self.outputpath + saveFileName + datetime.datetime.now().strftime("%Y-%m-%d") + '.xls'
        writer = pandas.ExcelWriter(outputFnXls, engine='xlsxwriter')
        table.to_excel(writer, index=False, sheet_name='report')
        workbook = writer.book
        worksheet = writer.sheets['report']

        format1 = workbook.add_format({'bg_color': '#FFC7CE','font_color': '#9C0006','bold': True})
        format2 = workbook.add_format({'bg_color': '#C6EFCE','font_color': '#006100','bold': True})
        #find the two largest and smallest value
        #offset = 2 #symbol,exg
        for col in table:
            if col=='symbol' or col=='exg':
                continue
            lvalue = table[col].max()
            svalue = table[col].min()
            lidx = table[col].idxmax()
            sidx = table[col].idxmin()
            #print lidx,lvalue,sidx,svalue
            #worksheet.write('B1', 'Cost', format1)
            worksheet.write_string(lidx+1,offset,str(lvalue),format1)
            worksheet.write_string(sidx+1,offset,str(svalue),format2)
            offset+=1

        writer.save()
        print "Finish wrote to ", outputFnXls
        #except:
        #    print "exception when write to excel ",outputFnXls
        pass