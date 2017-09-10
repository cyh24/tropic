#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
import random
import datetime
from save_excel import write_csv
from django.http import StreamingHttpResponse

def banji_course(request):
    msg = init_msg(request)
    if request.GET.has_key('video-id'):
        try:
            video_id = int(request.GET['video-id'])
            msg['video_id'] = video_id
            video = Video.objects.get(id=video_id)
            if not video and not video.is_customize:
                 return render_to_response('videos/play-error.html', msg)

            current_num = 0
            if request.GET.has_key('current'):
                current_num = int(request.GET['current'])

            if video.is_reverse == 1:
                files = video.files.all()[::-1]
            else:
                files = video.files.all()
            if getLen(files) <= current_num:
                current_num = 0

            key = files[current_num].key
            video_url = Qiniu.download_private_url(key.encode('utf-8'))
            msg['video_url'] = video_url
            play_list = [val for val in files]

            # try:
                # # course progress
                # course_progress = get_course_progress(request.user, video)
                # status_list = course_progress.get_status()

                # finished_num = 0
                # next_id = 0
                # for i in range(getLen(play_list)):
                    # if status_list[i] == 0:
                        # next_id = i
                        # break
                # for i in range(getLen(play_list)):
                    # if status_list[i] == 1:
                        # finished_num += 1
                    # play_list[i].watched = status_list[i]
                # msg['finished_num'] = finished_num
                # msg['total_num'] = getLen(play_list)
                # msg['percent'] = finished_num*100.0/getLen(play_list)
                # msg['next_id'] = next_id
                # msg['next_title'] = play_list[next_id].title
            # except Exception as e:
                # print str(e)
            FILE_STATUS = {}
            try:
                next_id = 0
                video_status = get_watch_video_status(request.user, video)
                files_status = video_status.q_files_status.all()
                for i in range(files_status.count()):
                    if not files_status[i].is_finished:
                        next_id = i
                        break
                FILE_STATUS = {}
                for fs in files_status:
                    if fs.is_finished:
                        step = 2
                    else:
                        if fs.current_time == 0:
                            step = 0
                        else:
                            step = 1
                    FILE_STATUS[int(fs.q_file.id)] = {"duration": "%02d:%02d"%(int(fs.duration/60), int(fs.duration%60)),
                            "current_time": "%02d:%02d"%(int(fs.current_time/60), int(fs.current_time%60)),
                            "step": step}
                msg['finished_num'] = video_status.finished_num
                msg['total_watched_time'] = int(video_status.total_watched_time / 60 )
                msg['total_time'] = int(video_status.total_time / 60)
                msg['total_num'] = getLen(play_list)
                msg['percent'] = video_status.finished_percent * 100
                msg['next_id'] = next_id
                msg['next_title'] = play_list[next_id].title
            except Exception as e:
                print("banji_course: ", str(e))

            if getLen(play_list) == 0 or play_list[0].chapter_num == -1:
                chapter_idx = []
            else:
                chapter_idx = [[0, play_list[0].chapter_name, play_list[0].chapter_num]]

            for i in range(1, getLen(play_list)):
                if play_list[i].chapter_num != -1 and play_list[i].chapter_num != play_list[i-1].chapter_num:
                    chapter_idx.append([i, play_list[i].chapter_name, play_list[i].chapter_num])

            chapter_idx.reverse()

            v_num = 0
            for i in range(getLen(play_list)):
                play_list[i].num = i
                play_list[i].cur_flag = 0
                if i not in chapter_idx:
                    v_num += 1
                    play_list[i].v_num = v_num
                    if int(play_list[i].id) in FILE_STATUS:
                        play_list[i].duration = FILE_STATUS[int(play_list[i].id)]['duration']
                        play_list[i].current_time = FILE_STATUS[int(play_list[i].id)]['current_time']
                        play_list[i].step = FILE_STATUS[int(play_list[i].id)]['step']

            play_list[current_num].cur_flag = 1

            for idx in chapter_idx:
                chapter = {}
                chapter['is_chapter'] = True
                chapter['chapter_num'] = idx[2]
                chapter['chapter_name'] = idx[1]
                play_list.insert(idx[0], chapter)

            msg['course'] = video
            msg['play_list'] = play_list

            if checkMobile(request):
                return render_to_response('mobile/banji/banji_course.html', msg)
            else:
                return render_to_response('banji/banji_course.html', msg)
        except Exception, e:
            print "banji_course:", str(e)

    return render_to_response('videos/play-error.html', msg)

def courses(request):
    msg = init_msg(request)
    try:
        msg['cur_page'] = 0
        courses = Video.objects.filter(is_customize=True).all()

        total_page = (getLen(courses)+10-1)/10
        subCourses, cur_page = paginator_show(request, courses, 10)

        pages_before, pages_after = paginator_bar(cur_page, total_page)

        msg['courses']     = subCourses
        msg['courses_num'] = getLen(courses)
        msg['cur_page']   = cur_page
        msg['pages_before'] = pages_before
        msg['pages_after']  = pages_after
        msg['pre_page']   = cur_page - 1
        msg['after_page'] = cur_page + 1
    except Exception, e:
        print "banji_courses:", str(e)

    return render_to_response('banji/courses.html', msg)

@super_user
def upload_banji_course_ui(request):
    msg = init_msg(request)

    return render_to_response('banji/upload_banji_course.html', msg)

def upload_banji_course_post(request):
    pass

@super_user
def application(request):
    msg = init_msg(request)
    applications  = ApplyGroup.objects.filter().all()
    for i, app in enumerate(applications):
        applications[i].account_name = app.account.nickname
        applications[i].group_name = app.group.group_name

    msg['applications'] = applications

    return render_to_response('banji/application.html', msg)

def banji_list(request):
    msg = init_msg(request)
    try:
        group_id = int(request.GET['group_id'])
        group = Group.objects.get(id=group_id)
        groups, l = get_groups(request.user)
        for g in groups:
            if g.id == group.id:
                group = g
                break
        videos = group.video_set.all()
        files_num = 0
        for i, v in enumerate(videos):
            videos[i].tags = (v.tags_str).split()
            files_num += videos[i].files_num
        msg['group'] = group
        msg['videos_num'] = getLen(videos)
        msg['files_num'] = files_num
        msg['videos'] = videos
    except Exception as e:
        printError(e)
    return render_to_response('banji/banji_list.html', msg)

def file_iterator(file_name, chunk_size=1024):
    with open(file_name) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
def user_progress(request):
    video_id = request.GET['video_id']
    video = get_video_by_id(video_id)
    groups = video.group.all()
    msg = {}
    data = []
    for group in groups:
        for acc in group.allow_accounts.all():
            try:
                video_status = WatchVideoStatus.objects.get(account=acc, video=video)
                data.append([acc.id, acc.nickname, video.title, video_status.total_time,
                    video_status.total_watched_time, video.files.all().count(),
                    video_status.finished_num, video_status.finished_percent])
            except Exception as e:
                print(e)
    try:
        row_title  = ['用户ID', '昵称','视频名称', '视频时长(s)', '观看时间(s)', '总课时数', '已经完成的课时数', '完成比例']
        data.insert(0, row_title)
        filename = "user_progress/" + get_uuid()+".csv"
        filepath = write_csv(filename, data)
        response = StreamingHttpResponse(file_iterator(filepath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
        return response

    except Exception as e:
        print(e)

    msg['data'] = data
    return JsonResponse(msg)
