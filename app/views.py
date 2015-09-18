#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *


def test(request):
    print "TEST"
    msg = init_msg(request)

    return render_to_response('test.html', msg)


def index(request):
    #wx_knife_pay(request)
    try:
        wechat_user = WxAuth.get_user(request)

        if wechat_user != None:
            print "Wechat-User: ", wechat_user

            if check_wx_openid(wechat_user) == True:
                wx_login_do(request, wechat_user)
        else:
            print "Wechat-User: None."

    except Exception, e:
        printError(e)

    msg = init_msg(request)


    return render_to_response('index.html', msg)



def login_ui(request):
    msg = init_msg(request)

    return render_to_response('login/login.html', msg)

def wechat_login(request):
    #login_url = "https://open.weixin.qq.com/connect/qrconnect?appid=%s&redirect_uri=%s&response_type=%s&scope=%s&state=%s#wechat_redirect"%(APP_ID, REDIRECT_URL, RESPONSE_TYPE, SCOPE, STATE)
    login_url = WxAuth.get_authorize_url(request)

    return HttpResponseRedirect(login_url)

def wechat_share(request):
    url = "http://facebuaa.cn"
    if request.GET.has_key('cur_url'):
        url = request.GET['cur_url']

    qrcode_url = get_qrcode(url)
    print qrcode_url
    json={'qrcode_url': qrcode_url}

    return JsonResponse(json)

def excute_login(request, username, password):
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print "user pass."
    except Exception, e:
        printError(e)


def wx_login_do(request, user):
    username = user['openid']
    password = "Z!"+username+"1!"

    excute_login(request, username, password)

def login_do(request):
    msg = init_msg(request)

    username = request.POST['username']
    password = request.POST['password']
    

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "user pass."

            # judge whether db exist accout related to the user.
            exist_user_account(user)

            if msg.has_key('next'):
                return HttpResponseRedirect( HOMEPAGE+ msg['next'])
            else:
                return HttpResponseRedirect( HOMEPAGE)


    return render_to_response('login/login.html', msg)

def log_out(request):
    logout(request)

    return HttpResponseRedirect(HOMEPAGE)

def videos_ui(request):

    msg = init_msg(request)

    videos = Video.objects.all()
    videos, msg = get_order_videos(request, videos, msg)

    total_page = (getLen(videos)+PAGE_SIZE-1)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    
    get_content = "/videos/?"
    for key in request.GET:
        if key != "page":
            get_content += "%s=%s&"%(key, request.GET[key])
    msg['get_content'] = get_content

    msg['interest_videos'] = get_interest_videos()

    return render_to_response('videos/videos.html', msg)


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

    msg['videos']     = subVideos
    msg['videos_len'] = len(videos)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    msg['interest_videos'] = get_interest_videos()

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



def search_result(request):

    msg = init_msg(request)

    #videos, msg = get_order_videos(request, msg)
    videos = get_search_videos(request)

    total_page = (getLen(videos)+PAGE_SIZE-1)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1

    msg['interest_videos'] = get_interest_videos()

    return render_to_response('videos/search_result.html', msg)

@login_required(login_url='/login/')
@csrf_exempt
def play_ui(request):
    msg = init_msg(request)

    if request.GET.has_key('video-id'):
        try:
            video_id = int(request.GET['video-id'])
            video = Video.objects.filter(id=video_id).all()
            if video != None:
                video = video[0]
                msg['video'] = video
            else:
                 return render_to_response('videos/play-error.html', msg)

            key = video.key
            video_url = Qiniu.download_private_url(key)
            
            msg['video_url'] = video_url
            # add the watch number
            add_watch_num(video_id)

            try:
                # get the video's comments
                comments = Video.objects.filter(id=video_id)[0].comments.all().order_by('release_date')
                new_comments = []
                if getLen(comments) > 0:
                    for cc in comments:
                        cc.release_date = str(cc.release_date).split(' ')[0]
                        new_comments.append(cc)

                msg['comments'] = new_comments
                msg['comments_num'] = getLen(comments)
            except Exception, e:
                printError(e)


            # check whether need pay for the play
            is_paid = get_video_state(request.user, video)
            if (video.money <= 0) or (is_paid):
                add_watch_history(request.user, video)

                if if_video_collected(request.user, video):
                    msg['collect_state'] = '1'
                else:
                    msg['collect_state'] = '0'

                return render_to_response('videos/play.html', msg)
            else:
                return render_to_response('videos/play-prohibited.html', msg)

        except Exception, e:
            print "error: ", str(e)
    
    
    return render_to_response('videos/play-error.html', msg)


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

@login_required(login_url='/login/')
@csrf_exempt
# watching history list
def space_index(request):
    msg = get_space_msg(request, get_watch_history)
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    return render_to_response('space/history.html', msg)


@login_required(login_url='/login/')
@csrf_exempt
# watching history list
def space_collect(request):
    msg = get_space_msg(request, get_collect)
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    return render_to_response('space/collect.html', msg)

@login_required(login_url='/login/')
@csrf_exempt
# watching history list
def space_shopping_cart(request):
    msg = get_space_msg(request, get_unpay)
    
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    return render_to_response('space/unpay.html', msg)


@login_required(login_url='/login/')
@csrf_exempt
# watching history list
def space_paid(request):
    msg = get_space_msg(request, get_paid)
    
    if request.GET.has_key('show_del'):
        if request.GET['show_del'] == 'True':
            msg['show_del'] = 'True'

    return render_to_response('space/paid.html', msg)


def setprofile(request):
    msg = init_msg(request)

    return render_to_response('space/setprofile.html', msg)

@login_required(login_url='/login/')
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

    if request.GET.has_key('order_id'):
        try:
            order_id = int(request.GET['order_id'])
            del_unpay(request.user, order_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)

@login_required(login_url='/login/')
@csrf_protect
def upload_ui(request):
    data = init_msg(request)
    data['domain']       = DOMAIN
    data['uptoken_url']  = 'uptoken'
    return render_to_response('upload/upload.html', data)


@login_required(login_url='/login/')
@csrf_protect
def update_video_ui(request):
    msg = init_msg(request)

    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])
            video = get_video_by_id(video_id)

            msg['video'] = video

            return render_to_response('upload/update_video.html', msg)
    except Exception, e:
        printError(e)
   
    return render_to_response('videos/play-error.html', msg)


def voteup(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            add_like_num(video_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)

def collect(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            collect_state = request.GET['collect_state']
            if collect_state == '1':
                if cancle_collect_video(request.user, video_id) == True:
                    json['collect_state'] = '0'
                else:
                    json['collect_state'] = '1'
            elif collect_state == '0':
                if add_collect_video(request.user, video_id) == True:
                    json['collect_state'] = '1'
                else:
                    json['collect_state'] = '0'
        except Exception, e:
            printError(e)

    return JsonResponse(json)

@login_required(login_url='/login/')
@csrf_protect
def comment_add(request):
    json = {}
    try:
       add_comment(request)

    except Exception, e:
        printError(e)

    return JsonResponse(json)


@login_required(login_url='/login/')
@csrf_protect
def pay_ui(request):
    msg = init_msg(request)
    try:
        kwargs = {}
        account = get_account_from_user(request.user)
        if account != None:
            kwargs['account'] = account
            kwargs['id'] = request.GET['unpay_order_id']

            unpay_order = Order.objects.filter(**kwargs)
            msg ['unpay_order'] = unpay_order[0]

    except Exception, e:
        printError(e)
    
    return render_to_response('pay/pay.html', msg)


@login_required(login_url='/login/')
@csrf_protect
def ready_pay(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])
            unpay_order = create_unpay_order(request.user, video_id)

            if unpay_order != None:
                if unpay_order.pay_state == 1:
                    json['state'] = 'ok'
                    json['pay_url'] = HOMEPAGE + "/pay?unpay_order_id=" + str(unpay_order.id)
                elif unpay_order.pay_state == 2:
                    json['state'] = 'paid'

    except Exception, e:
        printError(e)

    return JsonResponse(json)


boy_imgs = []
with open('app/static/samples/boy.txt') as f:
    boy_imgs = f.readlines()
girl_imgs = []
with open('app/static/samples/girl.txt') as f:
    girl_imgs = f.readlines()

def get_random(imgs):
    try:
        if imgs == None:
            return None

        r_int = random.randint(0, len(imgs)-1)
        return imgs[r_int]

    except Exception, e:
        printError(e)

    return None


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
@csrf_protect
@csrf_exempt
def update_pic(request):
    try: 
        path = None
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
    

