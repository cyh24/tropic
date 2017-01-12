#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
import random
import datetime

def banji_course(request):
    msg = init_msg(request)
    try:
        pass
    except Exception, e:
        print "banji_course:", str(e)

    return render_to_response('banji/banji_course.html', msg)

def courses(request):
    msg = init_msg(request)
    try:
        msg['cur_page'] = 0
    except Exception, e:
        print "banji_courses:", str(e)

    return render_to_response('banji/courses.html', msg)

@super_user
def upload_banji_course_ui(request):
    msg = init_msg(request)

    return render_to_response('banji/upload_banji_course.html', msg)

def upload_banji_course_post(request):
    pass
