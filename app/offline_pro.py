#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *

def offline(request):
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

    if checkMobile(request):
        return render_to_response('mobile/offline/offline.html', msg)
    else:
        return render_to_response('offline/offline.html', msg)


def offline_detail(request):
    msg = init_msg(request)
    try:
        course_id = int(request.GET['id'])
        offcourse = get_offcoures_by_id(course_id)

        msg['course'] = offcourse

    except Exception, e:
        print "offline_detail:", e
        return render_to_response('videos/play-error.html', msg)

    if checkMobile(request):
        return render_to_response('mobile/offline/offline_detail.html', msg)
    else:
        return render_to_response('offline/offline_detail.html', msg)


def offline_upload(request):
    msg = init_msg(request)
    return render_to_response('offline/offline_upload.html', msg)


def offline_update(request):
    msg = init_msg(request)
    try:
        course_id = int(request.GET['id'])
        offcourse = get_offcoures_by_id(course_id)

        msg['course'] = offcourse

    except Exception, e:
        print "offline_detail:", e
        return render_to_response('videos/play-error.html', msg)

    return render_to_response('offline/offline_update.html', msg)


def offline_delete(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('course_id'):
            if db_delete_course(request) == True:
                json = {'state': 'success'}

    except Exception, e:
        printError(e)
    return JsonResponse(json)

def offline_manage(request):
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

        msg['courses_len'] = getLen(subCourses)

    except Exception, e:
        print "offline:", e
    return render_to_response('offline/offline_manage.html', msg)

def offline_upload_post(request):
    msg = {'state': 'fail'}

    try:
        offline_entity = Offline()
        offline_entity = set_offline_entity(request.POST, offline_entity)
        offline_entity.save()

        msg['state'] = 'ok'

    except Exception, e:
        print "offline_upload_posti: ", str(e)

    return render_to_response('info.html', msg)

def offline_update_post(request):
    msg = {'state': 'fail'}

    try:
        course_id = int(request.POST['course_id'])
        offline_entity = get_offcoures_by_id(course_id)
        offline_entity = set_offline_entity(request.POST, offline_entity)
        offline_entity.save()

        msg['state'] = 'ok'

    except Exception, e:
        print "offline_update_post: ", str(e)

    return render_to_response('info.html', msg)

def set_offline_entity(data, _offline):
    try:
        title_       = data['title'].encode('utf-8')
        img_path_    = data['img_path'].encode('utf-8')
        short_info_  = data['short_info'].encode('utf-8')
        start_time_  = data['start_time'].encode('utf-8')
        course_time_ = data['course_time'].encode('utf-8')
        price_       = data['price'].encode('utf-8')
        status_      = data['status'].encode('utf-8')

        detail_intro_   = data['detail_intro'].encode('utf-8')
        course_intro_   = data['course_intro'].encode('utf-8')
        outlet_intro_   = data['outlet_intro'].encode('utf-8')
        prelearn_intro_ = data['prelearn_intro'].encode('utf-8')

        _offline.title = title_
        _offline.img_path = img_path_
        _offline.short_info = short_info_
        _offline.start_time  = start_time_
        _offline.course_time = course_time_
        _offline.price       = price_
        _offline.status      = status_
        _offline.detail_intro = detail_intro_
        _offline.course_intro = course_intro_
        _offline.outlet_intro = outlet_intro_
        _offline.prelearn_intro = prelearn_intro_

    except Exception, e:
        print "set_offline_entity:", e

    return _offline

def get_offcoures_by_id(course_id):
    try:
        offcourses = Offline.objects.all()
        if getLen(offcourses) > 0:
            offcourse = offcourses.filter(id=course_id).all()
            if getLen(offcourse) > 0:
                return offcourse[0]
    except Exception, e:
        print "get_offcoures_by_id:", e

    return None

def db_delete_course(request):
    try:
        course_id = int(request.GET['course_id'])
        offcourse = get_offcoures_by_id(course_id)
        offcourse.delete()
        return True
    except Exception, e:
        print "db_delete_course:", e

    return False
