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
from wechat_pro import *


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

        total_page = (get_len(msg_list) + page_size)/page_size
        if page > total_page:
            page = total_page
    except ValueError:
        page = 1

    
    try:
        paginator = Paginator(msg_list, page_size)
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
    try:
        wechat_user = WxAuth.get_user(request)

        if wechat_user != None:
            print "Wechat-User: ", wechat_user

            if check_wx_openid(wechat_user) == True:
                wx_login_do(request, wechat_user)
        else:
            print "Wechat-User: None."

    except Exception, e:
        printError(e)

    msg = init_msg(request)


    return render_to_response('index.html', msg)



def login_ui(request):
    msg = init_msg(request)

    return render_to_response('login/login.html', msg)

def wechat_login(request):
    #login_url = "https://open.weixin.qq.com/connect/qrconnect?appid=%s&redirect_uri=%s&response_type=%s&scope=%s&state=%s#wechat_redirect"%(APP_ID, REDIRECT_URL, RESPONSE_TYPE, SCOPE, STATE)
    login_url = WxAuth.get_authorize_url(request)

    return HttpResponseRedirect(login_url)

def wechat_share(request):
    url = "http://facebuaa.cn"
    if request.GET.has_key('cur_url'):
        url = request.GET['cur_url']

    qrcode_url = get_qrcode(url)
    print qrcode_url
    json={'qrcode_url': qrcode_url}

    return JsonResponse(json)

def excute_login(request, username, password):
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print "user pass."
    except Exception, e:
        printError(e)


def wx_login_do(request, user):
    username = user['openid']
    password = "Z!"+username+"1!"

    excute_login(request, username, password)

def login_do(request):
    msg = init_msg(request)

    username = request.POST['username']
    password = request.POST['password']
    

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "user pass."

            # judge whether db exist accout related to the user.
            exist_user_account(user)

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

    videos = Video.objects.all()
    videos, msg = get_order_videos(request, videos, msg)

    total_page = (get_len(videos)+PAGE_SIZE)/PAGE_SIZE
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


def videos_manage(request):
    msg = init_msg(request)
    return render_to_response('videos/videos-manage.html', msg)


def search_result(request):

    msg = init_msg(request)

    #videos, msg = get_order_videos(request, msg)
    videos = get_search_videos(request)

    total_page = (get_len(videos)+PAGE_SIZE)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    msg['interest_videos'] = get_interest_videos()

    return render_to_response('videos/search_result.html', msg)

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
            video_url = Qiniu.download_private_url(key)
            
            msg['video_url'] = video_url
            # add the watch number
            add_watch_num(video_id)

            try:
                # get the video's comments
                comments = Video.objects.filter(id=video_id)[0].comments.all().order_by('release_date')
                new_comments = []
                if get_len(comments) > 0:
                    for cc in comments:
                        cc.release_date = str(cc.release_date).split(' ')[0]
                        new_comments.append(cc)

                msg['comments'] = new_comments
                msg['comments_num'] = get_len(comments)
            except Exception, e:
                printError(e)


            # check whether need pay for the play
            if video.money <= 0:
                return render_to_response('videos/play.html', msg)
            else:
                return render_to_response('videos/play-prohibited.html', msg)

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


def voteup(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            add_like_num(video_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)

@login_required(login_url='/login/')
@csrf_protect
def comment_add(request):
    json = {}
    try:
       add_comment(request)

    except Exception, e:
        printError(e)

    return JsonResponse(json)
