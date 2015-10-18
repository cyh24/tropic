#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from qiniu_pro import *

from models import *
from config import *

from django.db import transaction
from wxpay import *
import datetime
from django.db.models import Q


def upload_course_post(request):
    msg = {'state': 'fail'}
    try:
        if request.method == "POST":
            for x in request.POST:
                print x, request.POST[x]
        

        if request.FILES.has_key('logo'):

            path = LOGO_FOLD + getRandomStr() + "-" + request.FILES['logo'].name
            handle_uploaded_photo(path, request.FILES['logo'])
            print "logo: ", path

            path_logo = path[3:]
            if save_video(request, path_logo) == True:
                msg['state'] = 'ok'

    except Exception, e:
        print "upload_course_post: ", str(e)
        #return HttpResponse("Fail.") 
    
    return render_to_response('info.html', msg)

def update_course_post(request):
    msg = {'state': 'fail'}
    try:
        if request.method == "POST":
            for x in request.POST:
                print x, request.POST[x]
        

        if request.FILES.has_key('logo'):
            if request.FILES['logo'] != None:
                path = LOGO_FOLD + getRandomStr() + "-" + request.FILES['logo'].name
                handle_uploaded_photo(path, request.FILES['logo'])
                print "logo: ", path

                path_logo = path[3:]
            
                if update_video(request, path_logo) == True:
                    msg['state'] = 'ok'
        else:
            if update_video(request) == True:
                msg['state'] = 'ok'

    except Exception, e:
        print "upload_course_post: ", str(e)
        #return HttpResponse("Fail.") 
    
    return render_to_response('info.html', msg)


def save_tag(tag_name):
    print "save tag: ", tag_name
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
    print "save kind; ", kind_name
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
        print "save_video"
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

        with transaction.atomic():
            qfiles = []
            if data.has_key('table_json'):
                qfiles = get_qiniu_files(data)

                if len(qfiles) == 0:
                    print "qiniu file: none."
                    return False

                video.save()
                for i in range(len(qfiles)):
                    qfiles[i].save()

                    video.files.add(qfiles[i])
            
            video.save()
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

        if video_key == "" or title == "":
            break

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

        with transaction.atomic():
            qfiles = []
            if data.has_key('table_json'):
                qfiles = get_qiniu_files(data)

                if getLen(qfiles) == 0:
                    print "qiniu file: none."
                    return False

                video.files.clear()
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


def get_search_videos(request):
    try:
        if request.GET.has_key('title'):
            q_title = request.GET['title'].encode('utf8')
            videos = Video.objects.filter(Q(title__icontains=q_title)|Q(kind_str__icontains=q_title)|Q(tags_str__icontains=q_title)).all()
            return videos
        else:
            return Video.objects.all()

    except Exception, e:
        printError(e)

    return None


def get_order_videos(request, videos, msg):
    try:
        if request.GET.has_key('order_by'):
            order_by = request.GET['order_by']
            msg['cur'] = order_by
            if order_by == "new":
                order_key = 'release_date'
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
                order_key = 'release_date'
            m_videos = videos.order_by(order_key)

            return m_videos, msg

    except Exception, e:
        printError(e)

    m_videos = videos.order_by('release_date')
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
    json = {}
    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])
        if request.GET.has_key('follow_id'):
            follow_id = int(request.GET['follow_id'])
        if request.GET.has_key('content'):
            content = request.GET['content'].encode('utf-8')
        print video_id, follow_id, content

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
        printError(e)

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
        printError(e)
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
    money = 1

    jsApi = JsApi_pub()
    unifiedOrder = UnifiedOrder_pub()
    unifiedOrder.setParameter("openid",openid) #商品描述########################


    order = create_unpay_order_mobile(request.user, int(request.POST['video_id']) )

    unifiedOrder.setParameter("body", order.name.encode('utf-8')) #商品描述
    #out_trade_no = "{0}{1}".format(getRandomStr(), int(timeStamp*100))
    out_trade_no = order.order_num
    unifiedOrder.setParameter("out_trade_no", out_trade_no) #商户订单号
    unifiedOrder.setParameter("total_fee", str(money)) #总金额
    unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL) #通知地址 
    unifiedOrder.setParameter("trade_type", "JSAPI") #交易类型
    unifiedOrder.setParameter("attach", "6666") #附件数据，可分辨不同商家(string(127))
    try:
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

        user_orders = Order.objects.filter(account=account).all()
        is_paid = False
        if getLen(user_orders) < 1:
            is_paid = False
        else:
            for o in user_orders:
                if o.video == video:
                    if o.pay_state == 2:
                        return True
                    elif o.pay_state == 1:
                        if check_pay_by_order_num(o.order_num) == True:
                            o.pay_state = 2
                            o.save()
                            return True

    except Exception, e:
        printError("get_video_state: " + str(e))

    return is_paid


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
        collect_videos = CollectVideos.objects.filter(account=account).all()[0]
        
        return collect_videos.videos_num

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

def get_paid(user):
    if user == None:
        return None, 0
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        paid_orders = Order.objects.filter(account=account).all().filter(pay_state=2).all()
        order_videos = []
        for o in paid_orders:
            order_videos.append(o.video)

        
        return order_videos, getLen(paid_orders)

    except Exception, e:
        printError(e)

    return None, 0

def get_paid_num(user):
    try:
        account = get_account_from_user(user)
        paid_order = Order.objects.filter(account=account).filter(pay_state=2).all()
        return getLen(paid_order)
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
        
        unpay_order.price = video.money

        unpay_order.pay_state = 1

        unpay_order.wxpay_qrcode = get_wxpay_qrcode(unpay_order)#"/static/storage/wxpay_qrcode/150831170420-zrOL.png"

        with transaction.atomic():
            unpay_order.save()
        
            unpay_order.video = video
            unpay_order.save()

            return unpay_order

    except Exception, e:
        printError("create_unpay_order: " + str(e))

    return None

def create_unpay_order_mobile(user, video_id):
    try:
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
                        unpay_order = o
                        break
                        
        except Exception, e:
            printError("create_unpay_order_mobile-1: " + str(e))
            

        print "no exist unpay_order_mobile"

        #unpay_order = Order()
        unpay_order.order_num = out_trade_no
        unpay_order.account = account
        unpay_order.video = video
        unpay_order.name = video.title
        unpay_order.pic  = video.logo_img
        
        unpay_order.price = video.money

        unpay_order.pay_state = 1

        #unpay_order.wxpay_qrcode = get_wxpay_qrcode(unpay_order)#"/static/storage/wxpay_qrcode/150831170420-zrOL.png"

        with transaction.atomic():
            unpay_order.save()
        
            unpay_order.video = video
            unpay_order.save()

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
