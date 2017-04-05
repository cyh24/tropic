#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
import random
import datetime

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

            try:
                # course progress
                course_progress = get_course_progress(request.user, video)
                status_list = course_progress.get_status()

                finished_num = 0
                next_id = 0
                for i in range(getLen(play_list)):
                    if status_list[i] == 0:
                        next_id = i
                        break
                for i in range(getLen(play_list)):
                    if status_list[i] == 1:
                        finished_num += 1
                    play_list[i].watched = status_list[i]
                msg['finished_num'] = finished_num
                msg['total_num'] = getLen(play_list)
                msg['percent'] = finished_num*100.0/getLen(play_list)
                msg['next_id'] = next_id
                msg['next_title'] = play_list[next_id].title
            except Exception as e:
                print str(e)

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
