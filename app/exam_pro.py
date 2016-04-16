#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *

def online_exam(request):
    msg = init_msg(request)

    try:
        offline_courses = Offline.objects.all().order_by('-release_date')

        total_page = (getLen(offline_courses)+PAGE_SIZE-1)/PAGE_SIZE
        subCourses, cur_page = paginator_show(request, offline_courses, PAGE_SIZE)

        pages_before, pages_after = paginator_bar(cur_page, total_page)

        msg['offcourses'] = subCourses
        msg['cur_page']   = cur_page
        msg['pages_before'] = pages_before
        msg['pages_after']  = pages_after
        msg['pre_page']   = cur_page - 1
        msg['after_page'] = cur_page + 1
        msg['total_page'] = total_page

    except Exception, e:
        print "offline:", e

    return render_to_response('onlineExam/onlineExam.html', msg)
    # if checkMobile(request):
        # return render_to_response('mobile/offline/offline.html', msg)
    # else:
        # return render_to_response('offline/offline.html', msg)

def single_select(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/single_select.html', msg)

def multi_select(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/multi_select.html', msg)
