#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *

##@login_required(login_url='/login/')
@super_user
def videos_data(request):
    msg = init_msg(request)
    data_info = DataInfo.objects.all()
    msg['data_info'] = data_info
    return render_to_response('videos/videos-data.html', msg)

@super_user
def index_info(request):
    msg = init_msg(request)
    index_info = IndexInfo.objects.all()
    msg['index_info'] = index_info
    return render_to_response('videos/index-info.html', msg)

#@login_required(login_url='/login/')
@super_user
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

    total_page = (getLen(videos)+10-1)/10
    subVideos, cur_page = paginator_show(request, videos, 10)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    intrest_videos = []
    for iv in IntrestVideos.objects.all():
        intrest_videos.append(iv.video)

    for i in range(getLen(subVideos)):
        if subVideos[i] in intrest_videos:
            subVideos[i].intrest_flag = 1
        else:
            subVideos[i].intrest_flag = 0
        try:
            subVideos[i].first_catalog = subVideos[i].first_catalogs.all()[0]
            subVideos[i].second_catalog = subVideos[i].second_catalogs.all()[0]
        except:
            pass

    msg['videos']     = subVideos
    msg['videos_len'] = len(videos)
    msg['cur_page']   = cur_page
    msg['first_page'] = 1
    msg['last_page'] = total_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    msg['intrest_videos'] = get_intrest_videos()

    return render_to_response('videos/videos-manage.html', msg)


#@login_required(login_url='/login/')
@super_user
def delete_video(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            if db_delete_video(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)


#@login_required(login_url='/login/')
@super_user
def delete_intrestvideo(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            if db_delete_intrestvideo(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)

#@login_required(login_url='/login/')
@super_user
def add_intrestvideo(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            if db_add_intrestvideo(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)

#@login_required(login_url='/login/')
@super_user
def upload_course_ui(request):
    msg = init_msg(request)
    groups = Group.objects.all()
    msg['groups'] = groups

    try:
        firsts = {}
        first_catalogs = get_all_first_catalogs()
        for first_cata in first_catalogs:
            second_catas = []
            for second_cata in first_cata.second_catalogs.all():
                second_catas.append({"txt": second_cata.name, "val": second_cata.id})
            firsts[first_cata.id] = second_catas
        msg['first_catalogs'] = first_catalogs
        msg['firsts'] = json.dumps(firsts)
    except Exception as e:
        print("upload_course_ui:", str(e))

    return render_to_response('upload/upload_course.html', msg)


#@login_required(login_url='/login/')
@super_user
@csrf_protect
def update_course_ui(request):
    msg = init_msg(request)

    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])

            video = get_video_by_id(video_id)

            groups = Group.objects.filter(is_valid=True).all()
            selected_group = video.group.all()
            if selected_group and groups:
                for i, group in enumerate(groups):
                    if group in selected_group:
                        groups[i].is_selected = True

            msg['groups'] = groups
            msg['public_flag'] = video.public_flag
            msg['video'] = video
            msg['play_list'] = video.files.all()
            for i in range(len(msg['play_list'])):
                msg['play_list'][i].num = i+1

            firsts = {}
            first_catalogs = get_all_first_catalogs()
            for first_cata in first_catalogs:
                second_catas = []
                for second_cata in first_cata.second_catalogs.all():
                    second_catas.append({"txt": second_cata.name, "val": second_cata.id})
                firsts[first_cata.id] = second_catas
            try:
                msg['cur_first_cata'] = video.first_catalogs.all()[0]
                msg['cur_second_cata'] = video.second_catalogs.all()[0]
                print(msg['cur_first_cata'], msg['cur_second_cata'])
            except Exception as e:
                print("cur_cata:", str(e))
            msg['first_catalogs'] = first_catalogs
            msg['firsts'] = json.dumps(firsts)

            return render_to_response('upload/update_course.html', msg)
    except Exception, e:
        printError("update_course_ui: " + str(e))
    return render_to_response('videos/play-error.html', msg)

@super_user
def order_manage(request):
    each_page_num = 20
    msg = init_msg(request)

    try:
        if request.GET.has_key("order_id"):
            order_id = int(request.GET['order_id'])
            orders = Order.objects.filter(id=order_id).all()
        else:
            orders = Order.objects.all()
    except Exception, e:
        orders = Order.objects.all()

    if getLen(orders) >= 1:
        orders = orders.order_by('-release_date')

    total_page = (getLen(orders)+each_page_num-1)/each_page_num
    subOrders, cur_page = paginator_show(request, orders, each_page_num)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    for i in range(getLen(subOrders)):
        subOrders[i].user_nickname = subOrders[i].account.nickname
        subOrders[i].release_date = str(subOrders[i].release_date).split(' ')[0]

    msg['orders']     = subOrders
    msg['orders_len'] = len(orders)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1
    return render_to_response('videos/order-manage.html', msg)

