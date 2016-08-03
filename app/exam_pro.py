#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *

def contestRoom(request):
    msg = init_msg(request)

    try:
        offline_exams = Exam.objects.all().order_by('-release_date')

        total_page = (getLen(offline_exams)+PAGE_SIZE-1)/PAGE_SIZE
        subExams, cur_page = paginator_show(request, offline_exams, PAGE_SIZE)

        pages_before, pages_after = paginator_bar(cur_page, total_page)

        msg['offexams'] = subExams
        msg['cur_page']   = cur_page
        msg['pages_before'] = pages_before
        msg['pages_after']  = pages_after
        msg['pre_page']   = cur_page - 1
        msg['after_page'] = cur_page + 1
        msg['total_page'] = total_page

    except Exception, e:
        print "contestRoom:", e

    return render_to_response('onlineExam/contestRoom.html', msg)

def exam_summary(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/examSummary.html', msg)

def single_select(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/single_select.html', msg)

def multi_select(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/multi_select.html', msg)
