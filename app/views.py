#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
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



HOMEPAGE = 'http://el.tropic.com.cn'

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

def index(request):
    msg = init_msg(request)

    return render_to_response('index.html', msg)



def login_ui(request):
    msg = init_msg(request)

    return render_to_response('login/login.html', msg)



def login_do(request):
    msg = init_msg(request)

    username = request.POST['username']
    password = request.POST['password']
    

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "user pass."
            if msg.has_key('next'):
                return HttpResponseRedirect( HOMEPAGE+ msg['next'])
            else:
                return HttpResponseRedirect( HOMEPAGE)


    return render_to_response('login/login.html', msg)

def log_out(request):
    logout(request)

    return HttpResponseRedirect(HOMEPAGE)

def videos_ui(request):
    msg = init_msg(request)

    return render_to_response('videos/videos.html', msg)


def upload_ui(request):
    msg = init_msg(request)

    return render_to_response('upload/upload.html', msg)

def wechat_pay(request):
    pass


