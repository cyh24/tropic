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
from qiniu_pro import *
from db_pro import *



HOMEPAGE = 'http://127.0.0.1:9999'
PAGE_SIZE = 16

@csrf_exempt 

@csrf_protect 
def paginator_show(request, msg_list, page_size):
    #after_range_num  = 5
    #before_range_num = 6
    page = 1
    try:
        if request.GET.has_key('page'):
            page = int(request.GET['page'])
        if page < 1:
            page = 1

        total_page = (len(msg_list) + page_size)/page_size
        if page > total_page:
            page = total_page
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
    return msg_list, page



def init_msg(request):
    msg = {}
    msg['login_state'] = False
    if request.user.is_authenticated():
        msg['login_state'] = True

    msg['next'] = '/'
    if request.GET.has_key('next'):
        msg['next'] = request.GET['next']

    return msg

def test(request):
    print "TEST"
    msg = init_msg(request)

    return render_to_response('test.html', msg)


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

def paginator_bar(cur_page, total_page):
    pages_before = []
    pages_after  = []
    Num = 5

    if total_page <= Num:
        for i in range(cur_page-1):
            pages_before.append(i+1)
        for i in range(cur_page+1, total_page+1):
            pages_after.append(i+1)
    elif cur_page <= Num/2:
        for i in range(cur_page-1):
            pages_before.append(i+1)
        for i in range(cur_page, cur_page+Num/2+1):
            pages_after.append(i+1)
    elif (total_page - cur_page) <= Num/2:
        for i in range(total_page - Num, cur_page-1):
            pages_before.append(i+1)
        for i in range(cur_page, total_page):
            pages_after.append(i+1)
    else:
        for i in range(cur_page-Num/2-1, cur_page-1):
            pages_before.append(i+1)
        for i in range(cur_page, cur_page + Num/2):
            pages_after.append(i+1)

    return pages_before, pages_after


def videos_ui(request):

    msg = init_msg(request)

    videos, msg = get_order_videos(request, msg)

    total_page = (len(videos)+PAGE_SIZE)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    msg['interest_videos'] = get_interest_videos()

    return render_to_response('videos/videos.html', msg)

def play_ui(request):
    msg = init_msg(request)

    if request.GET.has_key('video-id'):
        try:
            video_id = int(request.GET['video-id'])
            video = Video.objects.filter(id=video_id).all()
            if video != None:
                video = video[0]
                msg['video'] = video
            else:
                 return render_to_response('videos/play-error.html', msg)

            key = video.key
            video_url = Qiniu.download_private_url("oceans-clip_clip.mp4")
            
            msg['video_url'] = video_url
            print "Video URL: ", video_url

            add_watch_num(video_id)
            return render_to_response('videos/play.html', msg)

        except Exception, e:
            print "error: ", str(e)
    
    
    return render_to_response('videos/play-error.html', msg)



def space_index(request):
    msg = init_msg(request)

    return render_to_response('space/index.html', msg)

def setprofile(request):
    msg = init_msg(request)

    return render_to_response('space/setprofile.html', msg)

def setavator(request):
    msg = init_msg(request)

    return render_to_response('space/setavator.html', msg)

def setbindsns(request):
    msg = init_msg(request)

    return render_to_response('space/setbindsns.html', msg)

@login_required(login_url='/login/')
@csrf_protect
def upload_ui(request):
    data = init_msg(request)
    data['domain']       = DOMAIN
    data['uptoken_url']  = 'uptoken'
    return render_to_response('upload/upload.html', data)




