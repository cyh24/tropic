#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
from excel_analyze import excel_analyze

def set_exam_data(exam, data):
    try:
        exam.title = data['exam_title']
        exam.img_path = data['img_path']
        exam.detail_intro = data['exam_intro']
        exam.start_time = data['exam_start_time']
        exam.end_time = data['exam_end_time']
        exam.exam_mins = int(data['exam_time'])

        exam.single_score = float(data['single_score'])
        exam.single_num = int(data['single_num'])
        exam.multi_score  = float(data['multi_score'])
        exam.multi_num  = int(data['multi_num'])
        exam.max_retry_num = int(data['max_retry_num'])

        exam.total_score = exam.single_score + exam.multi_score
        exam.public_flag = True

    except Exception, e:
        print "set_exam_data.", e
    return exam

def set_Q(Q, pre):
    if Q != None:
        q_no = 1
        for q_i, q in enumerate(Q):
            Q[q_i]['q_no'] = q_no
            Q[q_i]['q_name'] = pre + str(q_no)
            q_no += 1
            choices = q['choices']
            answers = q['answers']
            Q[q_i]['choices'] = []
            for c_i in range(len(choices)):
                choice = {}
                choice['title'] = choices[c_i]
                choice['answer'] = answers[c_i]
                choice['name'] = pre + str(c_i)
                Q[q_i]['choices'].append(choice)
    return Q

def exam_upload_post(request):
    msg = {'state': 'fail'}
    try:
        for x in request.POST:
            print x, request.POST[x]

        exam_excel_file = request.POST['exam_excel_file']
        # exam_excel_content = open(exam_excel_file).readlines()

        exam = Exam()
        exam = set_exam_data(exam, request.POST)
        # exam.exam_excel_content = exam_excel_content
        exam.exam_excel_file = exam_excel_file
        exam.save()

        msg['state'] = 'ok'
    except Exception, e:
        print "Error in exam_update_post:", e

    return render_to_response('info.html', msg)

def exam_update_post(request):
    msg = {'state': 'fail'}
    try:
        for x in request.POST:
            print x, request.POST[x]

        # exam_excel_file = request.POST['exam_excel_file']
        # exam_excel_content = open(exam_excel_file).readlines()
        exam_id = int(request.POST['exam_id'])

        exam = Exam.objects.filter(id=exam_id)[0]
        exam = set_exam_data(exam, request.POST)
        # exam.exam_excel_content = exam_excel_content
        # exam.exam_excel_file = exam_excel_file
        exam.save()

        msg['state'] = 'ok'
    except Exception, e:
        print "Error in exam_update_post:", e

    return render_to_response('info.html', msg)

def createExam(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/create_exam.html', msg)

def update_exam(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        exam_id = int(request.GET['id'])
        msg['exam_id'] = exam_id
        exam = Exam.objects.filter(id=exam_id)[0]

        path = exam.exam_excel_file
        single_Q, multi_Q = excel_analyze(path)

        msg['single_Q'] = set_Q(single_Q, "single")
        msg['single_num'] = getLen(single_Q)
        msg['single_score'] = int(exam.single_score)
        msg['multi_Q'] = set_Q(multi_Q, "multi")
        msg['multi_num'] = getLen(multi_Q)
        msg['multi_score'] = int(exam.multi_score)
        msg['max_retry_num'] = int(exam.max_retry_num)
        msg['detail_intro'] = exam.detail_intro

        msg['exam_excel_file'] = path

    except Exception, e:
        print "create_exam_update_excel: ", str(e)

    return render_to_response('onlineExam/update_exam.html', msg)

def delete_exam(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        exam_id = int(request.GET['id'])
        exam = Exam.objects.filter(id=exam_id)[0]
        exam.delete()

    except Exception, e:
        print "create_exam_update_excel: ", str(e)

    return HttpResponseRedirect('/contestRoom/')

def upload_exam(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        file_key = 'exam_excel'
        if request.method == "POST":
            for x in request.POST:
                print x, request.POST[x]

        if request.FILES.has_key(file_key):
            postfix = (request.FILES[file_key].name).split('.')[-1]
            path = EXAM_EXCEL_FOLD + getRandomStr() + "." + postfix
            print path
            handle_uploaded_photo(path, request.FILES[file_key])

            single_Q, multi_Q = excel_analyze(path)

            msg['single_Q'] = set_Q(single_Q, "single")
            msg['single_num'] = getLen(single_Q)
            msg['single_score'] = 50
            msg['multi_Q'] = set_Q(multi_Q, "multi")
            msg['multi_num'] = getLen(multi_Q)
            msg['multi_score'] = 50

            msg['max_retry_num'] = 2

            msg['exam_excel_file'] = path

    except Exception, e:
        print "create_exam_upload_excel: ", str(e)

    return render_to_response('onlineExam/show_exam.html', msg)

def showExam(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/show_exam.html', msg)

def contestRoom(request):
    msg = init_msg(request)

    try:
        online_exams = Exam.objects.all().order_by('-release_date')

        total_page = (getLen(online_exams)+PAGE_SIZE-1)/PAGE_SIZE
        subExams, cur_page = paginator_show(request, online_exams, PAGE_SIZE)

        pages_before, pages_after = paginator_bar(cur_page, total_page)

        msg['offexams'] = subExams
        msg['cur_page']   = cur_page
        msg['pages_before'] = pages_before
        msg['pages_after']  = pages_after
        msg['pre_page']   = cur_page - 1
        msg['after_page'] = cur_page + 1
        msg['total_page'] = total_page

    except Exception, e:
        print "contestRoom:", e

    return render_to_response('onlineExam/contestRoom.html', msg)

def exam_summary(request):
    msg = init_msg(request)
    try:
        exam_id = int(request.GET['id'])
        online_exam = Exam.objects.filter(id=exam_id)[0]
        msg['exam'] = online_exam
    except Exception, e:
        print "exam_summary: ", e
    return render_to_response('onlineExam/examSummary.html', msg)

def single_select(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/single_select.html', msg)

def multi_select(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/multi_select.html', msg)
