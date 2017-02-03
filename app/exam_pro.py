#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
from excel_analyze import excel_analyze
from django.db.models import Q
import random
import datetime

def keep_enter(data):
    data = data.replace("\n", "<br/>")
    data = data.replace("\r", "<br/>")
    data = data.replace("\t", "!@")
    return data

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

        group_id = int(data['select_group_id'])
        if group_id == -1:
            exam.public_flag = True
        else:
            exam.public_flag = False
            with transaction.atomic():
                exam.save()
                exam.group.clear()
                exam.group.add(group_id)

    except Exception, e:
        print "set_exam_data.", e
    return exam

def set_Q(Q, pre):
    if Q != None:
        q_no = 1
        for q_i, q in enumerate(Q):
            Q[q_i]['q_no'] = q_no
            Q[q_i]['q_name'] = pre + "-" +str(q_no)
            q_no += 1
            choices = q['choices']
            answers = q['answers']
            Q[q_i]['choices'] = []
            for c_i in range(len(choices)):
                choice = {}
                choice['title'] = choices[c_i]
                choice['answer'] = answers[c_i]
                choice['q_name'] = Q[q_i]['q_name']
                choice['name'] = Q[q_i]['q_name'] + "-" + str(c_i)
                Q[q_i]['choices'].append(choice)
    return Q

@super_user
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

@super_user
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

@super_user
def createExam(request):
    msg = init_msg(request)
    return render_to_response('onlineExam/create_exam.html', msg)

@super_user
def update_exam(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        exam_id = int(request.GET['exam_id'])
        msg['exam_id'] = exam_id
        exam = Exam.objects.filter(id=exam_id)[0]

        path = exam.exam_excel_file
        single_Q, multi_Q = excel_analyze(path)

        groups = Group.objects.all()
        msg['groups'] = groups
        msg['exam'] = exam

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

@super_user
def db_delete_exam(request):
    try:
        exam_id = int(request.GET['exam_id'])
        exam = Exam.objects.filter(id=exam_id)[0]
        exam.delete()
        return True

    except Exception, e:
        printError(e)

    return False

@super_user
def delete_exam(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('exam_id'):
            if db_delete_exam(request) == True:
                json = {'state': 'success'}
    except Exception, e:
        printError(e)
    return JsonResponse(json)

@super_user
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

            groups = Group.objects.all()
            msg['groups'] = groups
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

@super_user
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

        local_time = time.time()
        for sub in subExams:
            sub.time_flag = -1
            try:
                exam_start = time.mktime(time.strptime(sub.start_time,'%Y-%m-%d,%H:%M:%S'))
                exam_end = time.mktime(time.strptime(sub.end_time,'%Y-%m-%d,%H:%M:%S'))
                if exam_start <= local_time <= exam_end:
                    sub.time_flag = 0
                elif local_time > exam_end:
                    sub.time_flag = 1
            except Exception, e:
                print "contestRoom:", str(e)

        msg['olexams'] = subExams
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
        exam_id = int(request.GET['exam_id'])
        online_exam = Exam.objects.filter(id=exam_id)[0]
        kaoshis = Kaoshi.objects.filter(account=msg['account']).all()
        if getLen(kaoshis) > 0:
            kaoshis = kaoshis.filter(exam=exam_id).all()
        msg['can_try'] = True
        msg['empty'] = True
        if kaoshis is not None:
            # check time over
            get_validate_kaoshi(kaoshis, online_exam.max_retry_num)

            if len(kaoshis) > 0:
                msg['empty'] = False
            msg['kaoshis_num'] = 0
            for i in range(len(kaoshis)):
                if kaoshis[i].submit_flag == True:
                    msg['kaoshis_num'] += 1
                kaoshis[i].no = i+1
            if msg['kaoshis_num'] >= online_exam.max_retry_num:
                msg['can_try'] = False
        msg['kaoshis'] = kaoshis
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

def get_single_multi_Q_given_exam(exam):
    try:
        path = exam.exam_excel_file
        single_Q, multi_Q = excel_analyze(path)
    except Exception, e:
        print "get_single_multi_Q_given_exam:", str(e)
        return None, None

    return single_Q, multi_Q


def get_existing_kaoshi(kaoshi):
    single_str = kaoshi.single_q
    multi_str = kaoshi.multi_q

    single_Q, multi_Q = get_single_multi_Q_given_exam(kaoshi.exam)

    shuffle_single = [int(val) for val in single_str.split(';')]
    shuffle_multi = [int(val) for val in multi_str.split(';')]

    select_single = set_Q([single_Q[i] for i in shuffle_single], 'single')
    select_multi  = set_Q([multi_Q[i] for i in shuffle_multi], 'multi')

    return select_single, select_multi, kaoshi

def get_validate_kaoshi(kaoshis, max_kaoshi_time):
    try:
        k_len = getLen(kaoshis)
        if k_len == 0:
            return 0, None

        for k in kaoshis:
            start_time = k.release_date
            end_time = datetime.datetime.now()
            spend_time = (end_time - start_time).seconds
            if spend_time > k.exam.exam_mins*60:
                # print k.id
                # print start_time, end_time, k.exam.exam_mins, spend_time
                # print "time over."
                k.submit_flag = True
                k.save()

        if k_len == max_kaoshi_time:
            if kaoshis[0].submit_flag == True:
                return -1, None
            else:
                return 1, kaoshis[0]
        elif k_len < max_kaoshi_time:
            if kaoshis[0].submit_flag == False:
                return 1, kaoshis[0]
            else:
                return 0, None
        else:
            print "else"
            return -1, None
    except Exception, e:
        print "error, get_validate_kaoshi:", str(e)

    print "get_validate_kaoshi, none."

def generate_exam(exam, account):
    try:
        if exam == None or account == None:
            return None, None, None

        kaoshis = Kaoshi.objects.filter(account=account).all()
        if getLen(kaoshis) > 0:
            kaoshis = kaoshis.filter(exam=exam).all().order_by('-release_date')
            if getLen(kaoshis) > 0:
                flag, kaoshi = get_validate_kaoshi(kaoshis, exam.max_retry_num)
                if flag == -1:
                    return None, None, None
                elif flag == 1:
                    return get_existing_kaoshi(kaoshi)
                else:
                    pass


        # create kaoshi
        single_num = exam.single_num
        multi_num  = exam.multi_num
        single_Q, multi_Q = get_single_multi_Q_given_exam(exam)

        shuffle_single = [i for i in range(len(single_Q))]
        shuffle_multi  = [i for i in range(len(multi_Q))]
        random.shuffle(shuffle_single)
        random.shuffle(shuffle_multi)
        shuffle_single = shuffle_single[:single_num]
        shuffle_multi  = shuffle_multi[:multi_num]

        select_single = set_Q([single_Q[i] for i in shuffle_single], 'single')
        select_multi  = set_Q([multi_Q[i] for i in shuffle_multi], 'multi')

        single_str = ""
        multi_str = ""
        for val in shuffle_single:
            single_str += str(val) + ";"
        single_str = single_str[:-1]

        for val in shuffle_multi:
            multi_str += str(val) + ";"
        multi_str = multi_str[:-1]

        single_answer_str = ""
        multi_answer_str = ""
        def get_answer_str(select):
            answer_str = ""
            for sm in select:
                choices = sm['choices']
                for choice in choices:
                    if choice['answer'] == True:
                        answer_str += choice['name'] + ","
                answer_str = answer_str[:-1] + ";"
            return answer_str

        single_answer_str = get_answer_str(select_single)
        multi_answer_str = get_answer_str(select_multi)
        print single_str
        print multi_str
        print single_answer_str
        print multi_answer_str


        new_kaoshi = Kaoshi()
        new_kaoshi.account = account
        new_kaoshi.exam = exam
        new_kaoshi.submit_flag = False
        new_kaoshi.single_q = single_str
        new_kaoshi.single_answer = single_answer_str
        new_kaoshi.multi_q = multi_str
        new_kaoshi.multi_answer = multi_answer_str
        new_kaoshi.score = 0
        new_kaoshi.save()

        return select_single, select_multi, new_kaoshi
    except Exception, e:
        print "generate_exam: ", str(e)

    return None, None, None

def check_kaoshi_valid(request, exam):
    msg = init_msg(request)
    try:
        # time
        now_time = str(datetime.datetime.now()).split()
        now_time_str = now_time[0] + ',' + now_time[1].split('.')[0]
        if now_time_str < exam.start_time or now_time_str > exam.end_time:
            print "time error.", now_time_str, exam.start_time, exam.end_time
            return False, render_to_response('404.html', msg)


        if exam.public_flag == False:
            if getLen(exam.group.all()) == 0:
                print "group is null."
                return False, render_to_response('404.html', msg)
            else:
                group = exam.group.all()[0]
                account = msg['account']
                if account not in group.allow_accounts.all():
                    print "not in the list."
                    return False, render_to_response('404.html', msg)


    except Exception, e:
        print "check_kaoshi_valid.", str(e)

    return True, None

def goto_exam(request):
    msg = init_msg(request)
    try:
        exam_id = int(request.GET['exam_id'])
        exam = Exam.objects.filter(id=exam_id)[0]

        valid, ret = check_kaoshi_valid(request, exam)
        if valid == False:
            return ret

        select_single, select_multi, kaoshi = generate_exam(exam, msg['account'])
        if kaoshi is None:
            return render_to_response('404.html', msg)

        start_time = kaoshi.release_date
        end_time = datetime.datetime.now()
        spend_time = (end_time - start_time).seconds
        msg['daojishi'] = max(exam.exam_mins * 60 - spend_time, 0)
        msg['single_Q'] = select_single
        msg['multi_Q'] = select_multi
        msg['exam'] = exam
        msg['kaoshi_id'] = kaoshi.id

    except Exception, e:
        print "Error, goto_exam:", str(e)
    return render_to_response('onlineExam/exam.html', msg)

def get_shijiancha(start_time, end_time):
    spend = (end_time - start_time).seconds
    hours = spend/3600
    mins = (spend-hours*3600)/60
    seconds = (spend-hours*3600-mins*60)%60

    shicha = "%02d:%02d:%02d"%(hours, mins, seconds)

    return shicha

def submit_exam_post(request):
    msg = init_msg(request)
    try:
        submit_answer = {}
        for x in request.POST:
            submit_answer[x] = request.POST[x]
        print submit_answer

        kaoshi_id = int(request.POST['kaoshi_id'])
        kaoshi = Kaoshi.objects.filter(id=kaoshi_id).all()[0]
        single_answer_str = kaoshi.single_answer
        multi_answer_str = kaoshi.multi_answer
        single_answer = single_answer_str.split(';')
        multi_answer  = multi_answer_str.split(';')

        single_correct_num = 0
        multi_correct_num  = 0
        for x in request.POST:
            x = request.POST[x]
            if x.split('-')[0] == 'single':
                if x in single_answer:
                    single_correct_num += 1

        for answers in multi_answer:
            answers = answers.split(',')
            flag = True
            pres = answers[0].split('-')[:-1]
            pre_str = ""
            for pre in pres:
                pre_str += pre + "-"
            pre_str = pre_str[:-1]

            cc = 0
            for xx in request.POST:
                if getLen(xx) < len(pre_str):
                    continue
                if xx[:len(pre_str)] == pre_str:
                    cc += 1
            if cc != getLen(answers):
                continue

            for answer in answers:
                if request.POST.has_key(answer) == False:
                    flag = False
            if flag == True:
                multi_correct_num += 1

        single_score = single_correct_num * kaoshi.exam.single_score/kaoshi.exam.single_num
        multi_score  = multi_correct_num * kaoshi.exam.multi_score/kaoshi.exam.multi_num

        total_score = single_score + multi_score
        use_time = get_shijiancha(kaoshi.release_date, datetime.datetime.now())

        msg['title'] = kaoshi.exam.title
        msg['total_num'] = kaoshi.exam.single_num + kaoshi.exam.multi_num
        msg['correct_num'] = single_correct_num + multi_correct_num
        msg['total_score'] = total_score
        msg['use_time'] = use_time
        msg['exam_id'] = kaoshi.exam.id

        kaoshi.submit_flag = True
        kaoshi.score = total_score
        kaoshi.total_q_num = max(0, msg['total_num'])
        kaoshi.correct_q_num = max(0, msg['correct_num'])
        kaoshi.use_time = use_time
        kaoshi.submit_answer = str(submit_answer)
        kaoshi.save()


    except Exception, e:
        print "submit_exam_post:", str(e)

    return render_to_response('onlineExam/result.html', msg)


def get_usernames_ids():
    accounts = Account.objects.all()
    names = []
    ids   = []
    for acc in accounts:
        names.append(acc.nickname)
        ids.append(acc.id)
    return names, ids


@super_user
def group_create(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        names, ids = get_usernames_ids()

        names_str = ""
        for i, name in enumerate(names):
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            names_str += nn + "-" + str(ids[i]) + "-=,"
        msg['usernames'] = names_str

    except Exception, e:
        print "group_create: ", str(e)

    return render_to_response('onlineExam/group_create.html', msg)

@super_user
def group_update(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        names, ids = get_usernames_ids()

        names_str = ""
        for i, name in enumerate(names):
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            names_str += nn + "-" + str(ids[i]) + "-=,"

        group_id = int(request.GET['group_id'])
        group = Group.objects.filter(id=group_id)[0]
        allow_accounts = group.allow_accounts.all()

        exist_usernames_str = ""
        for acc in allow_accounts:
            nn = acc.nickname
            nn = nn.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            exist_usernames_str += nn + "-" + str(acc.id) + "-=,"

        msg['exist_usernames'] = exist_usernames_str
        msg['group_name'] = group.group_name
        msg['group_id'] = int(group.id)
        msg['usernames'] = names_str

    except Exception, e:
        print "group update: ", str(e)

    return render_to_response('onlineExam/group_update.html', msg)

def set_group(group, group_name, ids):
    with transaction.atomic():
        group.group_name = group_name
        group.save()
        group.allow_accounts.clear()
        for id in ids:
            group.allow_accounts.add(id)
        group.save()

def group_create_post(request):
    msg = {'state': 'fail'}
    try:
        # for x in request.POST:
            # print x, request.POST[x]

        group_name = request.POST['group_name']
        if group_name.strip() == "":
            return render_to_response('info.html', msg)

        names = request.POST['names']
        names = names.split(',')
        ids = []
        for i, val in enumerate(names):
            val = val.split('-')
            # name_ = val[0]
            id_   = int(val[-1])
            ids.append(id_)

        group = Group()
        set_group(group, group_name, ids)
        msg['state'] = 'ok'


    except Exception, e:
        print "Error in group_create_post:", e

    return render_to_response('info.html', msg)

def group_update_post(request):
    msg = {'state': 'fail'}
    try:
        group_name = request.POST['group_name']
        if group_name.strip() == "":
            return render_to_response('info.html', msg)

        names = request.POST['names']
        names = names.split(',')
        ids = []
        for i, val in enumerate(names):
            val = val.split('-')
            # name_ = val[0]
            id_   = int(val[-1])
            ids.append(id_)

        group_id = int(request.POST['group_id'])
        group = Group.objects.filter(id=group_id)[0]
        set_group(group, group_name, ids)
        msg['state'] = 'ok'


    except Exception, e:
        print "Error in group_update_post:", e

    return render_to_response('info.html', msg)

@super_user
def kaoshi_groups(request):
    msg = init_msg(request)
    groups = Group.objects.all()

    if getLen(groups) > 0:
        new_groups = []
        for v in groups:
            v.release_date = str(v.release_date).split(' ')[0]
            new_groups.append(v)
        groups = new_groups

    total_page = (getLen(groups)+10-1)/10
    subGroups, cur_page = paginator_show(request, groups, 10)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['groups']     = subGroups
    msg['groups_num'] = len(groups)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1


    return render_to_response('onlineExam/kaoshi_groups.html', msg)


def db_delete_group(request):
    try:
        group_id = int(request.GET['group_id'])
        group = Group.objects.filter(id=group_id)[0]
        group.delete()
        return True

    except Exception, e:
        printError(e)

    return False

def group_delete(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('group_id'):
            if db_delete_group(request) == True:
                json = {'state': 'success'}
    except Exception, e:
        printError(e)
    return JsonResponse(json)

@super_user
def kaoshi_exams(request):
    msg = init_msg(request)
    exams = Exam.objects.all()

    if getLen(exams) > 0:
        new_exams = []
        for v in exams:
            v.release_date = str(v.release_date).split(' ')[0]
            new_exams.append(v)
        exams = new_exams

    total_page = (getLen(exams)+10-1)/10
    subExams, cur_page = paginator_show(request, exams, 10)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['exams']     = subExams
    msg['exams_num'] = getLen(exams)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1


    return render_to_response('onlineExam/kaoshi_exams.html', msg)
