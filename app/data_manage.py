#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
from excel_analyze import excel_analyze
import random
import datetime
import json

def analyze_exam_data(exam, msg):
    try:
        kaoshis = Kaoshi.objects.filter(exam=exam).all().order_by("-release_date")
        kscs = getLen(kaoshis)

        account_map = {}
        ckrs = 0
        tgrs = 0
        count = 0
        for i, kaoshi in enumerate(kaoshis):
            count += 1
            kaoshis[i].no = count
            if kaoshi.submit_flag == False:
                continue
            account_id = kaoshi.account
            if account_map.has_key(account_id) == False:
                ckrs += 1
                account_map[account_id] = kaoshi.score
            else:
                account_map[account_id] = max(account_map[account_id], kaoshi.score)

        for k in account_map:
            if account_map[k] >= 60:
                tgrs += 1

        msg['kaoshis'] = kaoshis
        msg['exam_title'] = exam.title

        msg['ckrs_str'] = "%d/%d"%(ckrs, exam.allow_accounts_num)
        msg['ckrs'] = ckrs
        msg['kscs'] = kscs
        msg['tgrs_str'] = "%d/%d"%(tgrs, ckrs)
        msg['tgrs'] = tgrs
        msg['qkrs'] = max(0, exam.allow_accounts_num - ckrs)
        # area_data = [{
                                    # "period": '2010 Q1',
                                    # "iphone": 2666,
                                    # "ipad": 0,
                                    # "itouch": 2647
                                # }, {
                                    # "period": '2010 Q2',
                                    # "iphone": 2778,
                                    # "ipad": 2294,
                                    # "itouch": 2441
                                # }, {
                                    # "period": '2010 Q3',
                                    # "iphone": 4912,
                                    # "ipad": 1969,
                                    # "itouch": 2501
                                # }, {
                                    # "period": '2010 Q4',
                                    # "iphone": 3767,
                                    # "ipad": 3597,
                                    # "itouch": 5689
                                # }, {
                                    # "period": '2011 Q1',
                                    # "iphone": 6810,
                                    # "ipad": 1914,
                                    # "itouch": 2293
                                # }, {
                                    # "period": '2011 Q2',
                                    # "iphone": 5670,
                                    # "ipad": 4293,
                                    # "itouch": 1881
                                # }, {
                                    # "period": '2011 Q3',
                                    # "iphone": 4820,
                                    # "ipad": 3795,
                                    # "itouch": 1588
                                # }, {
                                    # "period": '2011 Q4',
                                    # "iphone": 15073,
                                    # "ipad": 5967,
                                    # "itouch": 5175
                                # }, {
                                    # "period": '2012 Q1',
                                    # "iphone": 10687,
                                    # "ipad": 4460,
                                    # "itouch": 2028
                                # }, {
                                    # "period": '2012 Q2',
                                    # "iphone": 8432,
                                    # "ipad": 5713,
                                    # "itouch": 1791
                                # }]
        # month_days = getThismonthDays(datetime.datetime.now())

        # msg['area_data'] = json.dumps(area_data)

    except Exception, e:
        print "analyze_exam_data: ", str(e)

    return msg

def exam_data(request):
    msg = init_msg(request)
    try:
        exam_id = int(request.GET['exam_id'])
        exam = Exam.objects.filter(id=exam_id).all()[0]

        msg = analyze_exam_data(exam, msg)

    except Exception, e:
        print "exam_data:", str(e)

    return render_to_response('dataManage/exam_data.html', msg)
