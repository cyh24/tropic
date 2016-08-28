# -*- coding: utf-8 -*-
import sys
import  xdrlib
import xlrd

def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception,e:
        print str(e)

def excel_analyze(file):
    data = open_excel(file)
    return excel_analyze_by_content(data)

def excel_analyze_by_content(data):
    single_Q = []
    multi_Q = []
    try:
        table = data.sheets()[0]
        i = 0
        while (i < table.nrows) == True:
            kind = 0
            row = table.row_values(i)
            if row[0].strip() == "":
                i += 1
                continue

            row_kind = row[0].strip()
            if row_kind == "单选".decode('utf8'):
                kind = 1
            elif row_kind == "多选".decode('utf8'):
                kind = 2
            else:
                i += 1
                continue


            tmp_q = {}
            tmp_q['kind'] = kind
            tmp_q['answers'] = []
            tmp_q['choices'] = []

            i += 1
            while (i < table.nrows) == True:
                row = table.row_values(i)
                if row[0].strip() == "".decode('utf8'):
                    i += 1
                    continue
                else:
                    tmp_q['title'] = row[0]
                    i += 1
                    break

            while (i < table.nrows) == True:

                row = table.row_values(i)
                if row[0].strip() == "".decode('utf8'):
                    i += 1
                    continue

                if row[0].strip() == "分数".decode('utf8'):
                    tmp_q['score'] = float(row[1])
                    break

                if row[1] == '':
                    tmp_q['answers'].append(0)
                else:
                    tmp_q['answers'].append(1)

                tmp_q['choices'].append(row[0].strip())

                i += 1

            if kind == 1:
                single_Q.append(tmp_q)
            elif kind == 2:
                multi_Q.append(tmp_q)

    except Exception, e :
        print "Error in analyze excel: ", e
        return None, None

    return single_Q, multi_Q

if __name__=="__main__":
    excel_analyze(sys.argv[1])
