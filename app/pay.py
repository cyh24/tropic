#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse,HttpResponseRedirect 
from django.shortcuts import render_to_response 
from django.template import RequestContext 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.csrf import csrf_protect 
from django.template.context_processors import csrf
from django.template import loader

from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


from models import *
import time
import os
import sys

#Terry add import
from app.wechat_pay import NativeLink_pub, UnifiedOrder_pub
import qrcode
from cStringIO import StringIO
import random
import string

HOMEPAGE = 'http://127.0.0.1:8888'

@csrf_exempt 

@csrf_protect 
def paginator_show(request, msg_list, page_size=16):
    #after_range_num  = 5
    #before_range_num = 6
    try:
        page = 1
        #page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    paginator = Paginator(msg_list, page_size)
    
    try:
        msg_list = paginator.page(page)
    except(EmptyPage, PageNotAnInteger):
        msg_list = paginator.page(1)

    #if page >= after_range_num:
    #    page_range = paginator.page_range[page - after_range_num: page + before_range_num]
    #else:
    #    page_range = paginator.page_range[0: int(page) + before_range_num]

    #template_var["page_objects"] = msg_list
    #template_var["page_range"]   = page_range
    return msg_list



def init_msg(request):
    msg = {}
    msg['login_state'] = False
    if request.user.is_authenticated():
        msg['login_state'] = True

    msg['next'] = '/'
    if request.GET.has_key('next'):
        msg['next'] = request.GET['next']

    return msg


#二维码

def getRandomStr(num=5):#随机名
    
    current_time = time.strftime("%y%m%d%H%M%S", time.localtime())
    rand_str = ''.join(random.sample(string.ascii_letters + string.digits, num))

    return current_time + "-" + rand_str

def generate_qrcode(code_url):#生成二维码图片
    qr = qrcode.QRCode(version = 2,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size = 10, border = 1
    )
    qr.add_data(code_url)
    qr.make(fit=True)
    img = qr.make_image()
    return img

def wechat_pay(request):

    msg = init_msg(request)
    
    unifiedOrder = UnifiedOrder_pub()
    unifiedOrder.firmPara()
    prepay_id = unifiedOrder.getPrepayId()
    if prepay_id != "FALSE":
        code_url = unifiedOrder.result["code_url"]
        img = generate_qrcode(code_url)
        APP_PATH = os.path.dirname(os.path.dirname(__file__))
        STATIC_PATH = os.path.join(APP_PATH, 'app/static/images/').replace('\\','/')

        img_name = getRandomStr()+".png"
        msg['img_name'] = img_name
        outfile = os.path.join(STATIC_PATH, img_name) 
        img.save(outfile)
    else:
        msg['result'] = "FALSE"
    
    return render_to_response('WxPay/WxPay.html', msg)