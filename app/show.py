#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
from views import wx_login_do

def index(request):
    try:
        wechat_user = WxAuth.get_user(request)

        if wechat_user != None:
            print "Wechat-User: ", wechat_user

            if check_wx_unionid(request, wechat_user) == True:
                wx_login_do(request, wechat_user)
        else:
            print "Wechat-User: None."

        index_info = IndexInfo.objects.all()
        msg = init_msg(request)
        msg['index_info'] = index_info

    except Exception, e:
        printError(e)

    if checkMobile(request):
        return videos_ui(request)
        #return render_to_response('mobile/index.html', msg)
    else:
        return render_to_response('index.html', msg)

def mobile_index(request):
    try:
        wechat_user = WxAuth.get_user(request)

        if wechat_user != None:
            print "Wechat-User: ", wechat_user

            if check_wx_unionid(request, wechat_user) == True:
                wx_login_do(request, wechat_user)
        else:
            print "Wechat-User: None."

    except Exception, e:
        printError(e)

    msg = init_msg(request)


    if checkMobile(request):
        return render_to_response('mobile/index.html', msg)
    else:
        return render_to_response('index.html', msg)

def videos_ui(request):

    msg = init_msg(request)

    videos = Video.objects.all()
    videos, msg = get_order_videos(request, videos, msg)

    total_page = (getLen(videos)+PAGE_SIZE-1)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1
    msg['total_page'] = total_page


    get_content = "/videos/?"
    for key in request.GET:
        if key != "page":
            get_content += "%s=%s&"%(key, request.GET[key])
    msg['get_content'] = get_content

    msg['intrest_videos'] = get_intrest_videos()

    if checkMobile(request):
        return render_to_response('mobile/videos/videos.html', msg)
    else:
        return render_to_response('videos/videos.html', msg)



def search_result(request):

    msg = init_msg(request)

    #videos, msg = get_order_videos(request, msg)
    videos = get_search_videos(request)
    videos, msg = get_order_videos(request, videos, msg)

    total_page = (getLen(videos)+PAGE_SIZE-1)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    get_content = "/search/?"
    for key in request.GET:
        if key != "page":
            get_content += "%s=%s&"%(key, request.GET[key])
    msg['get_content'] = get_content

    msg['intrest_videos'] = get_intrest_videos()


    if checkMobile(request):
        return render_to_response('mobile/videos/search_result.html', msg)
    else:
        return render_to_response('videos/search_result.html', msg)
