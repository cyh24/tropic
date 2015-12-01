#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *


def get_space_msg(request, get_videos_method):
    msg = init_msg(request)

    msg['videos'] = None

    msg['v_num']  = 0
    msg['cur_page']   = 0
    msg['total_page'] = 0
    msg['pre_page']   = 0
    msg['after_page'] = 0

    msg['history_num'] = 0
    msg['paid_num']    = 0
    msg['unpay_num']  = 0
    msg['collect_num'] = 0

    try:

        msg['history_num'] = get_watch_history_num(request.user)
        msg['paid_num']    = get_paid_num(request.user)
        msg['unpay_num']   = get_unpay_num(request.user)
        msg['collect_num'] = get_collect_num(request.user)

        videos, videos_num = get_videos_method(request.user)

        total_page = (getLen(videos)+8-1)/8
        subVideos, cur_page = paginator_show(request, videos, 8)


        msg['videos']     = subVideos
        msg['v_num']  = videos_num

        msg['cur_page']   = cur_page
        msg['total_page'] = total_page

        msg['pre_page']   = cur_page - 1
        msg['after_page'] = cur_page + 1
        
    
    except Exception, e:
        printError(e)

    return msg

@login_required(login_url='/wechat-login/')
@csrf_exempt
# watching history list
def space_index(request):
    msg = get_space_msg(request, get_watch_history)
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'


    if checkMobile(request):
        return render_to_response('mobile/space/history.html', msg)
    else:
        return render_to_response('space/history.html', msg)


@login_required(login_url='/wechat-login/')
@csrf_exempt
# watching history list
def space_collect(request):
    msg = get_space_msg(request, get_collect)
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    if checkMobile(request):
        return render_to_response('mobile/space/collect.html', msg)
    else:
        return render_to_response('space/collect.html', msg)


@login_required(login_url='/wechat-login/')
@csrf_exempt
# watching history list
def space_shopping_cart(request):
    msg = get_space_msg(request, get_unpay)
    
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    return render_to_response('space/unpay.html', msg)


@login_required(login_url='/wechat-login/')
@csrf_exempt
# watching history list
def space_paid(request):
    msg = get_space_msg(request, get_paid)
    
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    if checkMobile(request):
        return render_to_response('mobile/space/paid.html', msg)
    else:
        return render_to_response('space/paid.html', msg)


def setprofile(request):
    msg = init_msg(request)

    return render_to_response('space/setprofile.html', msg)

@login_required(login_url='/wechat-login/')
@csrf_exempt
def setavator(request):
    msg = init_msg(request)

    return render_to_response('space/setavator.html', msg)

def setbindsns(request):
    msg = init_msg(request)

    return render_to_response('space/setbindsns.html', msg)


def history_del(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            del_watch_history(request.user, video_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)

def collect_del(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            del_collect(request.user, video_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)

def unpay_del(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            del_unpay(request.user, video_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)



@login_required(login_url='/wechat-login/')
@csrf_protect
def random_pic(request):
    json = {}
    try:
        account = get_account_from_user(request.user)
        img = None
        if account.sex == 1:
            img = get_random(boy_imgs)
        elif account.sex == 0:
            img = get_random(girl_imgs)
        else:
            img = get_random(boy_imgs+girl_imgs)

        json['logo_pic'] = img
        account.user_pic = img
        account.save()

    except Exception, e:
        printError(e)

    return JsonResponse(json)


@login_required(login_url='/wechat-login/')
@csrf_protect
def update_profile(request):
    json = {}
    json['state'] = 'False'
    try:
        if update_account(request) == True:
            json['state'] = 'True'

    except Exception, e:
        printError(e)

    return JsonResponse(json)


@login_required(login_url='/wechat-login/')
@csrf_protect
@csrf_exempt
def update_pic(request):
    try: 
        path = None
        path_pic = "/static/storage/logo-images/150827142149-KPg1-tt.png"
        if request.FILES.has_key('pic'):
            path = USER_PIC_FOLD + getRandomStr() + "-" + request.FILES['pic'].name
            handle_uploaded_photo(path, request.FILES['pic'])
            path_pic = path[3:]

        account = get_account_from_user(request.user)
        account.user_pic = path_pic
        account.save()

    except Exception, e:
        print str(e)
    
    msg = init_msg(request)

    return render_to_response('space/setavator.html', msg)
    

