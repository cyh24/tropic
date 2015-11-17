#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *

@login_required(login_url='/login/')
@csrf_exempt
def videos_data(request):
    msg = init_msg(request)
    return render_to_response('videos/videos-data.html', msg)

@login_required(login_url='/login/')
@csrf_exempt
def videos_manage(request):
    msg = init_msg(request)

    videos = Video.objects.all()

    #videos, msg = get_order_videos(request, videos, msg)

    if getLen(videos) > 0:
        new_videos = []
        for v in videos:
            v.release_date = str(v.release_date).split(' ')[0]
            new_videos.append(v)
        videos = new_videos

    total_page = (getLen(videos)+5-1)/5
    subVideos, cur_page = paginator_show(request, videos, 5)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    intrest_videos = []
    for iv in IntrestVideos.objects.all():
        intrest_videos.append(iv.video)

    for i in range(getLen(subVideos)):
        if subVideos[i] in intrest_videos:
            subVideos[i].intrest_flag = 1
        else:
            subVideos[i].intrest_flag = 0

    msg['videos']     = subVideos
    msg['videos_len'] = len(videos)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    msg['intrest_videos'] = get_intrest_videos()

    return render_to_response('videos/videos-manage.html', msg)


@login_required(login_url='/login/')
@csrf_exempt
def delete_video(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            if db_delete_video(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)


@login_required(login_url='/login/')
@csrf_exempt
def delete_intrestvideo(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            if db_delete_intrestvideo(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)

@login_required(login_url='/login/')
@csrf_exempt
def add_intrestvideo(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            if db_add_intrestvideo(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)

@login_required(login_url='/login/')
@csrf_protect
def upload_course_ui(request):
    data = init_msg(request)

    return render_to_response('upload/upload_course.html', data)




@login_required(login_url='/login/')
@csrf_protect
def update_course_ui(request):
    msg = init_msg(request)

    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])

            video = get_video_by_id(video_id)

            msg['video'] = video
            msg['play_list'] = video.files.all()
            for i in range(len(msg['play_list'])):
                msg['play_list'][i].num = i+1

            return render_to_response('upload/update_course.html', msg)
    except Exception, e:
        printError("update_course_ui: " + str(e))
   
    return render_to_response('videos/play-error.html', msg)

