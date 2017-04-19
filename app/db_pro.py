#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from qiniu_pro import *

from models import *
from config import *

from django.db import transaction
from wxpay import get_wxpay_qrcode, check_pay_by_order_num
from wxknife import JsApi_pub, UnifiedOrder_pub, WxPayConf_pub
import datetime
from django.db.models import *
from qiniu_pro import upload_free_file
import jieba

import time
def info_wait(request):
    msg = {'state': 'wait'}
    return render_to_response('info.html', msg)

def upload_course_post(request):
    msg = {'state': 'fail'}
    try:
        # if request.method == "POST":
            # for x in request.POST:
                # print x, request.POST[x]

        if request.FILES.has_key('logo'):
            postfix = (request.FILES['logo'].name).split('.')[-1]
            path = LOGO_FOLD + getRandomStr() + "." + postfix
            handle_uploaded_photo(path, request.FILES['logo'])
            # print "logo: ", path

            #path_logo = path[3:]
            new_path = upload_free_file(path)

            if save_video(request, new_path) == True:
                msg['state'] = 'ok'

    except Exception, e:
        print "upload_course_post: ", str(e)

    return render_to_response('info.html', msg)

def modify_order_post(request):
    json = {'state': 'fail'}
    try:
        order_id, name, value = None, None, None
        if request.GET.has_key("order_id"):
            order_id = int(request.GET['order_id'])

        if request.GET.has_key("name"):
            name = request.GET['name']

        if request.GET.has_key("value"):
            value = request.GET['value']

        order = get_order_given_orderid(order_id)
        if name == "price":
            order.price = float(value)
        elif name == "order_valid_day":
            order.order_valid_day = int(value)
        order.save()

        json['state'] = 'ok';

    except Exception, e:
        print "modify_order_post: ", str(e)

    return JsonResponse(json)

def modify_application_post(request):
    json = {'state': 'fail'}
    try:
        application_id, name, value = None, None, None
        if request.GET.has_key("application_id"):
            application_id = int(request.GET['application_id'])

        if request.GET.has_key("value"):
            status = request.GET['value']

        application = ApplyGroup.objects.get(id=application_id)

        if int(status) == 1:
            application.status = 1
            application.group.allow_accounts.add(application.account)
            application.delete()
        elif int(status) == -1:
            application.status = -1
            application.delete()

        json['state'] = 'ok';

    except Exception, e:
        print "modify_order_post: ", str(e)

    return JsonResponse(json)

def update_course_post(request):
    msg = {'state': 'fail'}
    try:
        # if request.method == "POST":
            # for x in request.POST:
                # print x, request.POST[x]

        if request.FILES.has_key('logo'):
            if request.FILES['logo'] != None:
                postfix = (request.FILES['logo'].name).split('.')[-1]
                path = LOGO_FOLD + getRandomStr() + "." + postfix
                print path
                handle_uploaded_photo(path, request.FILES['logo'])

                #path_logo = path[3:]
                new_path = upload_free_file(path)

                if update_video(request, new_path) == True:
                    msg['state'] = 'ok'
        else:
            if update_video(request) == True:
                msg['state'] = 'ok'

    except Exception, e:
        print "upload_course_post: ", str(e)

    return render_to_response('info.html', msg)

def index_info_post(request):
    msg = {'state': 'fail'}
    try:
        # if request.method == "POST":
            # for x in request.POST:
                # print x, request.POST[x]

            save_index_info(request.POST)
            msg ={'state': 'ok'}
            try:
                if request.POST.has_key("poster_img"):
                    poster_img = request.POST['poster_img'].strip()
                    if poster_img != "":
                        sys_cmd = "wget %s -O /home/www/tropic/app/static/images/poster.jpg"%(poster_img.encode("utf-8"))
                        os.system(sys_cmd)
                if request.POST.has_key("background_img"):
                    background_img = request.POST['background_img'].strip()
                    if background_img != "":
                        sys_cmd = "wget %s -O /home/www/tropic/app/static/images/backgound.jpg "%(background_img.encode("utf-8"))
                        os.system(sys_cmd)
            except Exception, e:
                print "poster_background", str(e)

    except Exception, e:
        print "index_info_post: ", str(e)

    return render_to_response('info.html', msg)

def save_index_info(data):
    table = json.loads(data['table_json'].encode('utf-8'))

    table_data = []
    for row in table:
        try:
            new_row = []
            img_num  = int(row['img_num'].encode('utf-8').strip())
            img_path = row['img_path'].encode('utf-8').strip()
            jump_url = row['jump_url'].encode('utf-8').strip()

            if img_path == "" or jump_url == "":
                break
            new_row.append(img_num)
            new_row.append(img_path)
            new_row.append(jump_url)
            table_data.append(new_row)
        except Exception, e:
            print "save_index_info", str(e)
            break

    if getLen(table_data) <= 0:
        print "index_info: none data"
        return -1
    #else

    with transaction.atomic():
        # first delete the old data
        old_data = IndexInfo.objects.all()
        if getLen(old_data) > 0:
            for od in old_data:
                od.delete()

        # add new data
        for row in table_data:
            index_info = IndexInfo()
            index_info.img_num  = row[0]
            index_info.img_path = row[1]
            index_info.jump_url = row[2]
            index_info.save()

def save_tag(tag_name):
    # print "save tag: ", tag_name
    db_tags = Tag.objects.all()
    db_tlist = []
    if db_tags != None:
        for db_tag in db_tags:
            db_tlist.append(db_tag.name)

    if db_tlist == None:
        pass
    elif tag_name in db_tlist:
        return None

    tag = Tag()
    tag.name = tag_name.encode('utf-8')
    tag.save()

    return True

def save_kind(kind_name):
    db_kinds = Tag.objects.all()
    db_klist = []
    if db_kinds != None:
        for db_kind in db_kinds:
            db_klist.append(db_kind.name)

    if db_klist == None:
        pass
    elif kind_name in db_klist:
        return False

    kind = Kind()
    kind.name = kind_name.encode('utf-8')
    kind.save()

    return True

def tag_deal(tag_list):
    db_tags = Tag.objects.all()
    db_tlist = []
    if db_tags != None:
        for db_tag in db_tags:
            db_tlist.append(db_tag.name)

    if tag_list == None:
        return True

    for tag in tag_list:
        if tag not in db_tlist:
            save_tag(tag)

def kind_deal(kind):
    db_kinds = Kind.objects.all()
    db_klist = []
    if db_kinds != None:
        for db_kind in db_kinds:
            db_klist.append(db_kind.name)
    if kind not in db_klist:
        save_kind(kind)

def get_video_by_id(video_id):
    try:
        video_id = int(video_id)
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            return video
    except Exception, e:
        printError(e)

    return None

def get_video_by_ordernum(order_num):
    try:
        order = get_order_given_ordernum(order_num)
        video = order.video
        return video
    except Exception, e:
        printError("get_video_by_ordernum: "+str(e))

    return None

def get_intrestvideo_by_id(video_id):
    try:
        video_id = int(video_id)
        video = IntrestVideos.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            return video
    except Exception, e:
        printError(e)

    return None

def save_video(request, logo_path, need_authority=True):

    try:
        video = Video()

        video.logo_img = logo_path

        video.teacher = Account.objects.filter(user=request.user).all()[0]

        data = request.POST
        if data.has_key('title'):
            video.title = data['title'].encode('utf-8')
            if video.title.strip() == "":
                return False
        if data.has_key('tag'):
            data_tag = data['tag']
            tagStr = ""
            tag_list = data_tag.split()
            tag_len = getLen(tag_list)
            for i in range(tag_len):
                if i != 0:
                    tagStr += " " + tag_list[i]
                else:
                    tagStr += tag_list[i]
            video.tags_str = tagStr.encode('utf-8')
            tag_deal(tag_list)

        if data.has_key('kind'):
            kind = data['kind']
            video.kind_str = kind.encode('utf-8')
            kind_deal(kind)

        if data.has_key('valid_day'):
            video.valid_day = int(data['valid_day'].strip())

        if data.has_key('desc'):
            video.info = data['desc'].encode('utf-8')
        if data.has_key('money'):
            video.money = float(data['money'].encode('utf-8'))

        if data.has_key('is_reverse'):
            is_reverse = 0
            try:
                is_reverse = int(float(data['is_reverse']))
            except Exception, e:
                is_reverse = 0
            video.is_reverse = is_reverse

        if data.has_key('is_customize'):
            is_customize = 0
            try:
                is_customize = int(float(data['is_customize']))
            except Exception, e:
                is_customize = 0
            video.is_customize = is_customize

        with transaction.atomic():
            qfiles = []
            if data.has_key('table_json'):
                qfiles = get_qiniu_files(data)

                if len(qfiles) == 0:
                    print "qiniu file: none."
                    return False

                video.release_date = datetime.datetime.now()
                video.save()
                for i in range(len(qfiles)):
                    qfiles[i].save()

                    video.files.add(qfiles[i])

            video.save()
            if data.has_key('select_group_id'):
                group_ids =  data.getlist('select_group_id')
                video.group.clear()
                for group_id in group_ids:
                    group_id = int(str(group_id))
                    if group_id == -1:
                        video.public_flag = True
                        video.group.clear()
                        break
                    else:
                        video.public_flag = False
                        video.group.add(group_id)
            # if data.has_key('select_group_id'):
                # group_ids =  data.getlist('select_group_id')
                # if group_id == -1:
                    # video.public_flag = True
                    # video.group.clear()
                # else:
                    # video.public_flag = False
                    # with transaction.atomic():
                        # video.group.clear()
                        # video.group.add(group_id)
            return True
    except Exception, e:
        print str(e)
        return False


def get_qiniu_files(data):
    qfiles = []
    count = 0
    table = json.loads(data['table_json'].encode('utf-8'))

    for row in table:
        qiniu_file = QiniuFile()
        video_key  = row['video_key'].encode('utf-8').strip()
        video_time = int(row['video_time'].encode('utf-8').strip())
        title      = row['video_name'].encode('utf-8').strip()
        chapter_num = int(row['chapter_num'].encode('utf-8').strip())
        chapter_name = row['chapter_name'].encode('utf-8').strip()

        if video_key == "" or title == "":
            break

        qiniu_file.chapter_num = chapter_num
        qiniu_file.chapter_name = chapter_name
        qiniu_file.key        = video_key
        qiniu_file.video_time = video_time
        qiniu_file.title      = title

        qiniu_file.bucket = BUCKET_NAME
        qiniu_file.domain = DOMAIN
        qiniu_file.need_authority = True

        qfiles.append(qiniu_file)

    return qfiles


def update_video(request, logo_path="", need_authority=True):
    print "update_video"
    try:
        data = request.POST

        video_id = int(data['video_id'])
        video = Video.objects.filter(id=video_id).all()[0]

        if logo_path != "":
            video.logo_img = logo_path

        data = request.POST
        if data.has_key('title'):
            video.title = data['title'].encode('utf-8')
            if video.title.strip() == "":
                print "Error: title none."
                return False
        if data.has_key('tag'):
            data_tag = data['tag']
            tagStr = ""
            tag_list = data_tag.split()
            tag_len = getLen(tag_list)
            for i in range(tag_len):
                if i != 0:
                    tagStr += " " + tag_list[i]
                else:
                    tagStr += tag_list[i]
            video.tags_str = tagStr.encode('utf-8')
            tag_deal(tag_list)

        if data.has_key('kind'):
            kind = data['kind']
            video.kind_str = kind.encode('utf-8')
            kind_deal(kind)

        if data.has_key('valid_day'):
            video.valid_day = int(data['valid_day'].strip())

        if data.has_key('desc'):
            video.info = data['desc'].encode('utf-8')
        if data.has_key('money'):
            video.money = float(data['money'].encode('utf-8'))

        if data.has_key('is_reverse'):
            is_reverse = 0
            try:
                is_reverse = int(float(data['is_reverse']))
            except Exception, e:
                is_reverse = 0
            video.is_reverse = is_reverse

        if data.has_key('is_customize'):
            is_customize = 0
            try:
                is_customize = int(float(data['is_customize']))
            except Exception, e:
                is_customize = 0
            video.is_customize = is_customize

        if data.has_key('select_group_id'):
            group_ids =  data.getlist('select_group_id')
            with transaction.atomic():
                video.group.clear()
                for group_id in group_ids:
                    group_id = int(str(group_id))
                    if group_id == -1:
                        video.public_flag = True
                        video.group.clear()
                        break
                    else:
                        video.public_flag = False
                        video.group.add(group_id)

        with transaction.atomic():
            qfiles = []
            if data.has_key('table_json'):
                qfiles = get_qiniu_files(data)

                if getLen(qfiles) == 0:
                    print "qiniu file: none."
                    return False

                video.files.clear()
                video.release_date = datetime.datetime.now()
                video.save()
                for i in range(getLen(qfiles)):
                    qfiles[i].save()

                    video.files.add(qfiles[i])
                    pass

            video.save()
            return True
    except Exception, e:
        print str(e)

    return False



def add_watch_num(video_id):
    try:
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            video.watch_num += 1
            video.save()
    except Exception, e:
        print "Error: add_watch_num.\nError: " + str(e)


def get_intrest_videos():
    try:
        intrest_videos = IntrestVideos.objects.all()
        videos = []
        for iv in intrest_videos:
            videos.append(iv.video)

        v_num = getLen(videos)
        if v_num > 4:
            return videos

        vs = Video.objects.order_by('watch_num')
        if getLen(vs) >= 5:
            vs = vs[:5]

        count = 0
        for v in vs:
            if v not in videos:
                videos.append(v)
                count += 1
            if count > 4:
                break

        return videos

    except Exception, e:
        print "get_intrest_videos: ", str(e)

    return None


stop_list = []
# with open("/home/www/tropic/app/stopword.txt", "r") as f:
    # stop_list = f.readlines()
    # stop_list = [line[:-1] for line in stop_list]
stop_list = {}.fromkeys([ line.rstrip() for line in open('/home/www/tropic/app/stopword.txt') ])

# video_list = []
# with open("/home/www/tropic/app/video.txt", "r") as f:
    # video_list = f.readlines()
    # video_list = [line[:-2] for line in video_list]

# keyword_list = []
# with open("/home/www/tropic/app/keyword.txt", "r") as f:
    # keyword_list = f.readlines()
    # keyword_list = [line[:-1] for line in keyword_list]


# with open("/home/www/tropic/app/key_videoID.txt", "w") as f:
    # m = {}
    # all_v = Video.objects.all()
    # # print all_v[0].files.all()[0].key.encode("utf8")
    # # print len(all_v[0].files.all()[0].key.encode("utf8"))
    # # print video_list[0]
    # # print len(video_list[0])
    # # print len("通过身份证号计算出生日期.mp4")
    # # print len("1招聘数据问题及正确思路.mp4")
    # for i in range(len(keyword_list)):
        # for key in keyword_list[i].split():
            # video_path = video_list[i]
            # for v in all_v:
                # for file in v.files.all():
                    # if file.key.encode("utf8") == str(video_path):
                        # if m.has_key(key) == False:
                            # m[key] = []
                        # m[key].append(v.id)
                        # break

    # for k in m:
        # f.write(str(k) + ":" + str(m[k])+"\n")

key_video = []
key_ = []
video_ = []
with open("/home/www/tropic/app/key_videoID.txt", "r") as f:
    key_video = f.readlines()
    key_ = [line[:-1].split(':')[0] for line in key_video]
    video_ = [line[:-1].split(':')[1] for line in key_video]


def get_search_videos(request):
    try:
        if request.GET.has_key('title'):
            q_titles = request.GET['title'].encode('utf8')
            seg_list = jieba.cut_for_search(q_titles)
            seg_list = list(seg_list)
            if "" in seg_list:
                seg_list.remove("")
            if " " in seg_list:
                seg_list.remove(" ")

            if getLen(seg_list) == 0:
                return None
                # return Video.objects.all()

            temp = []
            for i in range(getLen(seg_list)):
                if str(seg_list[i].encode("utf8")) not in stop_list:
                    temp.append(seg_list[i])
                    # seg_list.remove(seg_list[i])
                    # continue
                # elif seg_list[i].encode("utf8") not in key_:
                    # seg_list.remove(seg_list[i])
            seg_list = temp
            if getLen(seg_list) == 0:
                return None

            q_title = seg_list[0]
            videos = Video.objects.filter(is_customize=False).filter(Q(title__icontains=q_title)|Q(kind_str__icontains=q_title)|Q(tags_str__icontains=q_title)).all()
            for i in range(1, getLen(seg_list)):
                q_title = seg_list[i]
                videos = videos | Video.objects.filter(Q(title__icontains=q_title)|Q(kind_str__icontains=q_title)|Q(tags_str__icontains=q_title)).all()

            # ids = []
            # for seg in seg_list:
                # if seg.encode("utf8") in key_:
                    # v_ids = video_[key_.index(seg.encode("utf8"))]
                    # # print v_ids
                    # for v in v_ids.split(','):
                        # ids.append(v)

            # ids =  list(set(ids))
            # videos = None
            # if getLen(ids) >= 1:
                # q_id = ids[0]
                # videos = Video.objects.filter(id=q_id).all()
                # for i in range(1, len(ids)):
                    # q_id = ids[i]
                    # videos = videos | Video.objects.filter(id=q_id).all()

            # if getLen(videos) == 0:
                # return Video.objects.all()
            return videos

        else:
            return Video.objects.all()

    except Exception, e:
        printError("search:"+str(e))

    return None


def get_order_videos(request, videos, msg):
    m_videos = None
    try:
        if request.GET.has_key('order_by'):
            order_by = request.GET['order_by']
            msg['cur'] = order_by
            if order_by == "new":
                order_key = '-release_date'
            elif order_by == "like":
                order_key = '-like_num'
            elif order_by == "popular":
                order_key = '-watch_num'
            elif order_by == "price":
                flag = request.GET['flag']
                if flag == "up":
                    msg['up_down'] = "down"
                    order_key = '-money'
                else:
                    msg['up_down'] = "up"
                    order_key = 'money'
            else:
                order_key = '-watch_num'
            m_videos = videos.order_by(order_key)

            return m_videos, msg
        else:
            m_videos = videos.order_by('-watch_num')

    except Exception, e:
        printError(e)

    return m_videos, msg



def add_like_num(video_id):
    try:
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            video.like_num += 1
            video.save()
    except Exception, e:
        printError("Error: add_watch_num.\nError: " + str(e))

def if_video_collected(user, video):
    try:
        if user == None:
            return False

        account = get_account_from_user(user)
        collect_videos = get_collect_from_account(account)
        if collect_videos == None:
            return False
        else:
            videos = collect_videos.videos.all()
            if getLen(videos) < 1:
                return False
            for v in videos:
                if v == video:
                    return True

    except Exception, e:
        printError("if_video_collected: " + e)

    return False

def add_collect_video(user, video_id):
    try:
        account = get_account_from_user(user)
        if account == None:
            return False

        collect_videos = get_collect_from_account(account)
        video = get_video_by_id(video_id)
        videos = collect_videos.videos.all()
        if getLen(videos) < 1:
            collect_videos.videos.add(video)
        else:
            is_exist = False
            for v in videos:
                if v == video:
                    is_exist = True
            if is_exist == False:
                collect_videos.videos.add(video)

        collect_videos.save()
        return True

    except Exception, e:
        printError("Error: add_watch_num.\nError: " + str(e))

    return False

def cancle_collect_video(user, video_id):
    try:
        account = get_account_from_user(user)
        if account == None:
            return False

        collect_videos = get_collect_from_account(account)
        video = get_video_by_id(video_id)
        videos = collect_videos.videos.all()

        if getLen(videos) < 1:
            return True
        else:
            t_videos = []
            for v in videos:
                if v != video:
                    t_videos.append(v)
            collect_videos.videos = t_videos

        collect_videos.save()
        return True

    except Exception, e:
        printError("Error: cancle_collect_video.\nError: " + str(e))

    return False


def add_comment(request):
    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])
        if request.GET.has_key('follow_id'):
            follow_id = int(request.GET['follow_id'])
        if request.GET.has_key('content'):
            content = request.GET['content'].encode('utf-8')
        # print video_id, follow_id, content

        comment = Comment()
        comment.user = Account.objects.filter(user=request.user).all()[0]
        comment.follow_id = follow_id
        comment.comment    = content

        comment.save()

        video = get_video_by_id(video_id)
        video.comments.add(comment)
        video.save()

    except Exception, e:
        printError(e)

def del_comment(request):
    try:
        if request.GET.has_key('comment_id'):
            comment_id = int(request.GET['comment_id'])

        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])

        comment = Comment.objects.all().filter(id=comment_id)
        if getLen(comment) > 0:
            comment = comment[0]
        else:
            return
        video   = Video.objects.all().filter(id=video_id)
        if getLen(video) > 0:
            video = video[0]
        else:
            return

        video.comments.remove(comment)
        comment.delete()

        print "delete comment: ", comment_id

    except Exception, e:
        printError(e)

def create_account_given_wx(request, wx_user):
    try:
        wx_unionid = wx_user['unionid']
        with transaction.atomic():
            user = User()
            user.username = wx_unionid
            user.set_password("Z!"+wx_unionid+"1!")
            user.save()

            account = Account()
            account.user = user
            account.wx_unionid = wx_unionid
            if checkMobile(request) == True:
                account.wx_wx_openid = wx_user['openid']
            else:
                account.wx_pc_openid = wx_user['openid']

            account.nickname = wx_user['nickname']

            account.user_pic = wx_user['headimgurl']
            sex = wx_user['sex']
            try:
                sex = int(sex)
                if sex != 0 and sex != 1:
                    sex = -1
            except Exception, e:
                sex = -1
                printError(e)
            account.sex = sex
            account.info = "这家伙很懒，什么都没留~"

            account.save()
            return True
    except Exception, e:
        printError(e)

    return False

def create_account_given_user(user):
    try:
        account = Account()
        account.user = user
        account.nickname = user.username
        account.user_pic = "/static/samples/boy/junyong02.jpg"

        account.info = "这家伙很懒，什么都没留~"

        account.save()
        return account
    except Exception, e:
        printError(e)

    return None


def check_wx_unionid(request, wx_user):
    try:
        wx_unionid = wx_user['unionid']
        account = Account.objects.filter(wx_unionid=wx_unionid).all()

        if getLen(account) < 1:
            create_account_given_wx(request, wx_user)
            return True
        else:
            account = account[0]
            if checkMobile(request) == True:
                if account.wx_wx_openid == None or account.wx_wx_openid == "":
                    print "wx_wx_openid is none."
                    account.wx_wx_openid = wx_user['openid']
                    account.save()
            else:
                if account.wx_pc_openid == None or account.wx_pc_openid == "":
                    print "wx_pc_openid is none."
                    account.wx_pc_openid = wx_user['openid']
                    account.save()
            return True

    except Exception, e:
        printError(e)

    return False

def exist_user_account(user):
    try:
        account = Account.objects.filter(user=user).all()

        if getLen(account) < 1:
            create_account_given_user(user)
            return True

    except Exception, e:
        printError("exist_user_account: " + str(e))

    return False


def get_account_from_user(user):
    account = None
    try:
        account = Account.objects.filter(user=user).all()
        if getLen(account) < 1:
            account = create_account_given_user(user)
        else:
            account = account[0]
    except Exception, e:
        printError("get_account_from_user: "+str(e))
    return account

def get_openid_from_user(request):
    open_id = ""
    try:
        account = get_account_from_user(request.user)
        if checkMobile(request) == True:
            open_id = account.wx_wx_openid
        else:
            open_id = account.wx_pc_openid

    except Exception, e:
        printError("get_openid_from_user: " + str(e))

    return open_id

def paydetail(request):
    """获取支付信息"""
    openid = get_openid_from_user(request)
    #openid = request.openid
    print "openid: ", openid
    try:
        jsApi = JsApi_pub()
        unifiedOrder = UnifiedOrder_pub()
        unifiedOrder.setParameter("openid",openid) #商品描述########################


        order = create_unpay_order_mobile(request.user, int(request.POST['video_id']) )
        money = int(order.price*100)

        unifiedOrder.setParameter("body", order.name.encode('utf-8')) #商品描述
        #out_trade_no = "{0}{1}".format(getRandomStr(), int(timeStamp*100))
        out_trade_no = order.order_num
        unifiedOrder.setParameter("out_trade_no", out_trade_no) #商户订单号
        unifiedOrder.setParameter("total_fee", str(money)) #总金额
        unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL) #通知地址
        unifiedOrder.setParameter("trade_type", "JSAPI") #交易类型
        unifiedOrder.setParameter("attach", "6666") #附件数据，可分辨不同商家(string(127))

        prepay_id = unifiedOrder.getPrepayId()
        jsApi.setPrepayId(prepay_id)
        jsApiParameters = jsApi.getParameters()

        jsApiParameters = eval(jsApiParameters)
        jsApiParameters['order_num'] = out_trade_no
    except Exception as e:
        printError("paydetail: " + str(e))
    else:
        jsApiParameters = str(jsApiParameters)
        print jsApiParameters, type(jsApiParameters)
        return HttpResponse(jsApiParameters)

def create_collect_given_account(account):
    if account == None:
        return None
    collect_videos = None
    try:
        collect_videos = CollectVideos()
        collect_videos.account = account
        collect_videos.save()
    except Exception, e:
        printError(e)

    return collect_videos

def get_collect_from_account(account):
    if account == None:
        return None
    collect_videos = None
    try:
        collect_videos = CollectVideos.objects.filter(account=account).all()
        if getLen(collect_videos) < 1:
            collect_videos = create_collect_given_account(account)
        else:
            collect_videos = collect_videos[0]

    except Exception, e:
        printError("get_collect_from_account: " + str(e))

    return collect_videos

def get_video_state(user, video):
    if user == None:
        return False
    try:
        account = get_account_from_user(user)
        if account == None:
            return False
        try:
            if video.is_customize == True:
                groups = video.group.all()
                if groups.count() > 0:
                    for group in groups:
                        if check_chaoshi(group.release_date, group.valid_day):
                            group.is_valid = False
                            group.save()
                        if group.is_valid and account in group.allow_accounts.all():
                            return True
                return False
        except Exception as e:
            print "get_video_state:", str(e)


        user_orders = Order.objects.filter(account=account).all()
        is_paid = False
        if user.is_superuser == True:
            is_paid = True
        elif getLen(user_orders) < 1:
            is_paid = False
        else:
            for o in user_orders:
                if o.video == video:
                    if o.pay_state == 2:
                        if check_chaoshi(o.release_date, o.order_valid_day) == True:
                            o.pay_state = 1
                            o.save()
                            return False
                        else:
                            return True
                    elif o.pay_state == 1:
                        if check_pay_by_order_num(o.order_num) == True and check_chaoshi(o.release_date, o.order_valid_day) == False:
                            o.pay_state = 2
                            o.save()
                            # add user order info
                            add_user_order_info(account, o, pc_flag=1)
                            return True
                        else:
                            if o.price == 0:
                                if check_chaoshi(o.release_date, o.order_valid_day) == True:
                                    if o.pay_state == 1:
                                        o.delete()
                                    return False
                                else:
                                    return True

    except Exception, e:
        printError("get_video_state: " + str(e))

    return is_paid

def check_chaoshi(release_date, threshold):
    try:
        if threshold == -1:
            return False
        year  = release_date.year
        month = release_date.month
        day   = release_date.day
        d1 = datetime.date(year, month, day)

        now = datetime.datetime.now()
        cur_year  = now.year
        cur_month = now.month
        cur_day   = now.day
        d2 = datetime.date(cur_year, cur_month, cur_day)

        if (d2-d1).days <= threshold:
            return False
    except Exception, e:
        print "Error, check_chaoshi, ", str(e)
        return False

    return True

def add_watch_history(user, video):
    if user == None:
        return False
    try:
        account = get_account_from_user(user)
        if account == None:
            return False

        watch_history = WatchHistory.objects.filter(account=account).all()
        if getLen(watch_history) < 1:
            watch_history = WatchHistory()
            watch_history.account = account
            watch_history.save()
        else:
            watch_history = watch_history[0]

        videos = watch_history.videos.all()
        if getLen(videos) < 1:
            watch_history.videos.add(video)
        else:
            is_exist = False
            for v in videos:
                if v == video:
                    is_exist = True
                    break
            if is_exist == False:
                print "add watch history."
                watch_history.videos.add(video)

        watch_history.save()
        return True

    except Exception, e:
        printError("add_watch_history: " + str(e))

    return False


def get_watch_history(user):

    if user == None:
        return None, 0
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        watch_history = WatchHistory.objects.filter(account=account).all()
        if getLen(watch_history) < 1:
            return None, 0
        else:
            watch_history = watch_history[0]

        videos = watch_history.videos.all()

        return videos, watch_history.videos_num

    except Exception, e:
        printError(e)

    return None, 0


def get_watch_history_num(user):
    try:
        account = get_account_from_user(user)
        watch_history = WatchHistory.objects.filter(account=account).all()[0]
        return watch_history.videos_num

    except Exception, e:
        printError(e)

    return 0

def del_watch_history(user, video_id):
    try:
        account = get_account_from_user(user)
        watch_history = WatchHistory.objects.filter(account=account).all()[0]
        temp_video = get_video_by_id(video_id)
        watch_history.videos.remove(temp_video)
        watch_history.save()
    except Exception, e:
        printError(e)

    return False

def get_collect(user):

    if user == None:
        return None, 0
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        collect_videos = CollectVideos.objects.filter(account=account).all()
        if getLen(collect_videos) < 1:
            return None, 0
        else:
            collect_videos = collect_videos[0]

        videos = collect_videos.videos.all()

        return videos, collect_videos.videos_num

    except Exception, e:
        printError(e)

    return None, 0

def get_collect_num(user):
    try:
        account = get_account_from_user(user)
        collect_videos = CollectVideos.objects.filter(account=account).all()
        if getLen(collect_videos) > 0:
            return collect_videos[0].videos_num

    except Exception, e:
        printError(e)

    return 0

def del_collect(user, video_id):
    try:
        account = get_account_from_user(user)
        collect_videos = CollectVideos.objects.filter(account=account).all()[0]
        temp_video = get_video_by_id(video_id)
        collect_videos.videos.remove(temp_video)
        collect_videos.save()
    except Exception, e:
        printError(e)

    return False


def get_unpay(user):
    if user == None:
        return None, 0
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        unpay_orders = Order.objects.filter(account=account).all().filter(pay_state=1).all()
        order_videos = []
        for o in unpay_orders:
            order_videos.append(o.video)

        return order_videos, getLen(unpay_orders)

    except Exception, e:
        printError("get_unpay: " + str(e))

    return None, 0

def get_order_given_ordernum(order_num):
    order = Order.objects.all().filter(order_num=order_num)
    if getLen(order) == 0:
        return None
    else:
        return order[0]

def get_order_given_orderid(order_id):
    order = Order.objects.all().filter(id=order_id)
    if getLen(order) == 0:
        return None
    else:
        return order[0]

def get_orderid_given_user_video(user, video):
    try:
        account = get_account_from_user(user)
        order = Order.objects.all().filter(account=account).all().filter(video=video).all()
        return order[0].id
    except Exception, e:
        print "get_orderid_given_user_video: ", str(e)

    return None

def unpay_check_video_alive(unpay_order):
    try:
        for order in unpay_order:
            if order.video == None:
                order.pay_state = -1
                order.save()
    except Exception, e:
        printError("unpay_check_video_alive: " + str(e))

def get_unpay_num(user):
    try:
        account = get_account_from_user(user)
        unpay_order = Order.objects.filter(account=account).all().filter(pay_state=1).all()
        unpay_check_video_alive(unpay_order)
        unpay_order = Order.objects.filter(account=account).all().filter(pay_state=1).all()
        return getLen(unpay_order)
    except Exception, e:
        printError( "get_unpay_num: " + str(e))

    return 0

def del_unpay(user, video_id):
    try:
        account = get_account_from_user(user)
        unpay_order = Order.objects.filter(account=account).all().filter(pay_state=1).all()
        for order in unpay_order:
            if video_id == order.video.id:
                unpay_order = order
                break
        #unpay_order.pay_state = -1
        #unpay_order.save()
        unpay_order.delete()

    except Exception, e:
        printError("del_unpay: " + str(e))

    return False

def get_groups(user):
    if user == None:
        return None, 0
    groups = None
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        groups = Group.objects.filter(is_valid=True).all()
        for i, group in enumerate(groups):
            if check_chaoshi(group.release_date, group.valid_day):
                group.is_valid = False
                group.save()

        groups = Group.objects.filter(is_valid=True).all()
        for i, group in enumerate(groups):
            if account in group.allow_accounts.all():
                groups[i].is_joined = True
            if ApplyGroup.objects.filter(account=account, status=0).all():
                groups[i].is_applied = True

    except Exception, e:
        printError("get_groups:"+ str(e))

    return groups, getLen(groups)

def get_customize(user):
    if user == None:
        return None, 0
    order_videos = None
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        order_videos = []

    except Exception, e:
        printError(e)

    try:
        customize_videos = Video.objects.filter(is_customize=True).all()
        if customize_videos:
            for v in customize_videos:
                if v not in order_videos:
                    if v.group.count() > 0:
                        if account in v.group.all()[0].allow_accounts.all():
                            order_videos.append(v)
                    else:
                        order_videos.append(v)
    except Exception as e:
        print "get_customize, customize:", str(e)

    return order_videos, getLen(order_videos)

def get_paid(user):
    if user == None:
        return None, 0
    order_videos = None
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        paid_orders = Order.objects.filter(account=account).all().filter(pay_state=2).all()
        order_videos = []
        for o in paid_orders:
            order_videos.append(o.video)

    except Exception, e:
        printError(e)

    # try:
        # customize_videos = Video.objects.filter(is_customize=True).all()
        # if customize_videos:
            # for v in customize_videos:
                # if v not in order_videos:
                    # if v.group.count() > 0:
                        # if account in v.group.all()[0].allow_accounts.all():
                            # order_videos.append(v)
                    # else:
                        # order_videos.append(v)
    # except Exception as e:
        # print "get_paid, customize:", str(e)

    return order_videos, getLen(order_videos)

def get_paid_num(user):
    try:
        videos, num = get_paid(user)
        return num
        # account = get_account_from_user(user)
        # paid_order = Order.objects.filter(account=account).filter(pay_state=2).all()
        # return getLen(paid_order)
    except Exception, e:
        printError(e)

    return 0


def update_account(request):
    try:
        account = get_account_from_user(request.user)
        account.nickname = request.GET['nickname'].encode("utf-8")
        account.info     = request.GET['info'].encode("utf-8")
        account.sex      = int(request.GET['sex'])

        account.save()
        return True
    except Exception, e:
        printError(e)

    return False

def create_unpay_order(user, video_id):
    try:
        created_flag = False
        unpay_order = Order()

        video   = get_video_by_id(video_id)
        account = get_account_from_user(user)
        timeStamp = time.time()
        out_trade_no = "{0}{1}".format(getRandomStr(6),int(timeStamp*100))
        time_format = '%Y-%m-%d %H:%M:%S'
        try:
            t_order = Order.objects.filter(account=account).all()

            if t_order != None:
                for o in t_order:
                    v = o.video
                    if v == video:
                        if o.pay_state == 1:
                            #current = datetime.datetime.now()
                            #current_str = current.strftime(time_format)
                            #order_time_str = o.release_date.strftime(time_format)

                            #current = datetime.datetime.strptime(current_str,time_format)
                            #order_time = datetime.datetime.strptime(order_time_str,time_format)

                            #time_space =  (current-order_time).seconds
                            #if time_space > 5000:
                            if True:
                                if check_pay_by_order_num(o.order_num) == True:
                                    o.pay_state = 2
                                    o.save()
                                    return o
                        elif o.pay_state == 2:
                            return o

                        created_flag = True
                        unpay_order = o
                        break

                        #elif o.pay_state == -1:
                        #    o.pay_state = 1
                            #o.order_num = out_trade_no
                        #    remove_file(o.wxpay_qrcode)
                        #    o.wxpay_qrcode = get_wxpay_qrcode(o)
                        #    o.save()
        except Exception, e:
            printError("create_unpay_order-1: " + str(e))

        #unpay_order = Order()
        unpay_order.order_num = out_trade_no
        unpay_order.account = account
        unpay_order.video = video
        unpay_order.name = video.title
        unpay_order.pic  = video.logo_img

        if created_flag == False:
            unpay_order.price = video.money
            unpay_order.order_valid_day = video.valid_day

        unpay_order.pay_state = 1

        unpay_order.wxpay_qrcode = get_wxpay_qrcode(unpay_order)#"/static/storage/wxpay_qrcode/150831170420-zrOL.png"

        with transaction.atomic():
            unpay_order.save()

            unpay_order.video = video
            unpay_order.save()

            if created_flag == False:
                add_user_order_info(account, unpay_order, pc_flag=True)

            return unpay_order

    except Exception, e:
        printError("create_unpay_order: " + str(e))

    return None

def create_unpay_order_mobile(user, video_id):
    try:
        created_flag = False
        unpay_order = Order()

        timeStamp = time.time()
        out_trade_no = "{0}{1}".format(getRandomStr(6),int(timeStamp*100))

        video   = get_video_by_id(video_id)
        account = get_account_from_user(user)
        try:
            t_order = Order.objects.filter(account=account).all()

            if t_order != None:
                for o in t_order:
                    v = o.video
                    if v == video:
                        if o.pay_state == 2:
                            return o
                        elif o.pay_state == 1:
                            if check_pay_by_order_num(o.order_num) == True:
                                o.pay_state = 2
                                o.save()
                                return o
                        created_flag = True
                        unpay_order = o
                        break

        except Exception, e:
            printError("create_unpay_order_mobile-1: " + str(e))


        #unpay_order = Order()
        unpay_order.order_num = out_trade_no
        unpay_order.account = account
        unpay_order.video = video
        unpay_order.name = video.title
        unpay_order.pic  = video.logo_img

        if created_flag == False:
            unpay_order.price = video.money
            unpay_order.order_valid_day = video.valid_day

        unpay_order.pay_state = 1

        #unpay_order.wxpay_qrcode = get_wxpay_qrcode(unpay_order)#"/static/storage/wxpay_qrcode/150831170420-zrOL.png"

        with transaction.atomic():
            unpay_order.save()

            unpay_order.video = video
            unpay_order.save()

            if created_flag == False:
                add_user_order_info(account, unpay_order, pc_flag=False)

            return unpay_order

    except Exception, e:
        printError("create_unpay_order_mobile: " + str(e))

    return None

def db_delete_video(request):
    try:
        video_id = int(request.GET['video_id'])
        video = get_video_by_id(video_id)
        video.delete()
        return True

    except Exception, e:
        printError(e)

    return False

def db_delete_intrestvideo(request):
    try:
        video_id = int(request.GET['video_id'])
        intrest_video = IntrestVideos.objects.filter(video=get_video_by_id(video_id))
        intrest_video.delete()
        return True

    except Exception, e:
        printError(e)

    return False

def db_add_intrestvideo(request):
    try:
        video_id = int(request.GET['video_id'])
        video = get_video_by_id(video_id)
        intrest_video = IntrestVideos()
        intrest_video.video = video
        intrest_video.save()
        return True

    except Exception, e:
        printError(e)

    return False


def add_user_watch_info(request, video):
    try:
        if request.user.is_superuser == True:
            return False
        user_watch = UserWatchInfo()
        user_watch.account = get_account_from_user(request.user)
        user_watch.video = video
        if checkMobile(request) == True:
            user_watch.pc_flag = False
        else:
            user_watch.pc_flag = True

        user_watch.save()
        return True
    except Exception, e:
        print "Error: add_user_watch_info: ", str(e)

    return False


def add_user_order_info(account, order, pc_flag):
    try:
        user_order = UserOrderInfo()
        user_order.account   = account
        user_order.order     = order
        user_order.price     = order.price
        user_order.pay_state = order.pay_state
        user_order.pc_flag   = pc_flag

        user_order.save()
    except Exception, e:
        print "Error: add_user_order_info: ", str(e)


def add_user_order_info_by_request(request, order_num):
    order = get_order_given_ordernum(order_num)
    if checkMobile(request) == True:
        pc_flag = False
    else:
        pc_flag = True
    account = get_account_from_user(request.user)
    add_user_order_info(account, order, pc_flag)

def pay_result(request):
    msg = init_msg(request)
    try:
        if request.GET.has_key('paid_order_id'):
            paid_order_id = request.GET['paid_order_id']
            paid_orders = Order.objects.filter(id=paid_order_id)
            paid_order = paid_orders[0]
            paid_order.pay_state = 2
            remove_file(paid_order.wxpay_qrcode)
            paid_order.save()

            # add user order info
            add_user_order_info_by_request(request, paid_order.order_num)

            msg['paid_order'] = paid_order
    except Exception, e:
        printError(e)
    ###应添加订单状态处理
    return render_to_response('pay/notice.html', msg)


def get_course_progress(user, video):
    try:
        account = get_account_from_user(user)
        course_progress = None
        try:
            course_progress = CourseProgress.objects.get(account=account, video=video)
        except Exception as e1:
            print "course progress query not match: ", str(e1)
        if not course_progress:
            course_progress = CourseProgress(account=account, video=video)
            course_progress.save()
        return course_progress

    except Exception as e:
        print "get_course_progress:", str(e)

    return None
